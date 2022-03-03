"""Classes for triggering actions"""
import re
from abc import ABC, abstractmethod
from typing import List, Set
from fguard.actions import BaseAction
from fguard.colllectors import CollectionResult

EXPERIMENT_NUMBER = r"Experiments_(\d{6})/(\d{6})/"


class BaseTrigger(ABC):
    """Base trigger class that defines
    its interface"""

    @abstractmethod
    def inspect(self, old_state: CollectionResult, new_state: CollectionResult):
        pass


class FilesMissingTrigger(BaseTrigger):
    """Will trigger an actions when
    more than a specified number of files are missing"""

    def __init__(self, actions: List[BaseAction], number_threshold: int = 100):
        self.number_threshold = number_threshold
        self.actions = actions

    def _construct_message(
        self, missing_files_number, old_state, new_state, experiments_affected
    ):
        return {
            "title": "Missing files detected!",
            "description": f"There where {missing_files_number} missing files detected between a scan performed at {new_state.get_date()} and {old_state.get_date()}. There were {len(experiments_affected.keys())} experiments affected.",
            "subject": "Missing files detected",
            "details": {
                "missing_file_number": missing_files_number,
                "experiments_affected": experiments_affected,
                "new_directories_scanned": new_state.get_directories_scanned(),
                "old_directories_scanned": old_state.get_directories_scanned(),
                "new_date[utc]": str(new_state.get_date()),
                "old_date[utc": str(old_state.get_date()),
            },
        }

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
            message = self._construct_message(
                missing_files_number,
                old_state,
                new_state,
                experiments_affected,
            )
            for action in self.actions:
                action.perform(message)
            return message
        return {}

class ExperimentsMissingTrigger(BaseTrigger):
    """Will trigger actions when an experiment is missing"""
    def __init__(self, actions: List[BaseAction]):
        self.actions = actions

    def _get_experiments(self, state: CollectionResult) -> Set[int]:
        experiments = set()
        for file in state.get_files():
            matched_experiment = re.findall(EXPERIMENT_NUMBER, file)
            if len(matched_experiment) > 0 and len(matched_experiment[0]) > 1:
                experiment_number = matched_experiment[0][1]
                experiments.add(experiment_number)
        return experiments

    def _construct_message(
        self, missing_experiments, old_state, new_state
    ):
        return {
            "title": "Missing experiments detected!",
            "description": f"There where {len(missing_experiments)} missing experiments detected between a scan performed at {new_state.get_date()} and {old_state.get_date()}.",
            "subject": "Missing experiments detected",
            "details": {
                "missing_experiment_number": len(missing_experiments),
                "experiments_missing": missing_experiments,
                "new_directories_scanned": new_state.get_directories_scanned(),
                "old_directories_scanned": old_state.get_directories_scanned(),
                "new_date[utc]": str(new_state.get_date()),
                "old_date[utc": str(old_state.get_date()),
            },
        }

    def inspect(self, old_state: CollectionResult, new_state: CollectionResult):
        old_experiments = self._get_experiments(old_state)
        new_experiments = self._get_experiments(new_state)
        # go through experiments and check missing ones
        missing_experiments = []
        for experiment in old_experiments:
            if experiment not in new_experiments:
                missing_experiments.append(experiment)
        if len(missing_experiments) > 0:
            message = self._construct_message(
                missing_experiments,
                old_state,
                new_state,
            )
            for action in self.actions:
                action.perform(message)
            return message
        return {}



TRIGGERMAP = {"files_missing": FilesMissingTrigger}
