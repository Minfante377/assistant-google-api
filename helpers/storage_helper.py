import mimetypes
import os

from googleapiclient import errors
from googleapiclient.http import MediaFileUpload

from consts.roles import Storage
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
    def share_folder(self, folder_name, email,
                     parent_name=None,
                     role=Storage.READ,
                     notify=True):
        """
        Share folder with an email owner with a certain role.

        Args:
            - folder_name(str): Name of the folder to share.
            - email(str): Email address to share the folder with.
            - role(str): read/write role.
            - notify(bool): Send notification by email or not.

        Returns(tupple):
            (True, None) or (False, err_msg)
        """
        logger.log_info("Sharing folder {} with {}. Role {}"
                        .format(folder_name, email, role))
        body = {
            'role': role,
            'emailAddress': email,
            'type': 'user'
        }

        if parent_name:
            r, parent_id = self._get_folder_id(parent_name)
            if not r:
                logger.log_error("Error sharing folder: {}".format(parent_id))
                return False, parent_id
        else:
            parent_id = None

        r, folder_id = self._get_folder_id(folder_name, parent_id=parent_id)
        if not r:
            logger.log_error("Error sharing folder: {}".format(parent_id))
            return False, folder_id

        if role == Storage.OWN:
            transfer_ownership = True
            move = True
        else:
            transfer_ownership = False
            move = False

        try:
            self.service.permissions().create(
                body=body,
                fileId=folder_id[0],
                fields='id',
                sendNotificationEmail=notify,
                transferOwnership=transfer_ownership,
                moveToNewOwnersRoot=move,
                supportsAllDrives=True).execute()
            logger.log_info("Successfully shared folder {}"
                            .format(folder_name))
            return True, None
        except Exception as e:
            logger.log_error("Error sharing folder: {}".format(e))
            return False, str(e)

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

    def delete_folder(self, folder_name, parent_name=None):
        """
        Delete a folder using google drive API.

        Args:
            - folder_name(str): The name of the folder to delete.
            - parent_name(list): Parent folder name.

        Returns(Tupple):
            (True, None) or (False, err_msg)

        """
        logger.log_info("Deleting folder {}".format(folder_name))
        if parent_name:
            r, parent_name = self._get_folder_id(parent_name)
            if not r:
                return False, parent_name

        r, folder_id = self._get_folder_id(folder_name, parent_id=parent_name)
        if not r:
            logger.log_error("Folder {} does not exist".format(folder_name))
            return False, folder_id
        try:
            self.service.files().delete(fileId=folder_id[0]).execute()
            logger.log_info("Folder {} deleted.".format(folder_name))
            return True, None
        except errors.HttpError as e:
            logger.log_error("Error deleting folder: {}".format(e))
            return False, str(e)

    def delete_file(self, file_name, parent_name=None):
        """
        Delete a file using google drive API.

        Args:
            - file_name(str): The name of the file to delete.
            - parent_name(list): Parent folder name.

        Returns(Tupple):
            (True, None) or (False, err_msg)

        """
        logger.log_info("Deleting file {}".format(file_name))
        if parent_name:
            r, parent_name = self._get_folder_id(parent_name)
            if not r:
                return False, parent_name

        r, file_id = self._get_file_id(file_name, parent_id=parent_name)
        if not r:
            logger.log_error("File {} does not exist".format(file_name))
            return False, file_id
        try:
            self.service.files().delete(fileId=file_id[0]).execute()
            logger.log_info("Folder {} deleted.".format(file_name))
            return True, None
        except errors.HttpError as e:
            logger.log_error("Error deleting file: {}".format(e))
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
