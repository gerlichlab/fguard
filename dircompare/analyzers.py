"""Classes for analyzing a directory tree in terms of contained files"""
import os
import pickle
import logging
from typing import List


class FlatAnalyzer:
    """Walks a list of root directories
    and stores the absolute path to containing files
    in a dictionary with the associated values being information
    about the files."""

    def __init__(self, rootDirectories: List[str], log_level: str = "INFO") -> None:
        self._checkDirectories(rootDirectories)
        self.rootDirectories = rootDirectories
        self.files = {}
        self.logger = logging.getLogger()
        self.logger.setLevel(log_level)

    def _checkDirectories(self, directories: List[str]) -> None:
        """Checks whether the supplied directories exist and whether
        it is supplied as an absolute path"""
        for directory in directories:
            if not os.path.isdir(directory):
                raise ValueError(f"Path is not a directory: {directory}")
            if not os.path.isabs(directory):
                raise ValueError(f"Path {directory} should be supplied as absolute")

    def collect_files(self):
        """Walks specified root directories and
        puts found files with associated statistics
        into a flat dictionary"""
        for directory in self.rootDirectories:
            self.logger.info(f"Collecting files from {directory}")
            for dirpath, dirnames, files in os.walk(directory):
                for file in files:
                    filename = os.path.join(dirpath, file)
                    file_stats = os.stat(filename)
                    file_info = {
                        "size": file_stats.st_size,
                        "modified_date": file_stats.st_mtime,
                        "created_date": file_stats.st_ctime,
                        "user_id": file_stats.st_uid,
                    }
                    self.logger.debug(f"Processing {filename}")
                    self.files[filename] = file_info
        self.logger.info(f"Found {len(self.files.keys())} files")

    def get_file_stats(self):
        """Returns dictionary of file statistics"""
        return self.files

    def save_file_state(self, output_file):
        """writes collected files to the output file"""
        if os.path.isfile(output_file):
            raise ValueError("Output file already exists!")
        pickle.dump(self.files, open(output_file, "wb"))
