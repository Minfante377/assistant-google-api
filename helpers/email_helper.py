from base64 import urlsafe_b64encode

from email.mime.text import MIMEText
from googleapiclient import errors

from helpers.service_helper import GoogleServiceHandler
from utils.logger import logger


class EmailHandler(GoogleServiceHandler):
    """
    This class handles the interaction with the Google Gmail API.
    """

    credentials = service = None

    def __init__(self, credential_file_path):
        """
        Instanciate the Email Handler using the provided credential file.

        Args:
            - credential_file_path(str): relative path of the credential file.

        Returns(None)

        """
        self.credentials, self.service =\
            super().__init__("gmail", "v1", credential_file_path)

        if not self.credentials:
            logger.log_error("Failed to initialize EmailHandler")

    def send_email(self, recipient, sender, body, subject):
        """
        Build and send an email.

        Args:
            - recepient(str): Recipient's email address.
            - sender(str): Sender's email address.
            - body(str): Contents of the email.
            - subject(str): Subcject of the email.

        Returns(Tupple):
            (True, None) or (False, err_msg)

        """
        logger.log_info("Building a new message:\nFrom: {}\nTo: {}\n"
                        "Body: {}\n Subject: {}"
                        "\n".format(sender, recipient, body, subject))
        message = MIMEText(body)
        message['to'] = recipient
        message['from'] = sender
        message['subject'] = subject

        logger.log_info("Sending message")
        message = {'raw': urlsafe_b64encode(message.as_bytes()).decode()}
        try:
            message = self.service.users().messages().send(
                userId='me',
                body=message).execute()
            return True, None
        except errors.HttpError as e:
            logger.log_error("Error sending message: {}".format(e))
            return False, str(e)
