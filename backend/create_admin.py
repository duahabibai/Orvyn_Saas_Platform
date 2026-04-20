import sys
import os

# Add parent directory to path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, init_db
from models import User, Bot, BotSettings, Integration, Usage
from services import hash_password
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_super_admin(email, password, full_name="Super Admin"):
    db = SessionLocal()
    try:
        # Check if user already exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            logger.info(f"User {email} already exists. Updating role to super_admin.")
            existing.role = "super_admin"
            existing.password_hash = hash_password(password)
            db.commit()
            logger.info(f"Super Admin updated successfully!")
            return

        # Create new super admin
        user = User(
            email=email,
            password_hash=hash_password(password),
            role="super_admin",
            full_name=full_name,
            plan="growth" # Give super admin the highest plan
        )
        db.add(user)
        db.flush()

        # Create default bot for user
        bot = Bot(user_id=user.id, mode="ai", status=True)
        db.add(bot)
        db.flush()

        # Add related records
        db.add(BotSettings(bot_id=bot.id))
        db.add(Integration(bot_id=bot.id))
        db.add(Usage(user_id=user.id))
        
        db.commit()
        logger.info(f"Super Admin created successfully!")
        logger.info(f"Email: {email}")
        logger.info(f"Password: {password}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create Super Admin: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Create a Super Admin user.")
    parser.add_argument("--email", required=True, help="Admin email")
    parser.add_argument("--password", required=True, help="Admin password")
    args = parser.parse_args()
    
    create_super_admin(args.email, args.password)
