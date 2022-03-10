import mimetypes
import os
from base64 import urlsafe_b64encode

from email import encoders
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart, MIMEBase
from email.mime.text import MIMEText
from googleapiclient import errors

from helpers.service_helper import GoogleServiceHandler, get_auth
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

    @get_auth
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
                        "Body: {}\nSubject: {}"
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

    @get_auth
    def send_email_attachement(self, recipient, sender, body, subject,
                               attachement):
        """
        Build and send an email with attachement.

        Args:
            - recepient(str): Recipient's email address.
            - sender(str): Sender's email address.
            - body(str): Contents of the email.
            - subject(str): Subcject of the email.
            - attachement(str): Path to the file.

        Returns(Tupple):
            (True, None) or (False, err_msg)

        """
        if not os.path.exists(attachement):
            logger.log_error("The attachement file does not exist:"
                             "{}".format(attachement))
            return False, "The attachement file does not exist"

        logger.log_info("Building a new message:\nFrom: {}\nTo: {}\n"
                        "Body: {}\nSubject: {}\nFile:{}"
                        .format(sender, recipient, body, subject, attachement))
        message = MIMEMultipart()
        message['to'] = recipient
        message['from'] = sender
        message['subject'] = subject

        msg = MIMEText(body)
        message.attach(msg)

        content_type, encoding = mimetypes.guess_type(attachement)
        if not content_type or not encoding:
            content_type = 'application/octet-stream'
        main_type, sub_type = content_type.split('/', 1)

        if main_type == 'text':
            fp = open(attachement, 'rb')
            msg = MIMEText(fp.read(), _subtype=sub_type)
            fp.close()
        elif main_type == 'image':
            fp = open(attachement, 'rb')
            msg = MIMEImage(fp.read(), _subtype=sub_type)
            fp.close()
        elif main_type == 'audio':
            fp = open(attachement, 'rb')
            msg = MIMEAudio(fp.read(), _subtype=sub_type)
            fp.close()
        else:
            fp = open(attachement, 'rb')
            msg = MIMEBase(main_type, sub_type)
            msg.set_payload(fp.read())
            encoders.encode_base64(msg)
            fp.close()
        filename = os.path.basename(attachement)
        msg.add_header('Content-Disposition', 'attachement', filename=filename)
        message.attach(msg)

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
