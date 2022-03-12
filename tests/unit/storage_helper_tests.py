import os
import unittest

from consts.auth import Auth
from consts.utils import EmailUtils, StorageUtils
from helpers.storage_helper import StorageHandler
from utils.logger import logger


class TestStorageHandler(unittest.TestCase):
    """
    This class implements all the unit tests for the StorageHandler class.
    """

    @classmethod
    def setUpClass(cls):
        """
        Instanciate the EmailHandler to be used on the following tests.
        """
        logger.log_info("Instanciating the StorageHandler")
        cls.handler = StorageHandler(Auth.CREDENTIALS_FILE)

    def setUp(self):
        """
        Check that the EmailHandler object was correctly instantiated
        """
        if not self.handler:
            logger.log_error("Unable to instantiate the EmailHandler object")
            self.fail("Unable to instantiate the EmailHandler object")

    def test_create_folder(self):
        """
        Preconditions:
            - StorageHandler object correctly instantiated.

        Create a new folder. Assert the result.

        """
        result, error =\
            self.handler.create_folder(StorageUtils.TEST_FOLDER_NAME)
        assert result, "Failed to create new folder: {}".format(error)

    def test_create_file(self):
        """
        Preconditions:
            - StorageHandler object correctly instantiated.

        Create a new file. Assert the result.
        Create a pdf and image file.

        """

        result, error =\
            self.handler.create_file(StorageUtils.TEST_FILE_IMAGE)
        assert result, "Failed to create new image file: {}".format(error)

        result, error =\
            self.handler.create_file(StorageUtils.TEST_FILE_PDF)
        assert result, "Failed to create new pdf file: {}".format(error)

    def test_share_folder(self):
        """
        Preconditions:
            - StorageHandler object correctly instantiated.
            - Folder "test" created.

        Share a folder. Assert the result.

        """
        result, error = self.handler.share_folder(
                StorageUtils.TEST_FOLDER_NAME,
                EmailUtils.TEST_EMAIL)
        assert result, "Failed to share folder: {}".format(error)

    def test_delete_folder(self):
        """
        Preconditions:
            - StorageHandler object correctly instantiated.
            - Folder "test" created.

        Delete a folder. Assert the result.

        """
        result, error = self.handler.delete_folder(
            StorageUtils.TEST_FOLDER_NAME)
        assert result, "Failed to delete folder: {}".format(error)

    def test_delete_file(self):
        """
        Preconditions:
            - StorageHandler object correctly instantiated.
            - Test files created.

        Delete a folder. Assert the result.

        """
        result, error = self.handler.delete_file(
            os.path.basename(StorageUtils.TEST_FILE_IMAGE))
        assert result, "Failed to delete image file: {}".format(error)

        result, error = self.handler.delete_file(
            os.path.basename(StorageUtils.TEST_FILE_PDF))
        assert result, "Failed to delete pdf file: {}".format(error)
