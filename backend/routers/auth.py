from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import User, Bot, BotSettings, Integration, Usage
from schemas.auth import UserCreate, UserLogin, TokenResponse, UserOut
from services import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RefreshRequest(BaseModel):
    refresh_token: str


def get_current_user_id(request: Request) -> int:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "Not authenticated")
    payload = decode_token(auth[7:])
    if not payload:
        raise HTTPException(401, "Invalid token")
    return int(payload.get("sub", 0))


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    user_id = get_current_user_id(request)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(401, "User not found")
    return user


def admin_required(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(403, "Admin access required")
    return user


@router.post("/signup", response_model=TokenResponse)
async def signup(data: UserCreate, request: Request, db: Session = Depends(get_db)): # Added request and async
    logger.info(f"Received signup request from {request.client.host} for email: {data.email}")
    try:
        existing = db.query(User).filter(User.email == data.email).first()
        if existing:
            logger.warning(f"Signup attempt for existing email: {data.email}")
            raise HTTPException(400, "Email already registered")

        user = User(
            email=data.email,
            password_hash=hash_password(data.password),
            role="user",  # Explicitly set default role
            full_name=data.full_name
        )
        db.add(user)
        db.flush()

        # Create default bot for user
        bot = Bot(user_id=user.id, mode="default", status=True)
        db.add(bot)
        db.flush()

        bs = BotSettings(bot_id=bot.id)
        integ = Integration(bot_id=bot.id)
        usage = Usage(user_id=user.id)
        db.add(bs)
        db.add(integ)
        db.add(usage)
        db.commit()
        db.refresh(user)

        logger.info(f"User {user.id} ({data.email}) signed up successfully.")
        return TokenResponse(
            access_token=create_access_token({"sub": str(user.id)}),
            refresh_token=create_refresh_token({"sub": str(user.id)}),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup failed for email {data.email}: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Signup failed: {str(e)}")


def get_plan_limits(plan: str) -> dict:
    """Get usage limits based on user plan."""
    if plan == "growth":
        return {
            "whatsapp_limit": 1500,
            "ai_limit": 1500,
            "custom_responses_limit": -1,  # unlimited
            "custom_products_limit": -1,  # unlimited
            "automation_rules": -1,  # unlimited
        }
    else:  # starter
        return {
            "whatsapp_limit": 200,
            "ai_limit": 200,
            "custom_responses_limit": 10,
            "custom_products_limit": 10,
            "automation_rules": 5,
        }


@router.get("/usage")
async def get_usage(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)): # Added async
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    usage = db.query(Usage).filter(Usage.user_id == user_id).first()
    if not usage:
        # Create it if it doesn't exist (for existing users)
        logger.info(f"Usage record not found for user {user_id}, creating a new one.")
        usage = Usage(user_id=user_id)
        db.add(usage)
        db.commit()
        db.refresh(usage)

    # Apply plan-based limits
    limits = get_plan_limits(user.plan)
    usage.whatsapp_limit = limits["whatsapp_limit"]
    usage.ai_limit = limits["ai_limit"]

    return {
        "whatsapp_messages_sent": usage.whatsapp_messages_sent,
        "whatsapp_limit": usage.whatsapp_limit,
        "ai_requests_made": usage.ai_requests_made,
        "ai_limit": usage.ai_limit,
        "plan": user.plan,
    }


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, request: Request, db: Session = Depends(get_db)): # Added request and async
    logger.info(f"Received login request from {request.client.host} for email: {data.email}")
    try:
        user = db.query(User).filter(User.email == data.email).first()
        if not user or not verify_password(data.password, user.password_hash):
            logger.warning(f"Login failed for email {data.email}: Invalid credentials.")
            raise HTTPException(401, "Invalid credentials")

        logger.info(f"User {user.id} ({data.email}) logged in successfully.")
        return TokenResponse(
            access_token=create_access_token({"sub": str(user.id)}),
            refresh_token=create_refresh_token({"sub": str(user.id)}),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed for email {data.email}: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Login failed: {str(e)}")


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest, request: Request, db: Session = Depends(get_db)): # Added request and async
    logger.info(f"Received refresh token request from {request.client.host}.")
    payload = decode_token(data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        logger.warning(f"Refresh token failed: Invalid token type or payload. Token: {data.refresh_token[:10]}...") # Log first 10 chars of token
        raise HTTPException(401, "Invalid refresh token")

    user_id = payload.get("sub")
    if not user_id:
        logger.warning(f"Refresh token failed: No user ID found in payload. Token: {data.refresh_token[:10]}...")
        raise HTTPException(401, "Invalid refresh token payload")
    
    try:
        user = db.query(User).filter(User.id == int(user_id)).first() # Ensure user_id is int
        if not user:
            logger.warning(f"Refresh token failed: User not found for id {user_id}.")
            raise HTTPException(401, "User not found")

        logger.info(f"User {user.id} ({user.email}) token refreshed successfully.")
        return TokenResponse(
            access_token=create_access_token({"sub": str(user.id)}),
            refresh_token=create_refresh_token({"sub": str(user.id)}),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Refresh token failed for user {user_id}: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Token refresh failed: {str(e)}")


@router.get("/me", response_model=UserOut)
async def get_me(user: User = Depends(get_current_user)): # Added async
    return user


# --- ADMIN ENDPOINTS ---

@router.get("/admin/users", response_model=list[UserOut])
async def get_all_users(admin: User = Depends(admin_required), db: Session = Depends(get_db)): # Added async
    """Admin only: list all users."""
    logger.info(f"Admin user {admin.id} requested all users.")
    return db.query(User).all()


class PlanUpdateRequest(BaseModel):
    plan: str  # "starter" or "growth"


class PlanChangeRequest(BaseModel):
    pass  # No body needed, just a POST request


@router.delete("/admin/users/{user_id}")
async def delete_user(user_id: int, admin: User = Depends(admin_required), db: Session = Depends(get_db)): # Added async
    """Admin only: delete a user and their data."""
    logger.info(f"Admin user {admin.id} attempting to delete user {user_id}.")
    if user_id == admin.id:
        raise HTTPException(400, "Cannot delete yourself")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"Admin user {admin.id}: User {user_id} not found for deletion.")
        raise HTTPException(404, "User not found")

    db.delete(user)
    db.commit()
    logger.info(f"Admin user {admin.id} successfully deleted user {user_id}.")
    return {"status": "ok", "message": f"User {user_id} deleted"}


@router.patch("/admin/users/{user_id}/plan")
async def update_user_plan(
    user_id: int,
    data: PlanUpdateRequest,
    admin: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Admin only: change user's plan (starter/growth)."""
    logger.info(f"Admin user {admin.id} attempting to update plan for user {user_id}.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"Admin user {admin.id}: User {user_id} not found for plan update.")
        raise HTTPException(404, "User not found")

    if data.plan not in ("starter", "growth"):
        raise HTTPException(400, "Invalid plan. Must be 'starter' or 'growth'")

    old_plan = user.plan
    user.plan = data.plan
    db.commit()

    logger.info(f"Admin user {admin.id} updated user {user_id} plan from '{old_plan}' to '{user.plan}'.")
    return {
        "status": "ok",
        "user_id": user_id,
        "old_plan": old_plan,
        "new_plan": user.plan,
    }


@router.patch("/admin/users/{user_id}/status")
async def toggle_bot_status(user_id: int, admin: User = Depends(admin_required), db: Session = Depends(get_db)): # Added async
    """Admin only: activate/deactivate user's bot."""
    logger.info(f"Admin user {admin.id} attempting to toggle bot status for user {user_id}.")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.bot:
        logger.warning(f"Admin user {admin.id}: User {user_id} or their bot not found to toggle status.")
        raise HTTPException(404, "User or bot not found")
    
    user.bot.status = not user.bot.status
    db.commit()
    logger.info(f"Admin user {admin.id} toggled bot status for user {user_id}. New status: {user.bot.status}")
    return {"status": "ok", "is_active": user.bot.status}


@router.get("/admin/stats")
async def get_admin_stats(admin: User = Depends(admin_required), db: Session = Depends(get_db)): # Added async
    """Admin only: platform usage stats."""
    logger.info(f"Admin user {admin.id} requested admin stats.")
    from models import Message, Lead
    total_users = db.query(User).count()
    total_messages = db.query(Message).count()
    total_leads = db.query(Lead).count()

    return {
        "total_users": total_users,
        "total_messages": total_messages,
        "total_contacts": total_leads,
        "platform": "ORVYN"
    }


@router.post("/upgrade-plan")
async def upgrade_plan(
    request: PlanChangeRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upgrade from Starter to Growth plan."""
    logger.info(f"User {user.id} attempting to upgrade plan from {user.plan} to growth.")

    if user.plan == "growth":
        raise HTTPException(400, "Already on Growth plan")

    if user.plan != "starter":
        raise HTTPException(400, "Invalid plan for upgrade")

    # Update user plan
    user.plan = "growth"

    # Update usage limits
    usage = db.query(Usage).filter(Usage.user_id == user.id).first()
    if usage:
        usage.whatsapp_limit = 1500
        usage.ai_limit = 1500
        db.commit()
        db.refresh(usage)

    logger.info(f"User {user.id} successfully upgraded to Growth plan.")
    return {
        "status": "ok",
        "message": "Successfully upgraded to Growth plan",
        "new_plan": "growth"
    }


@router.post("/downgrade-plan")
async def downgrade_plan(
    request: PlanChangeRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Downgrade from Growth to Starter plan."""
    logger.info(f"User {user.id} attempting to downgrade plan from {user.plan} to starter.")

    if user.plan == "starter":
        raise HTTPException(400, "Already on Starter plan")

    if user.plan != "growth":
        raise HTTPException(400, "Invalid plan for downgrade")

    # Update user plan
    user.plan = "starter"

    # Update usage limits
    usage = db.query(Usage).filter(Usage.user_id == user.id).first()
    if usage:
        usage.whatsapp_limit = 200
        usage.ai_limit = 200
        db.commit()
        db.refresh(usage)

    logger.info(f"User {user.id} successfully downgraded to Starter plan.")
    return {
        "status": "ok",
        "message": "Successfully downgraded to Starter plan",
        "new_plan": "starter"
    }
