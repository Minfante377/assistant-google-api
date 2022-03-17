from pydantic import BaseModel
from typing import Optional


class Email(BaseModel):
    recipient: str
    sender: str
    body: str
    subcject: str
    attachement: Optional[str] = ''
    extension: Optional[str] = '.pdf'


class Event(BaseModel):
    summary: str
    calendar_id: Optional[str] = 'primary'


class NewEvent(BaseModel):
    attendees: list
    start: str
    end: str
    timezone: str
    location: Optional[str] = 'online'
