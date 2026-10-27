import glob
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    import yaml
except ImportError:  # CI installs pyyaml; locally: pip install pyyaml
    yaml = None


@unittest.skipIf(yaml is None, "pyyaml not installed")
class RepoFilesTests(unittest.TestCase):
    def test_github_yaml_parses(self):
        files = glob.glob(os.path.join(ROOT, ".github", "**", "*.yml"), recursive=True)
        self.assertTrue(files)
        for f in files:
            with self.subTest(f=os.path.relpath(f, ROOT)):
                with open(f, encoding="utf-8") as fh:
                    self.assertIsNotNone(yaml.safe_load(fh))


if __name__ == "__main__":
    unittest.main()
