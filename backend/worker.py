"""Email worker - processes emails and extracts links"""
import imaplib
import email
import re
from bs4 import BeautifulSoup
from datetime import datetime
import os
import signal
import sys
from pathlib import Path
import time

# Add paths for imports
current_dir = Path(__file__).parent
project_root = current_dir.parent

if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Try imports with backend prefix first, fallback to direct imports
try:
    from backend.utils.database import get_raw_connection
    from backend.config import settings
    from backend.utils.link_preview import fetch_link_preview
except ImportError:
    from utils.database import get_raw_connection
    from config import settings
    from utils.link_preview import fetch_link_preview

# Try PostgreSQL, fallback to SQLite
try:
    import psycopg2
    USE_POSTGRES = True
except ImportError:
    USE_POSTGRES = False
    import sqlite3

def init_database():
    """Create database tables if they don't exist"""
    conn = get_raw_connection()
    cursor = conn.cursor()
    
    if USE_POSTGRES and settings.database_url and not settings.database_url.startswith('sqlite'):
        # Check if feed_items exists, if not create with old schema
        cursor.execute('''
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'feed_items'
            );
        ''')
        exists = cursor.fetchone()[0]
        
        if not exists:
            cursor.execute('''
                CREATE TABLE feed_items (
                    id SERIAL PRIMARY KEY,
                    sender_email TEXT NOT NULL,
                    core_link TEXT NOT NULL,
                    received_date TIMESTAMP NOT NULL,
                    processed_date TIMESTAMP NOT NULL,
                    preview_title TEXT,
                    preview_description TEXT,
                    preview_image_url TEXT,
                    preview_site_name TEXT,
                    preview_fetched_at TIMESTAMP,
                    user_id INTEGER,
                    UNIQUE(sender_email, core_link, received_date)
                )
            ''')
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feed_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_email TEXT NOT NULL,
                core_link TEXT NOT NULL,
                received_date TEXT NOT NULL,
                processed_date TEXT NOT NULL,
                preview_title TEXT,
                preview_description TEXT,
                preview_image_url TEXT,
                preview_site_name TEXT,
                preview_fetched_at TEXT,
                user_id INTEGER,
                UNIQUE(sender_email, core_link, received_date)
            )
        ''')
    
    conn.commit()
    conn.close()
    print(f"✅ Database initialized ({'PostgreSQL' if USE_POSTGRES and settings.database_url and not settings.database_url.startswith('sqlite') else 'SQLite'})")

def save_to_database(sender_email, core_link, received_date):
    """Save feed item to database (just the link, no preview data)"""
    conn = get_raw_connection()
    cursor = conn.cursor()
    
    try:
        if USE_POSTGRES and settings.database_url and not settings.database_url.startswith('sqlite'):
            cursor.execute('''
                INSERT INTO feed_items (
                    sender_email, core_link, received_date, processed_date
                )
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (sender_email, core_link, received_date) DO NOTHING
            ''', (
                sender_email, core_link, received_date, datetime.now()
            ))
        else:
            cursor.execute('''
                INSERT INTO feed_items (
                    sender_email, core_link, received_date, processed_date
                )
                VALUES (?, ?, ?, ?)
            ''', (
                sender_email, core_link, received_date, datetime.now().isoformat()
            ))
        
        conn.commit()
        rows_affected = cursor.rowcount
        
        if rows_affected > 0:
            print(f"✅ Saved: {core_link} from {sender_email}")
            return True
        else:
            print(f"⚠️ Duplicate: {core_link} from {sender_email}")
            return False
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    finally:
        conn.close()

def connect_to_gmail():
    """Connect to Gmail"""
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(settings.gmail_user, settings.gmail_password)
    return imap

def extract_sender_email(from_field):
    """Extract clean email address from From field"""
    match = re.search(r'<(.+?)>', from_field)
    return match.group(1) if match else from_field.strip()

def extract_urls_from_email(message):
    """Extract all URLs from email"""
    urls = []
    text_content = ""
    html_content = ""
    
    if message.is_multipart():
        for part in message.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            
            if "attachment" not in content_disposition:
                if content_type == "text/plain":
                    text_content = part.get_payload(decode=True).decode(errors='ignore')
                elif content_type == "text/html":
                    html_content = part.get_payload(decode=True).decode(errors='ignore')
    else:
        content = message.get_payload(decode=True).decode(errors='ignore')
        if message.get_content_type() == "text/html":
            html_content = content
        else:
            text_content = content
    
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    
    if text_content:
        urls.extend(re.findall(url_pattern, text_content))
    
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        for link in soup.find_all('a', href=True):
            urls.append(link['href'])
        urls.extend(re.findall(url_pattern, html_content))
    
    # Deduplicate
    seen = set()
    unique_urls = []
    for url in urls:
        clean_url = url.rstrip('>')
        if clean_url not in seen and clean_url.startswith('http'):
            seen.add(clean_url)
            unique_urls.append(clean_url)
    
    return unique_urls

def get_primary_url(urls):
    """Get primary URL by filtering junk"""
    if not urls:
        return None
    
    junk_patterns = [
        r'apps\.apple\.com',
        r'play\.google\.com',
        r'onelink\.me',
        r'app\.link',
        r'/download',
        r'cdnjs\.cloudflare\.com',
        r'ea\.twimg\.com',
        r'pbs\.twimg\.com/profile',
        r'\.(png|jpg|jpeg|gif|svg|ico|css|js)(\?|$)',
        r'/pixel',
        r'google-analytics\.com',
        r'doubleclick\.net',
    ]
    
    for url in urls:
        is_junk = any(re.search(pattern, url, re.IGNORECASE) for pattern in junk_patterns)
        if not is_junk:
            return url
    
    return urls[0] if urls else None

def process_unseen_emails():
    """Process all unseen emails and add to database"""
    
    print(f"🔄 Checking emails at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        imap = connect_to_gmail()
        imap.select('"INBOX"')
        
        status, messages = imap.search(None, 'UNSEEN')
        
        if not messages[0]:
            print("   No new emails")
            imap.close()
            imap.logout()
            return 0
        
        email_ids = messages[0].split()
        processed_count = 0
        
        for email_id in email_ids:
            try:
                _, msg_data = imap.fetch(email_id, "(RFC822)")
                message = email.message_from_bytes(msg_data[0][1])
                
                from_field = message.get('From', '')
                sender_email = extract_sender_email(from_field)
                received_date = message.get('Date', datetime.now().isoformat())
                
                urls = extract_urls_from_email(message)
                core_link = get_primary_url(urls)
                
                if core_link:
                    # Just save the link, previews will be fetched on-demand
                    if save_to_database(sender_email, core_link, received_date):
                        processed_count += 1
                
            except Exception as e:
                print(f"❌ Error processing email {email_id}: {e}")
                continue
        
        print(f"✅ Processed {processed_count} new items")
        
        imap.close()
        imap.logout()
        
        return processed_count
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0

def signal_handler(sig, frame):
    """Graceful shutdown"""
    print('\n\n👋 Shutting down gracefully...')
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    print("=" * 80)
    print("🚀 FEED PROCESSOR STARTED")
    print(f"📧 Monitoring: {settings.gmail_user}")
    print(f"⏱️  Check interval: {settings.check_interval} seconds")
    print("=" * 80)
    
    init_database()
    
    while True:
        try:
            process_unseen_emails()
            time.sleep(settings.check_interval)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Fatal error: {e}")
            time.sleep(60)

