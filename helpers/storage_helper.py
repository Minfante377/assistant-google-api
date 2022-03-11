import mimetypes
import os

from googleapiclient import errors
from googleapiclient.http import MediaFileUpload

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
    def create_folder(self, folder_name, parent_name=None):
        """
        Creates a folder using Google Drive API.

        Args:
            - folder_name(str): The name of the folder to create.
            - parent_name(list): Parent folder name.

        Returns(Tupple):
            (True, None) or (False, err_msg)

        """
        logger.log_info("Creating a new folder:\nName:{}\nParent IDs:{}"
                        .format(folder_name, parent_name))

        body = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_name:
            r, parent_id = self._get_folder_id(parent_name)
            if r:
                body['parents'] = parent_id
            else:
                return False, parent_id

        try:
            self.service.files().create(body=body, fields='id').execute()
            logger.log_info("Folder {} successfully created"
                            .format(folder_name))
            return True, None
        except errors.HttpError as e:
            logger.log_error("Error creating folder: {}".format(e))
            return False, str(e)

    @get_auth
    def create_file(self, file_name, parent_name=None):
        """
        Creates a folder using Google Drive API.

        Args:
            - file_name(str): The name of the file to create.
            - parent_name(list): Parent folder name.

        Returns(Tupple):
            (True, None) or (False, err_msg)

        """
        logger.log_info("Creating a new file:\nName:{}\nParent IDs:{}"
                        .format(file_name, parent_name))

        mime_type, err = mimetypes.guess_type(file_name)
        if err:
            logger.log_error("Error detecting file type: {}".format(err))
            return False, err

        logger.log_info("File type detected: {}".format(mime_type))
        media = MediaFileUpload(file_name, mimetype=mime_type)

        file_metadata = {
            'name': os.path.basename(file_name),
        }
        if parent_name:
            r, parent_id = self._get_folder_id(parent_name)
            if r:
                file_metadata['parents'] = parent_id
            else:
                return False, parent_id

        try:
            self.service.files().create(
                body=file_metadata,
                media_body=media).execute()
            logger.log_info("File {} successfully created"
                            .format(file_name))
            return True, None
        except errors.HttpError as e:
            logger.log_error("Error creating file: {}".format(e))
            return False, str(e)

    def _get_file_id(self, file_name, parent_id=None):
        """
        Query the file id of a folder by file name.

        Args:
            - file_name(str): The name of the file we want to get the id
                                from.
            - parent_id(str): Parent folder ID.

        Returns(tupple):
            (True, [id]) or (False, err_msg)

        """
        query = "name='{}'".format(file_name) +\
                " and mimeType='application/vnd.google-apps.file'" +\
                " and trashed=false"
        if parent_id:
            query += " and {} in parents".format(parent_id)

        fields = "nextPageToken, files(id)"
        logger.log_info("Querying file {}".format(query))
        try:
            r = self.service.files().list(q=query,  fields=fields,
                                          spaces='drive').execute()
            items = r.get('files', [])
            if not items:
                logger.log_error("No file found")
                return False, "No file found"
            file_id = items[0]['id']
            return True, [file_id]
        except Exception as e:
            logger.log_info("Error querying file: {}".format(e))
            return False, str(e)

    def _get_folder_id(self, folder_name, parent_id=None):
        """
        Query the folder id of a folder by folder name.

        Args:
            - folder_name(str): The name of the folder we want to get the id
                                from.
            - parent_id(str): Parent folder ID.

        Returns(tupple):
            (True, [id]) or (False, err_msg)

        """
        query = "name='{}'".format(folder_name) +\
                " and mimeType='application/vnd.google-apps.folder'" +\
                " and trashed=false"
        if parent_id:
            query += " and {} in parents".format(parent_id)

        fields = "nextPageToken, files(id)"
        logger.log_info("Querying folder {}".format(query))
        try:
            r = self.service.files().list(q=query,  fields=fields,
                                          spaces='drive').execute()
            items = r.get('files', [])
            if not items:
                logger.log_error("No folder found")
                return False, "No folder found"
            folder_id = items[0]['id']
            return True, [folder_id]
        except Exception as e:
            logger.log_info("Error querying folder: {}".format(e))
            return False, str(e)
