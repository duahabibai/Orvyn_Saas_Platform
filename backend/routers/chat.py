from fastapi import APIRouter, Depends, Query, Request, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from database import get_db
from models import Message, Lead, Bot
from schemas.chat import MessageOut, LeadOut
from services import decode_token

router = APIRouter(prefix="/api", tags=["chat", "leads"])


def get_current_user_id(request: Request) -> int:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "Not authenticated")
    payload = decode_token(auth[7:])
    if not payload:
        raise HTTPException(401, "Invalid token")
    return int(payload.get("sub", 0))


@router.get("/chats", response_model=list[MessageOut])
def get_chats(
    phone_number: str = Query(None),
    limit: int = Query(50, le=500),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    q = db.query(Message).join(Message.bot).filter(Bot.user_id == user_id)
    if phone_number:
        q = q.filter(Message.phone_number == phone_number)
    return q.order_by(desc(Message.timestamp)).limit(limit).all()


@router.get("/messages/{bot_id}", response_model=list[MessageOut])
def get_messages_by_bot(
    bot_id: int,
    limit: int = Query(100, le=500),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    bot = db.query(Bot).filter(Bot.id == bot_id, Bot.user_id == user_id).first()
    if not bot:
        raise HTTPException(404, "Bot not found")
    return (db.query(Message).filter(Message.bot_id == bot_id)
            .order_by(desc(Message.timestamp))
            .limit(limit).all())


@router.get("/leads", response_model=list[LeadOut])
def get_leads(
    limit: int = Query(50, le=500),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    leads = (db.query(Lead).join(Lead.bot)
            .filter(Bot.user_id == user_id)
            .order_by(desc(Lead.updated_at))
            .limit(limit).all())
    
    # Add message_count to each lead
    for lead in leads:
        msg_count = db.query(func.count(Message.id)).filter(
            Message.bot_id == lead.bot_id,
            Message.phone_number == lead.phone
        ).scalar()
        lead.message_count = msg_count or 0
    
    return leads
