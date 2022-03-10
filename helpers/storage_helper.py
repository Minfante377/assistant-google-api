from googleapiclient import errors

from helpers.service_helper import GoogleServiceHandler, get_auth
from utils.logger import logger


class StorageHandler(GoogleServiceHandler):
    """
    This class handles the interaction with the Google Drive API.
    """

    credentials = service = None

    def __init__(self, crendentials_file_path):
        """
        Instanciate the Storage Handler using the provided credential file.

        Args:
            - credential_file_path(str): relative path of the credential file.

        Returns(None)

        """
        self.credentials, self.service =\
            super().__init__("drive", "v3", crendentials_file_path)

        if not self.credentials:
            logger.log_error("Failed to initialize StorageHandler")

    @get_auth
    def create_folder(self, folder_name, parent_ids=[]):
        """
        Creates a folder using Google Drive API.

        Args:
            - folder_name(str): The name of the folder to create.
            - parent_id(list): The list of parents IDs of the folder.

        Returns(Tupple):
            (True, None) or (False, err_msg)

        """
        logger.log_info("Creating a new folder:\nName:{}\nParent IDs:{}"
                        .format(folder_name, parent_ids))

        body = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_ids:
            body['parents'] = parent_ids

        try:
            self.service.files().create(body=body, fields='id').execute()
            logger.log_info("Folder {} successfully created"
                            .format(folder_name))
            return True, None
        except errors.HttpError as e:
            logger.log_error("Error creating folder: {}".format(e))
            return False, str(e)
