import base64
import json
import tempfile

from fastapi import FastAPI

from helpers import email_helper, meeting_helper, service_helper,\
    storage_helper
from models import Email, Event, NewEvent
from consts.auth import Auth
from utils.logger import logger

app = FastAPI()


@app.post("/email/send_email")
async def send_email(email: Email):
    """
    Send an email with the specified information.

    Request: POST
    Body: {'recipient': str ,
           'sender': str,
           'body': str,
           'subject': str,
           'attachement': optional[str],
           'extension': optional[str]
    }
    Returns {'statusCode': , 'error': error msg}
    """
    logger.log_info("New email request received: {}".format(email))

    if email.attachement:
        f = tempfile.NamedTemporaryFile(suffix=email.extension)
        data = base64.b64decode(email.attachement)
        f.write(data)
        result, err = \
            email_helper.EmailHandler(Auth.CREDENTIALS_FILE)\
            .send_email_attachement(email.recipient, email.sender, email.body,
                                    email.subject, f.name)
        if not result:
            logger.log_error("Error sending message")
            return json.dumps({
                'statusCode': 500,
                'error': err})
        return json.dumps({
            'statusCode': 200,
            'error': ''})

    result, err = email_helper.EmailHandler(Auth.CREDENTIALS_FILE).send_email(
        email.recipient,
        email.sender,
        email.body,
        email.subject)
    if not result:
        logger.log_error("Error sending message")
        return json.dumps({
            'statusCode': 500,
            'error': err})
    return json.dumps({
        'statusCode': 200,
        'error': ''})


@app.post("/meeting/create_event")
async def create_event(event: NewEvent):
    """
    Create a Google Meet event.

    Request: POST
    Body: {'summary': str ,
           'attendees': list,
           'start': str,
           'end': str,
           'timezone': str,
           'calendar_id': optional[str],
           'location': optional[str]
    }
    Returns {'statusCode': , 'error': error msg}
    """
    logger.log_info("New event creation request received: {}".format(event))
    result, err = meeting_helper.MeetingHandler(Auth.CREDENTIALS_FILE)\
        .create_event(event.calendar_id, event.summary, event.attendees,
                      event.start, event.end, event.timezone, event.location)

    if not result:
        logger.log_error("Error creating event")
        return json.dumps({
            'statusCode': 500,
            'error': err})
    return json.dumps({
        'statusCode': 200,
        'error': ''})


@app.post("/meeting/delete_event")
async def delete_event(event: Event):
    """
    Create a Google Meet event.

    Request: POST
    Body: {'summary': str ,
           'calendar_id': optional[str],
    }
    Returns {'statusCode': , 'error': error msg}
    """
    logger.log_info("New event deletion request received: {}".format(event))
    result, err = meeting_helper.MeetingHandler(Auth.CREDENTIALS_FILE)\
        .delete_event(event.calendar_id, event.summary)

    if not result:
        logger.log_error("Error deleting event")
        return json.dumps({
            'statusCode': 500,
            'error': err})
    return json.dumps({
        'statusCode': 200,
        'error': ''})