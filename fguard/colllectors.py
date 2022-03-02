"""Classes for collecting files from a directory tree"""
import os
from datetime import datetime
import pickle
import logging
from typing import List


DATEFORMAT = "%Y-%m-%dT%H:%M:%S"


class CollectionResult:
    """Represents result of collection"""

    def __init__(self, result, directories_scanned, date):
        self.result = result
        self.directories_scanned = directories_scanned
        self.date = date

    def __contains__(self, file_name):
        return file_name in self.result

    def get_directories_scanned(self):
        return self.directories_scanned

    def get_date(self):
        return self.date

    def get_files(self):
        return self.result.keys()

    def get_filename(self):
        number_directories = len(self.directories_scanned)
        return f"{self.date.strftime(DATEFORMAT)}_{number_directories}_rootdirs.scan"

    @staticmethod
    def from_file(file_path):
        """Load collectionresult from a file"""
        with open(file_path, "rb") as f:
            return pickle.load(f)

    def get_result(self):
        return self.result


class FlatCollector:
    """Walks a list of root directories
    and stores the absolute path to containing files
    in a dictionary with the associated values being information
    about the files."""

    def __init__(self, rootDirectories: List[str], log_level: str = "INFO") -> None:
        self._checkDirectories(rootDirectories)
        self.rootDirectories = rootDirectories
        self._files = {}
        self.logger = logging.getLogger()
        self.logger.setLevel(log_level)
        self.result = None

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
            self.logger.info(f" Collecting files from {directory}")
            for dirpath, dirnames, files in os.walk(directory):
                self.logger.debug(f"Collecting from {dirpath}")
                for file in files:
                    filename = os.path.join(dirpath, file)
                    file_stats = os.stat(filename)
                    file_info = {
                        "size": file_stats.st_size,
                        "modified_date": file_stats.st_mtime,
                        "created_date": file_stats.st_ctime,
                        "user_id": file_stats.st_uid,
                    }
                    self._files[filename] = file_info
        self.logger.info(f" Found {len(self._files.keys())} files")
        self.result = CollectionResult(
            self._files, self.rootDirectories, datetime.utcnow()
        )

    def get_file_stats(self):
        """Returns dictionary of file statistics"""
        if self.result is None:
            raise ValueError("No result, run collection first!")
        return self.result

    def save(self, output_directory):
        """writes collected files to the output file"""
        if self.result is None:
            raise ValueError("No result, run collection first!")
        filename = self.result.get_filename()
        with open(os.path.join(output_directory, filename), "wb") as f:
            pickle.dump(self.result, f)
