from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MessageOut(BaseModel):
    id: int
    bot_id: int
    sender: str
    phone_number: str
    message: Optional[str]
    timestamp: Optional[datetime]

    class Config:
        from_attributes = True


class LeadOut(BaseModel):
    id: int
    bot_id: int
    phone: str
    name: Optional[str]
    last_message: Optional[str]
    message_count: int = 0
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
