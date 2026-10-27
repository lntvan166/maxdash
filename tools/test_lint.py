import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import lint  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HERE, "fixtures", "lint")
PATTERNS = os.path.join(FIX, "leaks.txt")


def rules(findings):
    return [(os.path.basename(f.path), f.line, f.rule) for f in findings]


class LintTests(unittest.TestCase):
    def run_on(self, name):
        return lint.check([os.path.join(FIX, "bad", name)], leak_files=[PATTERNS])

    def test_leak_strings(self):
        got = rules(self.run_on("leaks.md"))
        self.assertEqual(
            got,
            [
                ("leaks.md", 3, "leak"),  # private.example.invalid
                ("leaks.md", 4, "leak"),  # 9999000011 serial
                ("leaks.md", 5, "leak"),  # Messages.swift:75
                ("leaks.md", 6, "leak"),  # cloudflared
            ],
        )

    def test_leak_in_html_and_json(self):
        self.assertEqual(rules(self.run_on("leak.html")), [("leak.html", 2, "leak")])
        self.assertEqual(rules(self.run_on("leak.json")), [("leak.json", 1, "leak")])

    def test_label_rule(self):
        self.assertEqual(rules(self.run_on("labels.md")), [("labels.md", 6, "label")])

    def test_escaped_pipe_in_cell(self):
        found = lint.check([os.path.join(FIX, "clean", "escaped.md")], leak_files=[PATTERNS])
        self.assertEqual(rules(found), [])

    def test_skip_rules_apply_to_subfolders(self):
        found = lint.check([os.path.join(HERE)], leak_files=[PATTERNS])
        self.assertEqual(rules(found), [])

    def test_skill_refs(self):
        found = lint.check([os.path.join(FIX, "bad", "skill", "AGENTS.md")], leak_files=[PATTERNS])
        self.assertEqual(rules(found), [("AGENTS.md", 3, "ref")])

    def test_relative_links(self):
        self.assertEqual(rules(self.run_on("links.md")), [("links.md", 1, "link")])

    def test_clean_repo_passes(self):
        r = subprocess.run(
            [sys.executable, os.path.join(HERE, "lint.py"), "--leaks", PATTERNS]
            + [os.path.join(FIX, "clean", f) for f in sorted(os.listdir(os.path.join(FIX, "clean")))],
            capture_output=True, text=True,
        )
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
