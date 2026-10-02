from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from local_secret_review import scan_path
from local_secret_review.cli import main


class RegressionTests(unittest.TestCase):
    def test_json_key_and_new_header_shapes_are_redacted(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/"owned.json").write_text('{"password": "syntheticvalue12345"}')
            (root/"owned.py").write_text('-----BEGIN ENCRYPTED PRIVATE KEY-----\n'+'github_pat_'+'A'*24)
            findings=scan_path(root).findings
            self.assertEqual({item.rule for item in findings},{"literal-credential-assignment","private-key-header","github-token-shape"})
            self.assertNotIn("syntheticvalue12345",repr(findings))
    def test_skipped_input_and_walk_error_are_incomplete(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/"large.js").write_text("x"*40)
            with redirect_stdout(StringIO()):
                self.assertEqual(main([str(root),"--max-bytes","8"]),2)
            with patch("local_secret_review.scanner.os.walk",side_effect=OSError("synthetic error")),redirect_stderr(StringIO()),self.assertRaises(SystemExit) as caught:
                main([str(root)])
            self.assertEqual(caught.exception.code,2)
