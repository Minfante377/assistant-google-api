import unittest

from consts.auth import Auth
from consts.utils import StorageUtils
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
