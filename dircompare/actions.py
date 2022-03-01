"""Actions to be preformed when triggers are activated"""
from abc import ABC, abstractmethod


class BaseAction(ABC):

    @abstractmethod
    def perform(self, message):
        pass


class StdOutAction(BaseAction):
    """Logs results to standard out"""

    def perform(self, message):
        print(message)

ACTIONMAP = {
    "stdout": StdOutAction
}