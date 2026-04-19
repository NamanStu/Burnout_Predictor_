"""
Configuration for MongoDB connections
Supports both local and remote connections via environment variables
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ── MongoDB Connection Settings ──────────────────────
# Default: Local MongoDB (localhost)
# For remote: Set these in .env file or environment variables

MONGODB_HOST = os.getenv(
    'MONGODB_HOST',
    'mongodb://localhost:27017/'  # Default to local
)

MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'burnout_db')

# Connection timeout (milliseconds)
CONNECTION_TIMEOUT = int(os.getenv('CONNECTION_TIMEOUT', '5000'))

# ── Current Configuration Info ──────────────────────
print(f"[MongoDB Config] Using: {MONGODB_HOST.split('@')[-1] if '@' in MONGODB_HOST else MONGODB_HOST}")
print(f"[MongoDB Config] Database: {MONGODB_DB_NAME}")
