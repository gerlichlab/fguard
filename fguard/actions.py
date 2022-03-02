"""Actions to be preformed when triggers are activated"""
from abc import ABC, abstractmethod
import json
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
    """Send email with results"""

    FROM = "fguard@cbe.vbc.ac.at"

    def __init__(self):
        """Get recipient from environment variables"""
        recipient = os.getenv("FGUARD_EMAIL_ADDRESS")
        if recipient is None:
            raise ValueError(
                "You need to define the 'FGUARD_EMAIL_ADDRESS' environment variable to use the EmailAction trigger"
            )
        self.recipient = recipient

    def get_mail_body(self, message):
        # format body
        body_string = "This is an automatically generated message from fguard\n\n\n"
        for key, value in message.items():
            body_string += str(key)
            body_string += " - "
            body_string += str(value)
            body_string += "\n"
        return f"subject:{message['trigger']}\nfrom:{self.FROM}\n{body_string}"

    def perform(self, message):
        body = self.get_mail_body(json.loads(message))
        os.system(f"echo '{body}' | sendmail {self.recipient}")


ACTIONMAP = {"stdout": StdOutAction, "email": EmailAction}
