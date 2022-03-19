from pydantic import BaseModel
from typing import Optional


class Calendar(BaseModel):
    summary: str


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


class Folder(BaseModel):
    folder_name: str
    parent_name: Optional[str] = ''


class Item(BaseModel):
    file_name: str
    parent_name: Optional[str] = ''


class NewCalendar(Calendar):
    time_zone: str


class NewEvent(BaseModel):
    attendees: list
    start: str
    end: str
    timezone: str
    location: Optional[str] = 'online'


class NewItem(Item):
    content: str


class SharedFolder(Folder):
    email: str
    role: Optional[str] = 'reader'
    notify: Optional[bool] = True
