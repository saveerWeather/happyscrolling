"""Create email verification and password reset token tables"""
import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent.resolve()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from sqlalchemy import text
from utils.database import engine, Base
from models import EmailVerificationToken, PasswordResetToken

def create_token_tables():
    """Create token tables if they don't exist"""
    print("Creating token tables...")
    Base.metadata.create_all(bind=engine, tables=[
        EmailVerificationToken.__table__,
        PasswordResetToken.__table__
    ])
    print("✓ Token tables created successfully")

if __name__ == "__main__":
    create_token_tables()
