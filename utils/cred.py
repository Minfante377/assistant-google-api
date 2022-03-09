import os

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


from consts.auth import EmailAuth
from consts.utils import EmailUtils

SCOPES = ['https://mail.google.com/']
our_email = EmailUtils.TEST_EMAIL


def gmail_authenticate():
    if os.path.exists(EmailAuth.CREDENTIALS_FILE):
        try:
            creds = Credentials.from_authorized_user_file(
                EmailAuth.CREDENTIALS_FILE, SCOPES)
            print("Credentials loaded")
        except Exception:
            creds = None
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                EmailAuth.CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(EmailAuth.CREDENTIALS_FILE, 'w+') as token:
            token.write(creds.to_json())


gmail_authenticate()
