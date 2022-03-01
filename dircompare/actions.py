"""Actions to be preformed when triggers are activated"""
from abc import ABC, abstractmethod
import os


class BaseAction(ABC):
    @abstractmethod
    def perform(self, message):
        pass


class StdOutAction(BaseAction):
    """Logs results to standard out"""

    def perform(self, message):
        print(message)


class EmailAction(BaseAction):
    """Logs results to standard out"""
    FROM = "dircompare@cbe.vbc.ac.at"
    def __init__(self):
        """Get recipient from environment variables"""
        recipient = os.getenv("DIRCOMPARE_EMAIL_ADDRESS")
        if recipient is None:
            raise ValueError("You need to define the 'DIRCOMPARE_EMAIL_ADDRESS' environment variable to use the EmailAction trigger")
        self.recipient = recipient
    def get_mail_body(self, message):
        return f"subject:{message['trigger']}\nfrom:{self.FROM}\n{message}"
    def perform(self, message):
        body = self.get_mail_body(message)
        os.system(f"echo '{body}' | sendmail {self.recipient}")


ACTIONMAP = {
    "stdout": StdOutAction,
    "email": EmailAction
}