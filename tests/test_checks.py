"""Exercise the guard against bad metadata and partial staging in isolated repositories."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1]


class CheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="answer-me guard ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env = os.environ.copy()
        for key in ["GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR"]:
            self.env.pop(key, None)
        self.env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", ANSWERME_PYTHON=sys.executable)
        for name in ["scripts/check.py", "scripts/install-hooks.sh", ".githooks/pre-commit"]:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SOURCE / name, target)
        self.write("skills/demo/SKILL.md", '---\nname: demo\ndescription: Explain an example.\n---\n# Demo\n')
        self.write("skills/demo/agents/openai.yaml", 'interface:\n  display_name: Demo\n  short_description: Explain an example\n')
        self.write("README.md", "[Details](docs/details.md)\n")
        self.write("docs/details.md", "# Details\n")
        self.git("init", "-q")

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def run_command(self, *command, env=None):
        return subprocess.run(command, cwd=self.root, env=env or self.env, text=True, capture_output=True)

    def git(self, *args):
        result = self.run_command("git", *args)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def check(self, *args, valid=True, env=None):
        result = self.run_command(sys.executable, "scripts/check.py", *args, env=env)
        if valid:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def test_valid_checkout_and_missing_link(self):
        self.check()
        self.write("README.md", "[Details](docs/absent.md)\n")
        self.assertIn("missing relative link", self.check(valid=False).stderr)

    def test_invalid_frontmatter(self):
        self.write("skills/demo/SKILL.md", "---\nname: Bad_Name\ndescription: Example\n---\n")
        self.assertIn("hyphen-case", self.check(valid=False).stderr)

    def test_invalid_display_yaml(self):
        self.write("skills/demo/agents/openai.yaml", "interface: [\n")
        self.assertIn("openai.yaml", self.check(valid=False).stderr)

    def test_missing_validator_fails_explicitly(self):
        env = dict(self.env, SKILL_VALIDATOR=str(self.root / "absent.py"))
        self.assertIn("Skill validator missing", self.check(valid=False, env=env).stderr)

    def test_bad_index_is_not_hidden_by_worktree_fix(self):
        self.write("README.md", "[Broken](absent.md)\n")
        self.git("add", ".")
        self.write("README.md", "# Fixed only in working tree\n")
        self.check()
        self.assertIn("missing relative link", self.check("--staged", valid=False).stderr)

    def test_good_index_ignores_bad_unstaged_and_untracked_files(self):
        self.git("add", ".")
        self.write("README.md", "[Broken](absent.md)\n")
        self.write("docs/untracked.md", "[Broken](absent.md)\n")
        self.check(valid=False)
        self.check("--staged")

    def test_untracked_target_cannot_satisfy_staged_link(self):
        self.write("README.md", "[New](docs/new.md)\n")
        self.git("add", ".")
        self.write("docs/new.md", "# Only in working tree\n")
        self.check()
        self.check("--staged", valid=False)
        self.git("add", "docs/new.md")
        self.check("--staged")

    def write_site(self):
        self.write("site/index.html", '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
                   '<link href="https://fonts.googleapis.com/css2?family=Lora" rel="stylesheet">\n'
                   '<a href="examples/one.html">One</a>\n')
        self.write("site/examples/one.html", '<a href="../index.html#top">Home</a>\n'
                   '<a href="https://github.com/carl/AnswerMe">Repo</a>\n')

    def test_valid_site_passes(self):
        self.write_site()
        self.check()

    def test_site_local_path_fails(self):
        self.write_site()
        self.write("site/examples/one.html", "file:///Users/x/a.md\n")
        self.assertIn("local path", self.check(valid=False).stderr)
        self.write("site/examples/one.html", "see /home/x/a.md\n")
        self.assertIn("site/examples/one.html:1: local path", self.check(valid=False).stderr)

    def test_site_missing_relative_link_fails(self):
        self.write_site()
        self.write("site/examples/one.html", '<p>x</p>\n<a href="missing.html?a=1#b">Gone</a>\n')
        self.assertIn("site/examples/one.html:2: missing relative link missing.html", self.check(valid=False).stderr)

    def test_site_example_external_resource_fails_but_link_passes(self):
        self.write_site()
        self.write("site/examples/one.html", '<script src="https://cdn.example.com/x.js"></script>\n')
        self.assertIn("site/examples/one.html:1: loads external resource https://cdn.example.com/x.js", self.check(valid=False).stderr)
        self.write("site/examples/one.html", '<a href="https://cdn.example.com/x.js">x</a>\n')
        self.check()

    def test_site_example_style_external_url_fails(self):
        self.write_site()
        self.write("site/examples/one.html", '<style>\n@import "https://x.example/a.css";\nbody { background: url(https://x.example/a.png) }\n</style>\n')
        self.assertIn("site/examples/one.html:3: loads external resource", self.check(valid=False).stderr)
        self.write("site/examples/one.html", '<p style="background:url(\'//x.example/a.png\')">x</p>\n')
        self.assertIn("site/examples/one.html:1: loads external resource", self.check(valid=False).stderr)
        self.write("site/examples/one.html", '<style>@import url(https://x.example/a.css);</style>\n')
        self.assertIn("loads external resource", self.check(valid=False).stderr)
        self.write("site/examples/one.html", '<style>body { background: url(a.png) }</style>\n')
        self.write("site/examples/a.png", "x")
        self.check()

    def test_site_landing_allows_only_google_fonts(self):
        self.write_site()
        self.check()
        self.write("site/index.html", '<link href="https://fonts.gstatic.com/s/x.woff2" rel="stylesheet">\n'
                   '<style>@import url(https://fonts.googleapis.com/css2?family=Lora);</style>\n'
                   '<script src="https://cdn.example.com/x.js"></script>\n')
        result = self.check(valid=False)
        self.assertIn("site/index.html:3: loads external resource https://cdn.example.com/x.js", result.stderr)
        self.assertEqual(result.stderr.count("loads external resource"), 1)
        self.write("site/index.html", '<style>body { background: url(//cdn.example.com/a.png) }</style>\n')
        self.assertIn("site/index.html:1: loads external resource", self.check(valid=False).stderr)

    def test_site_bad_index_is_not_hidden_by_worktree_fix(self):
        self.write_site()
        self.write("site/examples/one.html", '<script src="https://cdn.example.com/x.js"></script> /Users/x\n')
        self.git("add", ".")
        self.write_site()
        self.check()
        result = self.check("--staged", valid=False)
        self.assertIn("loads external resource", result.stderr)
        self.assertIn("local path", result.stderr)

    def test_untracked_target_cannot_satisfy_staged_site_link(self):
        self.write_site()
        self.write("site/examples/one.html", '<a href="two.html">Two</a>\n')
        self.git("add", ".")
        self.write("site/examples/two.html", "<p>Only in working tree</p>\n")
        self.check()
        self.assertIn("missing relative link two.html", self.check("--staged", valid=False).stderr)
        self.git("add", "site/examples/two.html")
        self.check("--staged")

    def test_site_link_leaving_site_fails(self):
        self.write_site()
        self.write("site/index.html", '<a href="../README.md">Readme</a>\n')
        self.assertIn("site/index.html:1: link leaves site ../README.md", self.check(valid=False).stderr)

    def test_site_directory_link_needs_index(self):
        self.write_site()
        self.write("site/examples/sub/a.html", "<p>a</p>\n")
        self.write("site/index.html", '<a href="examples/sub/">Sub</a>\n')
        self.assertIn("site/index.html:1: missing relative link examples/sub/", self.check(valid=False).stderr)
        self.write("site/examples/sub/index.html", "<p>sub</p>\n")
        self.check()

    def test_site_root_absolute_link_fails(self):
        self.write_site()
        self.write("site/examples/one.html", '<a href="/index.html">Home</a>\n')
        self.assertIn("site/examples/one.html:1: root-absolute link /index.html", self.check(valid=False).stderr)

    def test_site_local_path_ignores_url_segments(self):
        self.write_site()
        self.write("site/examples/one.html", '<a href="https://example.com/home/page">a</a>\n<a href="https://github.com/Users/x">b</a>\n')
        self.check()
        self.write("site/examples/one.html", '<p>"/Users/carl/x"</p>\n')
        self.assertIn("local path", self.check(valid=False).stderr)
        self.write("site/examples/one.html", '<a href="file:///Users/carl/x">a</a>\n')
        self.assertIn("local path", self.check(valid=False).stderr)

    def test_site_mentioning_file_scheme_without_path_passes(self):
        self.write_site()
        self.write("site/examples/one.html", '<p>開 <code>file://</code> 網址，或用 file:// 協定。</p>\n')
        self.check()
        self.write("site/examples/one.html", '<a href="file://localhost/etc/x">a</a>\n')
        self.assertIn("local path", self.check(valid=False).stderr)

    def test_site_landing_fonts_only_on_link_tags(self):
        self.write_site()
        self.write("site/index.html", '<script src="https://fonts.googleapis.com/x.js"></script>\n')
        self.assertIn("site/index.html:1: loads external resource", self.check(valid=False).stderr)

    def test_site_example_srcset_and_poster_fail(self):
        self.write_site()
        self.write("site/examples/a.png", "x")
        self.write("site/examples/one.html", '<img srcset="a.png 1x, https://x.example/b.png 2x">\n')
        self.assertIn("site/examples/one.html:1: loads external resource https://x.example/b.png", self.check(valid=False).stderr)
        self.write("site/examples/one.html", '<video poster="//x.example/p.png"></video>\n')
        self.assertIn("site/examples/one.html:1: loads external resource //x.example/p.png", self.check(valid=False).stderr)
        self.write("site/examples/one.html", '<picture><source srcset="https://x.example/c.webp"></picture>\n')
        self.assertIn("site/examples/one.html:1: loads external resource https://x.example/c.webp", self.check(valid=False).stderr)
        self.write("site/examples/one.html", '<img srcset="a.png 1x, a.png 2x">\n')
        self.check()

    def test_site_style_url_split_across_lines_fails(self):
        self.write_site()
        self.write("site/examples/one.html", '<style>\nbody {\n  background: url(\n    https://x.example/a.png\n  )\n}\n</style>\n')
        self.assertIn("site/examples/one.html:3: loads external resource https://x.example/a.png", self.check(valid=False).stderr)

    def test_tree_without_site_passes(self):
        self.assertFalse((self.root / "site").exists())
        self.check()

    def test_hook_install_and_execution(self):
        result = self.run_command("sh", "scripts/install-hooks.sh")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git("config", "--local", "--get", "core.hooksPath").stdout.strip(), ".githooks")
        self.assertEqual(self.run_command("sh", "scripts/install-hooks.sh").returncode, 0)
        self.git("add", ".")
        self.assertEqual(self.run_command(".githooks/pre-commit").returncode, 0)
        self.write("README.md", "[Broken](absent.md)\n")
        self.git("add", "README.md")
        self.assertNotEqual(self.run_command(".githooks/pre-commit").returncode, 0)

    def test_installer_preserves_existing_hook_configuration(self):
        self.git("config", "--local", "core.hooksPath", "existing-hooks")
        result = self.run_command("sh", "scripts/install-hooks.sh")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.git("config", "--local", "--get", "core.hooksPath").stdout.strip(), "existing-hooks")

    def test_installer_preserves_active_default_hook(self):
        self.write(".git/hooks/post-commit", "#!/bin/sh\nexit 0\n")
        hook = self.root / ".git/hooks/post-commit"
        hook.chmod(0o755)
        result = self.run_command("sh", "scripts/install-hooks.sh")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Existing executable hook preserved", result.stderr)
        self.assertEqual(hook.read_text(), "#!/bin/sh\nexit 0\n")


if __name__ == "__main__":
    unittest.main()
