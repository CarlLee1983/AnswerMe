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
    NOTES = "Release\n\n文件與網站：README 與介紹頁已審視，無需更新\n"

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="answer-me guard ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env = os.environ.copy()
        for key in ["GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR"]:
            self.env.pop(key, None)
        self.env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", ANSWERME_PYTHON=sys.executable)
        self.env.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.com", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.com")
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

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-q", "-m", "commit")

    def write_example(self, version):
        self.write("site/index.html", '<a href="examples/one.html">One</a>\n')
        self.write("site/examples/one.html", f"<p>範例：由 answer-me {version} 產生 · 2026-10-05</p>\n")

    def release_repo(self, example_version="v0.1.0", notes=None):
        """提交含範例頁的 commit，並建立舊版 tag v0.1.0 與待發布的 annotated tag v0.2.0。"""
        self.write_example(example_version)
        self.commit()
        self.git("tag", "-a", "v0.1.0", "-m", "old")
        self.git("tag", "-a", "v0.2.0", "-m", self.NOTES if notes is None else notes)

    def test_release_valid_tag_passes_and_older_example_version_is_allowed(self):
        self.release_repo()
        self.assertIn("PASS", self.check("--release", "v0.2.0").stdout)

    def test_release_missing_tag_fails(self):
        self.release_repo()
        self.assertIn("v9.9.9", self.check("--release", "v9.9.9", valid=False).stderr)

    def test_release_lightweight_tag_fails(self):
        self.release_repo()
        self.git("tag", "v0.3.0")
        self.assertIn("annotated", self.check("--release", "v0.3.0", valid=False).stderr)

    def test_release_notes_need_docs_and_site_line(self):
        self.release_repo(notes="Release\n\n只有說明\n")
        self.assertIn("文件與網站", self.check("--release", "v0.2.0", valid=False).stderr)
        self.git("tag", "-a", "-f", "v0.2.0", "-m", "Release\n\n文件與網站：   \n")
        self.assertIn("文件與網站", self.check("--release", "v0.2.0", valid=False).stderr)
        self.git("tag", "-a", "-f", "v0.2.0", "-m", "Release\n\n文件與網站：已審視\n")
        self.check("--release", "v0.2.0")

    def test_release_example_version_must_be_existing_tag(self):
        self.release_repo(example_version="v0.9.0")
        self.assertIn("v0.9.0", self.check("--release", "v0.2.0", valid=False).stderr)

    def test_release_reads_tag_commit_not_worktree(self):
        self.release_repo(example_version="v0.9.0")
        self.write_example("v0.1.0")
        self.assertIn("v0.9.0", self.check("--release", "v0.2.0", valid=False).stderr)
        self.write_example("v0.1.0")
        self.commit()
        self.git("tag", "-a", "v0.3.0", "-m", self.NOTES)
        self.write_example("v0.9.0")
        self.write("README.md", "[Broken](absent.md)\n")
        self.check("--release", "v0.3.0")

    def test_release_tag_commit_with_broken_quick_check_fails(self):
        self.write("README.md", "[Broken](absent.md)\n")
        self.release_repo()
        self.write("README.md", "[Details](docs/details.md)\n")
        self.assertIn("missing relative link", self.check("--release", "v0.2.0", valid=False).stderr)

    def test_release_blank_notes_line_is_not_satisfied_by_next_line(self):
        self.release_repo(notes="Release\n\n文件與網站：\n下一行有文字\n")
        self.assertIn("文件與網站", self.check("--release", "v0.2.0", valid=False).stderr)
        self.git("tag", "-a", "-f", "v0.2.0", "-m", "Release\n\n文件與網站：　 \n下一行有文字\n")
        self.assertIn("文件與網站", self.check("--release", "v0.2.0", valid=False).stderr)

    def test_release_invalid_tag_name_fails_with_single_error(self):
        self.release_repo()
        result = self.check("--release", "bad..name", valid=False)
        self.assertEqual(len(result.stderr.strip().splitlines()), 1)
        self.assertIn("bad..name", result.stderr)

    def test_release_and_staged_are_mutually_exclusive(self):
        self.release_repo()
        self.check("--release", "v0.2.0", "--staged", valid=False)

    def test_release_checks_example_pages_in_subdirectories(self):
        self.release_repo()
        self.write("site/examples/deep/two.html", "<p>範例：由 answer-me v0.9.0 產生</p>\n")
        self.commit()
        self.git("tag", "-a", "v0.3.0", "-m", self.NOTES)
        result = self.check("--release", "v0.3.0", valid=False)
        self.assertIn("site/examples/deep/two.html", result.stderr)

    def test_release_reports_all_errors_together(self):
        self.write("README.md", "[Broken](absent.md)\n")
        self.release_repo(example_version="v0.9.0", notes="沒有審視紀錄\n")
        stderr = self.check("--release", "v0.2.0", valid=False).stderr
        for expected in ["文件與網站", "v0.9.0", "missing relative link"]:
            self.assertIn(expected, stderr)

    REMINDER = "提醒"

    def reminder_repo(self):
        """已有 HEAD、技能資料夾與兩份使用者文件的 repo，之後的變更都相對於這個基線。"""
        self.write("skills/answer-me/notes.md", "# Notes\n")
        self.write("site/index.html", "<p>intro</p>\n")
        self.commit()

    def test_staged_reminder_when_only_technique_folder_changes(self):
        self.reminder_repo()
        self.write("skills/answer-me/notes.md", "# Notes\nmore\n")
        self.git("add", "skills")
        result = self.check("--staged")
        self.assertIn(self.REMINDER, result.stderr)
        self.assertIn("README", result.stderr)
        self.assertEqual(result.returncode, 0)

    def test_staged_no_reminder_when_readme_also_staged(self):
        self.reminder_repo()
        self.write("skills/answer-me/notes.md", "# Notes\nmore\n")
        self.write("README.md", "[Details](docs/details.md)\nupdated\n")
        self.git("add", ".")
        self.assertNotIn(self.REMINDER, self.check("--staged").stderr)

    def test_staged_no_reminder_when_landing_page_also_staged(self):
        self.reminder_repo()
        self.write("skills/answer-me/notes.md", "# Notes\nmore\n")
        self.write("site/index.html", "<p>updated</p>\n")
        self.git("add", ".")
        self.assertNotIn(self.REMINDER, self.check("--staged").stderr)

    def test_staged_no_reminder_when_only_docs_change(self):
        self.reminder_repo()
        self.write("README.md", "[Details](docs/details.md)\nupdated\n")
        self.git("add", ".")
        self.assertNotIn(self.REMINDER, self.check("--staged").stderr)

    def test_staged_no_reminder_for_unstaged_technique_change(self):
        self.reminder_repo()
        self.write("skills/answer-me/notes.md", "# Notes\nmore\n")
        self.assertNotIn(self.REMINDER, self.check("--staged").stderr)

    def test_staged_reminder_ignores_unstaged_readme_change(self):
        self.reminder_repo()
        self.write("skills/answer-me/notes.md", "# Notes\nmore\n")
        self.git("add", "skills")
        self.write("README.md", "[Details](docs/details.md)\nupdated\n")
        self.assertIn(self.REMINDER, self.check("--staged").stderr)

    def test_staged_reminder_in_initial_commit_without_docs(self):
        self.write("skills/answer-me/notes.md", "# Notes\n")
        self.git("add", "skills")
        self.assertIn(self.REMINDER, self.check("--staged").stderr)

    def test_staged_no_reminder_in_initial_commit_with_docs(self):
        self.write("skills/answer-me/notes.md", "# Notes\n")
        self.git("add", ".")
        self.assertNotIn(self.REMINDER, self.check("--staged").stderr)

    def test_staged_reminder_for_deletion_in_technique_folder(self):
        self.reminder_repo()
        self.git("rm", "-q", "skills/answer-me/notes.md")
        self.assertIn(self.REMINDER, self.check("--staged").stderr)

    def test_staged_reminder_does_not_block_failing_check(self):
        self.reminder_repo()
        self.write("skills/answer-me/notes.md", "[Broken](absent.md)\n")
        self.git("add", "skills")
        stderr = self.check("--staged", valid=False).stderr
        self.assertIn("missing relative link", stderr)
        self.assertIn(self.REMINDER, stderr)

    def test_reminder_not_printed_outside_staged_mode(self):
        self.reminder_repo()
        self.write("skills/answer-me/notes.md", "# Notes\nmore\n")
        self.git("add", "skills")
        self.assertNotIn(self.REMINDER, self.check().stderr)

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
