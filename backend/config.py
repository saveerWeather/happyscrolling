"""Configuration settings"""
import os
import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent))

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    project_root = Path(__file__).parent.parent
    env_path = project_root / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # python-dotenv not installed, that's okay

class Settings:
    """Simple settings class using os.getenv"""
    # Database
    database_url: str = os.getenv('DATABASE_URL', 'sqlite:///feed.db')
    
    # JWT
    jwt_secret: str = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
    jwt_algorithm: str = os.getenv('JWT_ALGORITHM', 'HS256')
    jwt_expiration_hours: int = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))
    
    # CORS - convert string to list
    _cors_origins_str: str = os.getenv('CORS_ORIGINS', 'http://localhost:3000')
    
    @property
    def cors_origins(self) -> List[str]:
        """Convert comma-separated string to list"""
        # Remove trailing slashes and strip whitespace
        origins = [origin.strip().rstrip('/') for origin in self._cors_origins_str.split(',')]
        return origins
    
    # Email worker
    gmail_user: str = os.getenv('GMAIL_USER', 'addtofeed2@gmail.com')
    gmail_password: str = os.getenv('GMAIL_PASSWORD', '')
    check_interval: int = int(os.getenv('CHECK_INTERVAL', '30'))

settings = Settings()

