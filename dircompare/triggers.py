"""Classes for triggering actions"""
from email import message
import re
from abc import ABC, abstractmethod
import json
from typing import List
from dircompare.actions import BaseAction
from dircompare.colllectors import CollectionResult

EXPERIMENT_NUMBER = r"Experiments_(\d{6})/(\d{6})"


class BaseTrigger(ABC):
    """Base trigger class that defines
    its interface"""

    @abstractmethod
    def inspect(self, old_state: dict, new_state: dict):
        pass


class FilesMissingTrigger(BaseTrigger):
    """Will trigger an action when
    more than a specified number of files are missing"""

    def __init__(self, actions: List[BaseAction], number_threshold: int = 100):
        self.number_threshold = number_threshold
        self.actions = actions

    def inspect(self, old_state: CollectionResult, new_state: CollectionResult):
        missing_files_number = 0
        missing_files = []
        experiments_affected = {}
        for file in old_state.get_files():
            if file not in new_state:
                missing_files_number += 1
                missing_files.append(file)
                matched_experiment = re.findall(EXPERIMENT_NUMBER, file)
                if len(matched_experiment) > 0 and len(matched_experiment[0]) > 1:
                    experiment_number = matched_experiment[0][1]
                    if experiment_number in experiments_affected:
                        experiments_affected[experiment_number] += 1
                    else:
                        experiments_affected[experiment_number] = 1
        # check whether actions should be performed
        if missing_files_number > self.number_threshold:
            message = {
                "trigger": "Missing files trigger",
                "missing_file_number": missing_files_number,
                "experiments_affected": experiments_affected,
                "new_directories_scanned": new_state.get_directories_scanned(),
                "old_directories_scanned": old_state.get_directories_scanned(),
                "new_date[utc]": str(new_state.get_date()),
                "old_date[utc": str(old_state.get_date()),
            }
            for action in self.actions:
                action.perform(json.dumps(message))
            return message


TRIGGERMAP = {"files_missing": FilesMissingTrigger}
