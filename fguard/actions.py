"""Actions to be preformed when triggers are activated"""
from abc import ABC, abstractmethod
from jinja2 import Template
from fguard.templates.email import EMAIL_TEMPLATE
import os


class BaseAction(ABC):

    @abstractmethod
    def perform(self, message):
        pass


class StdOutAction(BaseAction):
    """Logs results to standard out"""

    def _format_message(self, message):
        output = "\n" + "".join(["#"]*len(message["title"])) + "\n"
        output += message["title"] + "\n"
        output += "".join(["#"]*len(message["title"])) + "\n"
        output += message["description"] + "\n\n"
        output += "Details:\n"
        for key, value in message["details"].items():
            output += str(key)
            output += " - "
            output += str(value)
            output += "\n"
        return output

    def perform(self, message):
        print(self._format_message(message))


class EmailAction(BaseAction):
    """Send email with results"""

    FROM = "fguard@cbe.vbc.ac.at"

    def _format_message(self, message):
        """Formats email body"""
        # construct details
        details = ""
        for key, value in message["details"].items():
            details += str(key)
            details += " - "
            details += str(value)
            details += "<br>"
        t = Template(EMAIL_TEMPLATE)
        return t.render({
            "title": message["title"],
            "description": message["description"],
            "details": details
        })

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
        return f"subject:{message['subject']}\ncontent-type:text/html\ncontent-disposition:inline\nMIME-Version: 1.0\nfrom:{self.FROM}\n{self._format_message(message)}"

    def perform(self, message):
        body = self.get_mail_body(message)
        os.system(f"echo '{body}' | sendmail {self.recipient}")


ACTIONMAP = {"stdout": StdOutAction, "email": EmailAction}
