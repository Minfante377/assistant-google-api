import unittest

from consts.auth import EmailAuth
from consts.utils import EmailUtils
from helpers.email_helper import EmailHandler
from utils.logger import logger


class TestEmailHandler(unittest.TestCase):
    """
    This class implements all the unit tests for the EmailHandler class.
    """

    @classmethod
    def setUpClass(cls):
        """
        Instanciate the EmailHandler to be used on the following tests.
        """
        logger.log_info("Instanciating the EmailHandler")
        cls.handler = EmailHandler(EmailAuth.CREDENTIALS_FILE)

    def setUp(self):
        """
        Check that the EmailHandler object was correctly instantiated
        """
        if not self.handler:
            logger.log_error("Unable to instantiate the EmailHandler object")
            self.fail("Unable to instantiate the EmailHandler object")

    def test_send_email(self):
        """
        Preconditions:
            - EmailHandler object correctly instantiated.

        Send an email to the test email. Assert the result.

        """
        result, error = self.handler.send_email(
            EmailUtils.TEST_EMAIL,
            EmailUtils.TEST_EMAIL,
            EmailUtils.TEST_BODY,
            EmailUtils.TEST_SUBJECT)
        assert result, "Failed to send email: {}".format(error)

    def test_send_email_attachement(self):
        """
        Preconditions:
            - EmailHandler object correctly instantiated.

        Send an email with attachement to the test email. Assert the result.
        The test files used are pdf and image type.

        """
        result, error = self.handler.send_email_attachement(
            EmailUtils.TEST_EMAIL,
            EmailUtils.TEST_EMAIL,
            EmailUtils.TEST_BODY,
            EmailUtils.TEST_SUBJECT,
            EmailUtils.TEST_FILE_PDF)
        assert result, "Failed to send email with pdf: {}".format(error)

        result, error = self.handler.send_email_attachement(
            EmailUtils.TEST_EMAIL,
            EmailUtils.TEST_EMAIL,
            EmailUtils.TEST_BODY,
            EmailUtils.TEST_SUBJECT,
            EmailUtils.TEST_FILE_IMAGE)
        assert result, "Failed to send email with image: {}".format(error)
