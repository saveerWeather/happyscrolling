"""Add notes column to feed_items table"""
import sys
from pathlib import Path

# Add backend to path
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from utils.database import engine, DATABASE_URL
from sqlalchemy import text, inspect

def add_notes_column():
    """Add notes column to feed_items table if it doesn't exist"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('feed_items')]

    if 'notes' not in columns:
        print("Adding notes column...")
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE feed_items ADD COLUMN notes TEXT"))
            conn.commit()
        print("✓ Notes column added successfully!")
    else:
        print("✓ Notes column already exists.")

if __name__ == "__main__":
    print(f"Database: {DATABASE_URL}")
    add_notes_column()
