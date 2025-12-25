"""Add display_name column to users table"""
import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent.resolve()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from sqlalchemy import text
from utils.database import engine

def add_display_name_column():
    """Add display_name column to users table if it doesn't exist"""
    with engine.connect() as conn:
        # Check if column exists
        check_query = text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='users' AND column_name='display_name';
        """)

        result = conn.execute(check_query)
        exists = result.fetchone() is not None

        if not exists:
            print("Adding display_name column to users table...")
            alter_query = text("""
                ALTER TABLE users
                ADD COLUMN display_name VARCHAR NULL;
            """)
            conn.execute(alter_query)
            conn.commit()
            print("✓ display_name column added successfully")
        else:
            print("display_name column already exists")

if __name__ == "__main__":
    add_display_name_column()
