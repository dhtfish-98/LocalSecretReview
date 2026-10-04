import errno
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock
from local_secret_review.local_input import read_local_file


class InputTests(unittest.TestCase):
    def test_descriptor_closed_when_stream_creation_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "input"
            path.write_bytes(b"local fixture")
            descriptors = []

            def fail_stream(descriptor, mode):
                descriptors.append(descriptor)
                raise OSError("simulated stream creation failure")

            with mock.patch("local_secret_review.local_input.os.fdopen", side_effect=fail_stream):
                with self.assertRaisesRegex(OSError, "simulated stream creation failure"):
                    read_local_file(path)

            self.assertEqual(len(descriptors), 1)
            try:
                with self.assertRaises(OSError) as error:
                    os.fstat(descriptors[0])
                self.assertEqual(error.exception.errno, errno.EBADF)
            finally:
                try:
                    os.close(descriptors[0])
                except OSError:
                    pass

    def test_stream_failure_keeps_original_error_if_descriptor_was_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "input"
            path.write_bytes(b"local fixture")
            descriptors = []

            def fail_after_close(descriptor, mode):
                descriptors.append(descriptor)
                os.close(descriptor)
                raise OSError("stream failed after consuming descriptor")

            with mock.patch("local_secret_review.local_input.os.fdopen", side_effect=fail_after_close):
                with self.assertRaisesRegex(OSError, "stream failed after consuming descriptor"):
                    read_local_file(path)

            self.assertEqual(len(descriptors), 1)
            with self.assertRaises(OSError) as error:
                os.fstat(descriptors[0])
            self.assertEqual(error.exception.errno, errno.EBADF)

    def test_oversized_link_and_nonregular_inputs(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            path=root/"input"
            path.write_bytes(b"x"*9)
            with self.assertRaises(ValueError): read_local_file(path,8)
            link=root/"link"
            link.symlink_to(path)
            with self.assertRaises(ValueError): read_local_file(link)
            with self.assertRaises((ValueError,OSError)): read_local_file(root)
            if hasattr(os,"mkfifo"):
                pipe=root/"pipe"
                os.mkfifo(pipe)
                with self.assertRaises(ValueError): read_local_file(pipe)
