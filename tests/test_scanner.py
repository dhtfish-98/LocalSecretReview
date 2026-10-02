from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

from local_secret_review import scan_path
from local_secret_review.cli import main


class ScannerTests(unittest.TestCase):
    def test_redacted_reports_and_stable_location(self):
        synthetic = "ghp_" + "A" * 24
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "app.js").write_text("const token = '" + synthetic + "';\n", encoding="utf-8")
            result = scan_path(root)
            self.assertEqual(result.scanned_files, 1)
            self.assertEqual(len(result.findings), 2)
            self.assertEqual({f.path for f in result.findings}, {"app.js"})
            self.assertEqual({f.line for f in result.findings}, {1})
            self.assertNotIn(synthetic, repr(result))
            for options in ([], ["--json"]):
                output = StringIO()
                with redirect_stdout(output):
                    self.assertEqual(main([str(root), *options]), 1)
                self.assertNotIn(synthetic, output.getvalue())
                if options:
                    self.assertEqual(len(json.loads(output.getvalue())["findings"]), 2)

    def test_skips_generated_dirs_symlinks_and_large_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "safe.js").write_text("const safe = true;\n", encoding="utf-8")
            (root / "large.js").write_text("x" * 40, encoding="utf-8")
            vendor = root / "node_modules"
            vendor.mkdir()
            (vendor / "ignored.js").write_text("password = 'verylongvalue123'", encoding="utf-8")
            (root / "link.js").symlink_to(vendor / "ignored.js")
            result = scan_path(root, max_bytes=32)
            self.assertEqual((result.scanned_files, result.skipped_files), (1, 1))
            self.assertEqual(result.findings, ())

    def test_env_and_binary_handling(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".env").write_text("PASSWORD=abcdefghijklmn\n", encoding="utf-8")
            (root / "binary.js").write_bytes(b"\x00PASSWORD=abcdefghijklmn")
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            (workflows / "check.yml").write_text("steps: []\n", encoding="utf-8")
            result = scan_path(root)
            self.assertEqual((result.scanned_files, result.skipped_files), (2, 1))
            self.assertEqual([f.path for f in result.findings], [".env"])

    def test_rejects_symlink_root_and_invalid_limit(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "code.js").write_text("ok", encoding="utf-8")
            link = root / "linked.js"
            link.symlink_to(root / "code.js")
            with self.assertRaises(ValueError):
                scan_path(link)
            with self.assertRaises(ValueError):
                scan_path(root, max_bytes=0)
            with self.assertRaises(ValueError):
                scan_path(root, max_bytes=16 * 1_048_576 + 1)


if __name__ == "__main__":
    unittest.main()
