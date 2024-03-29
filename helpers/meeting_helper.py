import time

from googleapiclient import errors

from consts.utils import MeetingUtils
from helpers.service_helper import GoogleServiceHandler, get_auth
from utils.logger import logger


class MeetingHandler(GoogleServiceHandler):
    """
    This class handles the interaction with the Google Calendar API.
    """

    credentials = service = None

    def __init__(self, credential_file_path):
        """
        Instanciate the Meeting Handler using the provided credential file.

        Args:
            - credential_file_path(str): relative path of the credential file.

        Returns(None)

        """
        self.credentials, self.service =\
            super().__init__("calendar", "v3", credential_file_path)

        if not self.credentials:
            logger.log_error("Failed to initialize MeetingHandler")

    @get_auth
    def create_event(self, calendar_id, summary, attendees, start, end,
                     timezone, location):
        """
        Create a new event and invite the attendes.
        If location is 'online' a new Google Meet meeting will be created.

        Args:
            - calendar_id(string): ID of the calendar to add the meet to.
            - summary(string): Title of the meeting.
            - attendees(list): List of emails to invite.
            - start(string): Datetime start.
            - end(string): Datetime end.
            - timezone(string): Timezone of the event.
            - location(string): Location of the meeting.

        Returns(tupple):
            (True, None) or (False, err_msg)

        """
        logger.log_info("Creating new meet on calendar {} from {} to {}"
                        .format(calendar_id, start, end))
        attendees = [{'email': email} for email in attendees]
        logger.log_info("Attendees: {}".format(attendees))
        event = {
            "summary": summary,
            "start": {
                "dateTime": start,
                "timeZone": timezone
            },
            "end": {
                "dateTime": end,
                "timeZone": timezone
            },
            "attendees": attendees,
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 30}
                ]
            }
        }

        if location == MeetingUtils.ONLINE_EVENT:
            logger.log_info("Attaching Google Meet link")
            event['conferenceData'] = {}
            event['conferenceData']['createRequest'] =\
                {'requestId': 'SecureRandom.uuid'}
        else:
            event['location'] = location

        logger.log_info("Requesting event creation: {}".format(event))
        try:
            self.service.events().insert(calendarId=calendar_id,
                                         sendUpdates='all',
                                         conferenceDataVersion=1,
                                         body=event).execute()
            logger.log_info("Event successfully created")
            return True, None
        except errors.HttpError as e:
            logger.log_error("Error creating event: {}".format(e))
            return False, str(e)

    @get_auth
    def delete_event(self, calendar_id, summary):
        """
        Delete event from a certain calendar using Google Calendar API.

        Args:
            - calendar_id(str): ID of the calendar which the event belongs to.
            - summary(str): Summary of the event.

        Returns(tupple):
            (True, None) or (False, err_msg)

        """
        logger.log_info("Deleting event {} from calendar {}"
                        .format(summary, calendar_id))
        r, event_id = self._get_event_id_summary(calendar_id, summary)
        if not r:
            return False, event_id

        try:
            r = self.service.events().delete(calendarId=calendar_id,
                                             sendUpdates='all',
                                             eventId=event_id).execute()
            logger.log_info("Event successfully deleted")
            return True, None
        except errors.HttpError as e:
            logger.log_error("Failed to delete event: {}".format(e))
            return False, str(e)

    @get_auth
    def create_calendar(self, summary, time_zone):
        """
        Create a calendar using Google Calendar API

        Args:
            - summary(str): Name of the calendar.
            - time_zone(str): Time zone of the calendar.

        Returns(tupple):
            (True, None) or (False, err_msg)

        """
        logger.log_info("Creating calendar {}".format(summary))

        body = {
            'summary': summary,
            'timeZone': time_zone
        }

        try:
            self.service.calendars().insert(body=body).execute()
            logger.log_info("Successfully created calendar")
            return True, None
        except errors.HttpError as e:
            logger.log_error("Error creating calendar: {}".format(e))
            return False, str(e)

    @get_auth
    def delete_calendar(self, summary):
        """
        Delete calendar by calendar name using Google Calendar API

        Args:
            - summary(str): Name of the calendar.

        Returns(tupple):
            (True, None) or (False, err_msg)

        """
        logger.log_info("Deleting calendar {}".format(summary))
        r, calendar_id = self._get_calendar_id_summary(summary)
        if not r:
            logger.log_error("Failed to retrieve calendar ID")
            return False, calendar_id

        try:
            self.service.calendars().delete(calendarId=calendar_id).execute()
            logger.log_info("Successfully deleted calendar")
            return True, None
        except errors.HttpError as e:
            logger.log_error("Failed to delete calendar: {}".format(e))
            return False, str(e)

    @get_auth
    def get_calendar_id(self, summary):
        """
        Get ID of the calendar based on its summary

        Args:
            - summary(str): Name of the calendar.

        Returns(True, calendar_id) or (False, err_msg)

        """
        return self._get_calendar_id_summary(summary)

    def _get_event_id_summary(self, calendar_id, summary):
        """
        Get event id of a certain calendar filtering by its summary.

        Args:
            - calendar_id(str): ID of the calendar which the event belongs to.
            - summary(str): Summary of the event.

        Returns(tupple):
            (True, event_id) or (False, err_msg)

        """
        logger.log_info("Querying event ID of event {}".format(summary))
        r = self.service.events().list(calendarId=calendar_id,
                                       orderBy='updated').execute()

        items = r.get('items', [])
        for item in items:
            if item.get('summary', '') == summary:
                logger.log_info("Event found: {}".format(item))
                logger.log_info("Successfully queried event")
                return True, item['id']
        logger.log_error("No event found with summary {}".format(summary))
        return False, "No event found with summary {}".format(summary)

    def _get_calendar_id_summary(self, summary, timeout=10):
        """
        Get calendar id filtering by its summary.

        Args:
            - summary(str): Summary of the calendar.
            - timeout(int): Operation timeout

        Returns(tupple):
            (True, calendar_id) or (False, err_msg)

        """
        logger.log_info("Querying calendar ID of {}".format(summary))
        page_token = None
        now = time.time()
        while time.time() - now < timeout:
            r = self.service.calendarList().list(
                pageToken=page_token).execute()
            items = r.get('items', [])
            for item in items:
                if item.get('summary', '') == summary:
                    logger.log_info("Calendar found: {}".format(item))
                    logger.log_info("Successfully queried event")
                    return True, item['id']
            page_token = r.get('nextPageToken')
        logger.log_error("No calendar found with summary {}".format(summary))
        return False, "No calendar found with summary {}".format(summary)
