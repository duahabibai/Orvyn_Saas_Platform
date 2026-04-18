"""
Migration: Add plan column to users table.
Run this once to add plan column for existing users.
All existing users default to 'starter' plan.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import models FIRST to register them with Base
import models
from database import engine, SessionLocal, Base, init_db
from sqlalchemy import text

def migrate():
    """Add plan column to users table."""
    # First ensure tables exist
    print("Initializing database tables...")
    init_db()

    db = SessionLocal()
    try:
        # Check if column already exists
        result = db.execute(text(
            "PRAGMA table_info(users)"
        )).fetchall()

        columns = [row[1] for row in result]

        if "plan" in columns:
            print("[OK] 'plan' column already exists in users table")
            return True

        # Add plan column with default value
        db.execute(text(
            "ALTER TABLE users ADD COLUMN plan VARCHAR(20) DEFAULT 'starter'"
        ))
        db.commit()

        print("[OK] Migration successful: 'plan' column added to users table")
        print("    All existing users set to 'starter' plan")
        return True

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Migration failed: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
