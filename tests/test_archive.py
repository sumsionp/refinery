import unittest
import os
import shutil
import tarfile
import zipfile
from src.archive_utils import unpack_archive

class TestArchiveUtils(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests/temp_extract"
        os.makedirs(self.test_dir, exist_ok=True)
        self.sample_file = "tests/sample.txt"
        with open(self.sample_file, "w") as f:
            f.write("test content")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        if os.path.exists(self.sample_file):
            os.remove(self.sample_file)
        if os.path.exists("tests/test.tar.gz"):
            os.remove("tests/test.tar.gz")
        if os.path.exists("tests/test.zip"):
            os.remove("tests/test.zip")

    def test_unpack_tar_gz(self):
        archive = "tests/test.tar.gz"
        with tarfile.open(archive, "w:gz") as tar:
            tar.add(self.sample_file, arcname="sample.txt")

        success = unpack_archive(archive, self.test_dir)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "sample.txt")))

    def test_unpack_zip(self):
        archive = "tests/test.zip"
        with zipfile.ZipFile(archive, "w") as zip_f:
            zip_f.write(self.sample_file, arcname="sample.txt")

        success = unpack_archive(archive, self.test_dir)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "sample.txt")))

if __name__ == '__main__':
    unittest.main()
