import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from utils.logger import logger


class GoogleServiceHandler:
    """
    This class handles the creation of Google API service handler.
    """

    def __init__(self, service, version, credential_file_path):
        """
        Read credentials file and save them in memory.

        Args:
            - service(str): service name. Read Google API doc for reference.
            - version(str): service version. Read Google API doc for reference.
            - credential_file_path(str): relative path of the credential file.

        Returns(tupple | None):
            (credentials, service)

        """
        logger.log_info("Initializing {} Handler...".format(service))
        path = os.path.join(os.getcwd(), credential_file_path)
        if not os.path.exists(path):
            logger.log_error("{} configuration file does not exists"
                             .format(path))
            return None, None

        credentials = Credentials.from_authorized_user_file(path)
        service = build(service, version, credentials=credentials)
        logger.log_info("{} Handler initialized".format(service))
        return credentials, service
