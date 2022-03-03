"""Test triggers"""

import unittest
from datetime import datetime
from unittest.mock import MagicMock
from fguard.triggers import FilesMissingTrigger, ExperimentsMissingTrigger
from fguard.colllectors import CollectionResult


class TestFilesMissingTrigger(unittest.TestCase):
    """Test suite for files missing trigger"""

    def test_triggered_when_files_missing(self):
        """Tests that trigger is triggered when
        more than number_threshold files are missing"""
        new_files = {"test1": "asdf", "test2": "fdsa"}
        old_files = {"test1": "asdf", "test2": "fdsa", "test3": "asdf", "test4": "fdsa"}
        # create results
        new_result = CollectionResult(
            new_files, directories_scanned=["test"], date=datetime.now()
        )
        old_result = CollectionResult(
            old_files, directories_scanned=["test"], date=datetime.now()
        )
        # set up mocking
        mock_action = MagicMock()
        perform_mock = MagicMock()
        mock_action.perform = perform_mock
        # check triggering
        trigger = FilesMissingTrigger(number_threshold=1, actions=[mock_action])
        trigger.inspect(old_result, new_result)
        perform_mock.assert_called()

    def test_experiments_found_correctly(self):
        """Tests that experiments are found correctly"""
        new_files = {"test1": "asdf", "test2": "fdsa"}
        old_files = {
            "test1": "asdf",
            "test2": "fdsa",
            "/groups/gerlich/experiments/Experiments_004200/004211/test3": "asdf",
            "/groups/gerlich/experiments/Experiments_004200/004212/test4": "fdsa",
        }
        # create results
        new_result = CollectionResult(
            new_files, directories_scanned=["test"], date=datetime.now()
        )
        old_result = CollectionResult(
            old_files, directories_scanned=["test"], date=datetime.now()
        )
        # set up mocking
        mock_action = MagicMock()
        # check triggering
        trigger = FilesMissingTrigger(number_threshold=1, actions=[mock_action])
        message = trigger.inspect(old_result, new_result)
        self.assertEqual(
            message["details"]["experiments_affected"], {"004211": 1, "004212": 1}
        )

    def test_malformed_experiments_not_found(self):
        """Tests that malformed experimetns are excluded"""
        new_files = {"test1": "asdf", "test2": "fdsa"}
        old_files = {
            "test1": "asdf",
            "test2": "fdsa",
            "/groups/gerlich/experiments/Experiments_0000/004211/test3": "asdf",
            "/groups/gerlich/experiments/Experiments_0000/004212/test4": "fdsa",
        }
        # create results
        new_result = CollectionResult(
            new_files, directories_scanned=["test"], date=datetime.now()
        )
        old_result = CollectionResult(
            old_files, directories_scanned=["test"], date=datetime.now()
        )
        # set up mocking
        mock_action = MagicMock()
        # check triggering
        trigger = FilesMissingTrigger(number_threshold=1, actions=[mock_action])
        message = trigger.inspect(old_result, new_result)
        self.assertEqual(message["details"]["experiments_affected"], {})


class TestExperimentsMissingTrigger(unittest.TestCase):
    """Test for experiments missing trigger"""

    def test_triggered_when_experiments_missing(self):
        """Test whether is correctly triggered when experiments are missing"""
        new_files = {"test1": "asdf", "test2": "fdsa"}
        old_files = {
            "test1": "asdf",
            "test2": "fdsa",
            "/groups/gerlich/experiments/Experiments_004200/004211/test3": "asdf",
            "/groups/gerlich/experiments/Experiments_004200/004212/test4": "fdsa",
        }
        # create results
        new_result = CollectionResult(
            new_files, directories_scanned=["test"], date=datetime.now()
        )
        old_result = CollectionResult(
            old_files, directories_scanned=["test"], date=datetime.now()
        )
        # set up mocking
        mock_action = MagicMock()
        perform_mock = MagicMock()
        mock_action.perform = perform_mock
        # check triggering
        trigger = ExperimentsMissingTrigger(actions=[mock_action])
        message = trigger.inspect(old_result, new_result)
        self.assertEqual(
            sorted(message["details"]["experiments_missing"]), sorted(["004211", "004212"])
        )
        perform_mock.assert_called()

    def test_not_triggered_when_files_missing(self):
        """Test whether is correctly triggered when experiments are missing"""
        new_files = {
            "/groups/gerlich/experiments/Experiments_004200/004211/test3": "asdf"
        }
        old_files = {
            "/groups/gerlich/experiments/Experiments_004200/004211/test3": "asdf",
            "/groups/gerlich/experiments/Experiments_004200/004211/test4": "fdsa",
        }
        # create results
        new_result = CollectionResult(
            new_files, directories_scanned=["test"], date=datetime.now()
        )
        old_result = CollectionResult(
            old_files, directories_scanned=["test"], date=datetime.now()
        )
        # set up mocking
        mock_action = MagicMock()
        perform_mock = MagicMock()
        mock_action.perform = perform_mock
        # check triggering
        trigger = ExperimentsMissingTrigger(actions=[mock_action])
        message = trigger.inspect(old_result, new_result)
        self.assertEqual(message, {})
        perform_mock.assert_not_called()

if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
