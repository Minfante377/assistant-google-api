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
