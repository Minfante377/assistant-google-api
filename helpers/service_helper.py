import os

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from consts.auth import Auth

from utils.logger import logger


def get_auth(f):
    """
    Check token and refresh it when needed.
    This function is intendeed to be used as a decorator for other class
    methods.

    Args:
        - f(function):

    Returns(function):
    """
    def _auth():
        os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = "1"
        creds = None
        if os.path.exists(Auth.CREDENTIALS_FILE):
            try:
                creds = Credentials.from_authorized_user_file(
                    Auth.CREDENTIALS_FILE, Auth.SCOPES)
            except Exception:
                creds = None
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                logger.log_info("Credentials refreshed")
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    Auth.CLIENT_SECRET_FILE, Auth.SCOPES)
                creds = flow.run_local_server(port=0)
            with open(Auth.CREDENTIALS_FILE, 'w+') as token:
                token.write(creds.to_json())
        return creds

    def wrapper(*args):
        creds = _auth()
        args[0].credentials = creds
        return f(*args)

    return wrapper


class GoogleServiceHandler:
    """
    This class handles the creation of Google API service handler.
    """

    @get_auth
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
