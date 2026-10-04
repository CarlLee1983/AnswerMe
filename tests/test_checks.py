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
