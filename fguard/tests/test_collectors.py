"""tests for the analyzer classes"""
import unittest
import os
from fguard.colllectors import FlatCollector


class TestFlatCollector(unittest.TestCase):
    """Testsuite for flat analyzer"""

    def test_non_abs_directories_rejected(self):
        """Tests whether non absolute directories are rejected"""
        relativeDirectory = "dircompare/tests/testfiles"
        badcall = lambda: FlatCollector([relativeDirectory])
        self.assertRaises(ValueError, badcall)

    def test_non_existing_directory_rejected(self):
        file_path = os.path.abspath(__file__)
        test_dir = os.path.join(file_path, "testfilesxx")
        badcall = lambda: FlatCollector([test_dir])
        self.assertRaises(ValueError, badcall)

    def test_existing_directory_accepted(self):
        file_path = os.path.abspath(__file__)
        directory = os.path.dirname(file_path)
        test_dir = os.path.join(directory, "testfiles")
        # instantiate
        FlatCollector([test_dir])

    def test_correct_files_found(self):
        """ "Tests whether correct files are found"""
        file_path = os.path.abspath(__file__)
        directory = os.path.dirname(file_path)
        test_dir1 = os.path.join(directory, "testfiles")
        test_dir2 = os.path.join(directory, "testfiles2")
        # instantiate
        analyzer = FlatCollector([test_dir1, test_dir2])
        # collect
        analyzer.collect_files()
        result = analyzer.get_file_stats()
        # compare to expected
        expected_keys = set(
            [
                os.path.join(test_dir1, "test1.txt"),
                os.path.join(test_dir1, "test2.txt"),
                os.path.join(test_dir1, "test3.txt"),
                os.path.join(test_dir2, "test4.txt"),
                os.path.join(test_dir2, "test5.txt"),
                os.path.join(test_dir2, "testfiles3/test6.txt"),
            ]
        )
        self.assertEqual(set(result.get_result().keys()), expected_keys)


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
