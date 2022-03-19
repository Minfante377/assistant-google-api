import base64
import json
import os
import tempfile

from fastapi import FastAPI, HTTPException, status

from helpers import email_helper, meeting_helper, storage_helper
from models import Calendar, Email, Event, Folder, Item,  NewCalendar,\
    NewEvent, NewItem
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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=err)
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=err)


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
    """
    logger.log_info("New event creation request received: {}".format(event))
    result, err = meeting_helper.MeetingHandler(Auth.CREDENTIALS_FILE)\
        .create_event(event.calendar_id, event.summary, event.attendees,
                      event.start, event.end, event.timezone, event.location)

    if not result:
        logger.log_error("Error creating event")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=err)


@app.post("/meeting/delete_event")
async def delete_event(event: Event):
    """
    Create a Google Meet event.

    Request: POST
    Body: {'summary': str ,
           'calendar_id': optional[str],
    }
    """
    logger.log_info("New event deletion request received: {}".format(event))
    result, err = meeting_helper.MeetingHandler(Auth.CREDENTIALS_FILE)\
        .delete_event(event.calendar_id, event.summary)

    if not result:
        logger.log_error("Error deleting event")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=err)


@app.post("/meeting/create_calendar")
async def create_calendar(calendar: NewCalendar):
    """
    Create Google Calendar calendar.

    Request: POST
    Body: {'summary': str,
           'time_zone': str
    }
    """
    logger.log_info("New calendar creation request received: {}"
                    .format(calendar))
    result, err = meeting_helper.MeetingHandler(Auth.CREDENTIALS_FILE)\
        .create_calendar(calendar.summary, calendar.time_zone)

    if not result:
        logger.log_error("Error creating calendar")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=err)


@app.post("/meeting/delete_calendar")
async def delete_calendar(calendar: Calendar):
    """
    Delete Google Calendar calendar.

    Request: POST
    Body: {'summary': str,
    }
    """
    logger.log_info("New calendar deletion request received: {}"
                    .format(calendar))
    result, err = meeting_helper.MeetingHandler(Auth.CREDENTIALS_FILE)\
        .delete_calendar(calendar.summary)

    if not result:
        logger.log_error("Error deleting calendar")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=err)


@app.post("/meeting/get_calendar_id")
async def get_calendar_id(calendar: Calendar):
    """
    Get calendar ID by syntax.

    Request: POST
    Body: {'summary': str,
    }
    Returns {'calendar_id':}
    """
    logger.log_info("Get Calendar ID request received: {}".format(calendar))
    result, calendar_id = meeting_helper.MeetingHandler(Auth.CREDENTIALS_FILE)\
        .get_calendar_id(calendar.summary)

    if not result:
        logger.log_error("Error fetching calendar ID")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=calendar_id)
    return json.dumps({
        'calendar_id': calendar_id})


@app.post("/storage/create_item")
async def create_item(item: NewItem):
    """
    Create Item on Google Drive.

    Request: POST
    Body: {
        'file_name': str,
        'content' bytes,
        'parent_name': optinal[str]
    }
    """
    logger.log_info("Create file request received: {}".format(item))
    suffix = ".{}".format(item.file_name.split('.', 1)[-1])
    f = tempfile.NamedTemporaryFile(suffix=suffix)
    data = base64.b64decode(item.content)
    f.write(data)
    os.link(f.name, item.file_name)
    result, err = storage_helper.StorageHandler(Auth.CREDENTIALS_FILE)\
        .create_file(item.file_name, item.parent_name)
    os.remove(item.file_name)
    if not result:
        logger.log_error("Error creating file: {}".format(err))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=err)


@app.post("/storage/delete_item")
async def delete_item(item: Item):
    """
    Delete Item on Google Drive using its name.

    Request: POST
    Body: {
        'file_name': str,
        'parent_name': optional[str]
    """
    logger.log_info("Delete file request received: {}".format(item))
    result, err = storage_helper.StorageHandler(Auth.CREDENTIALS_FILE)\
        .delete_file(item.file_name, item.parent_name)
    if not result:
        logger.log_error("Error deleting file: {}".format(err))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=err)


@app.post("/storage/create_folder")
async def create_folder(folder: Folder):
    """
    Create Folder on Google Drive.

    Request: POST
    Body: {
        'folder_name': str,
        'parent_name': optinal[str]
    }
    """
    logger.log_info("Create folder request received: {}".format(folder))
    result, err = storage_helper.StorageHandler(Auth.CREDENTIALS_FILE)\
        .create_folder(folder.folder_name, folder.parent_name)
    if not result:
        logger.log_error("Error creating folder: {}".format(err))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=err)


@app.post("/storage/delete_folder")
async def delete_folder(folder: Folder):
    """
    Delete Folder on Google Drive.

    Request: POST
    Body: {
        'folder_name': str,
        'parent_name': optinal[str]
    }
    """
    logger.log_info("Delete folder request received: {}".format(folder))
    result, err = storage_helper.StorageHandler(Auth.CREDENTIALS_FILE)\
        .delete_folder(folder.folder_name, folder.parent_name)
    if not result:
        logger.log_error("Error deleting folder: {}".format(err))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=err)
