from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class TestChatRequest(BaseModel):
    message: str


class TestChatResponse(BaseModel):
    reply: str
    mode: str
    bot_id: int


class BotSettingsUpdate(BaseModel):
    prompt: Optional[str] = None
    model_name: Optional[str] = None  # Provider: openai, gemini, openrouter, qwen
    specific_model_name: Optional[str] = None
    api_key: Optional[str] = None
    temperature: Optional[int] = None  # 0-100 stored as int, converted to float for AI
    language: Optional[str] = None
    custom_responses: Optional[Dict[str, str]] = None
    custom_products: Optional[Any] = None


class BotModeUpdate(BaseModel):
    mode: str  # default, predefined, ai


class BotStatusUpdate(BaseModel):
    status: bool


class BotResponse(BaseModel):
    id: int
    user_id: int
    mode: str
    status: bool
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class SettingsResponse(BaseModel):
    id: int
    bot_id: int
    prompt: Optional[str]
    model_name: str  # Provider: openai, gemini, openrouter, qwen
    specific_model_name: Optional[str]  # Specific model: gpt-4o, gemini-2.0-flash, etc.
    temperature: int
    language: str
    custom_responses: Optional[Dict[str, str]]
    custom_products: Optional[Any]
    has_api_key: bool

    class Config:
        from_attributes = True
