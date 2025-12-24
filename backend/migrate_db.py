"""Migration script to add missing columns to feed_items table"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.utils.database import get_raw_connection, USE_POSTGRES, DATABASE_URL

def migrate_database():
    """Add missing columns to feed_items table if they don't exist"""
    conn = get_raw_connection()
    cursor = conn.cursor()
    
    if USE_POSTGRES and DATABASE_URL and not DATABASE_URL.startswith('sqlite'):
        print("🔄 Migrating PostgreSQL database...")
        
        # Check and add preview columns
        columns_to_add = [
            ('preview_title', 'TEXT'),
            ('preview_description', 'TEXT'),
            ('preview_image_url', 'TEXT'),
            ('preview_site_name', 'TEXT'),
            ('preview_fetched_at', 'TIMESTAMP'),
            ('user_id', 'INTEGER')
        ]
        
        for column_name, column_type in columns_to_add:
            # Check if column exists
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='feed_items' AND column_name=%s
            """, (column_name,))
            
            if not cursor.fetchone():
                print(f"  Adding column: {column_name}")
                cursor.execute(f"ALTER TABLE feed_items ADD COLUMN {column_name} {column_type}")
            else:
                print(f"  Column {column_name} already exists")
        
        conn.commit()
        print("✅ Migration complete!")
    else:
        print("ℹ️  Using SQLite - no migration needed")
    
    conn.close()

if __name__ == "__main__":
    migrate_database()

