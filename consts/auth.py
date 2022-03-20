class Auth:
    CLIENT_SECRET_FILE = "utils/files/client_secret.json"
    CREDENTIALS_FILE = "utils/files/credentials.json"
    SCOPES = ['https://www.googleapis.com/auth/gmail.send',
              'https://www.googleapis.com/auth/drive',
              'https://www.googleapis.com/auth/calendar']
