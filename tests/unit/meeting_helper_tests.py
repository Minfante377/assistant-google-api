import unittest
import time

from consts.auth import Auth
from consts.utils import MeetingUtils
from helpers.meeting_helper import MeetingHandler
from utils.logger import logger


class TestMeetingHandler(unittest.TestCase):
    """
    This class implements all the unit tests for the MeetingHandler class.
    """

    @classmethod
    def setUpClass(cls):
        """
        Instanciate the Meeting to be used on the following tests.
        """
        logger.log_info("Instanciating the MeetingHandler")
        cls.handler = MeetingHandler(Auth.CREDENTIALS_FILE)

    def setUp(self):
        """
        Check that the EmailHandler object was correctly instantiated
        """
        if not self.handler:
            logger.log_error("Unable to instantiate the EmailHandler object")
            self.fail("Unable to instantiate the EmailHandler object")

    def test_create_event(self):
        """
        Preconditions:
            - MeetingHandler object correctly instantiated.

        Create a new event. Assert the result.

        """
        now = time.time()
        start = now + 30 * 60  # Current ts + 30 minutes
        end = now + 40 * 60  # Current ts + 40 minutes
        start = time.strftime(MeetingUtils.TIME_FORMAT,
                              time.localtime(start))
        start = "{}{}".format(start, MeetingUtils.TEST_DELTA)
        end = time.strftime(MeetingUtils.TIME_FORMAT, time.localtime(end))
        end = "{}{}".format(end, MeetingUtils.TEST_DELTA)

        result, error = self.handler.create_event(
            MeetingUtils.TEST_CALENDAR_ID,
            MeetingUtils.TEST_SUMMARY,
            MeetingUtils.TEST_ATTENDEES,
            start,
            end,
            MeetingUtils.TEST_TIMEZONE,
            MeetingUtils.TEST_LOCATION)
        assert result, "Error creating event: {}".format(error)

    def test_delete_event(self):
        """
        Preconditions:
            - MeetingHandler object correctly instantiated.
            - Test event created.

        Delete an event. Assert the result.

        """
        result, error = self.handler.delete_event(
            MeetingUtils.TEST_CALENDAR_ID,
            MeetingUtils.TEST_SUMMARY)

        assert result, "Error deleting event: {}".format(error)

    def test_create_calendar(self):
        """
        Preconditions:
            - MeetingHandler object correctly instantiated.

        Create a calendar. Assert the result
        """
        result, error = self.handler.create_calendar(
            MeetingUtils.TEST_CALENDAR_ID,
            MeetingUtils.TEST_TIMEZONE
        )
        assert result, "Error creating calendar: {}".format(error)

    def test_delete_calendar(self):
        """
        Preconditions:
            - MeetingHandler object correctly instantiated.
            - Test calendar created.

        Delete an calendar. Assert the result.

        """
        result, error = self.handler.delete_calendar(
            MeetingUtils.TEST_CALENDAR_ID)

        assert result, "Error deleting calendar: {}".format(error)
