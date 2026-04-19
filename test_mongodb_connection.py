#!/usr/bin/env python3
"""
Test MongoDB Connection Script
Run this to verify your MongoDB connection is working
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_connection():
    """Test MongoDB connection with detailed diagnostics."""
    
    print("=" * 60)
    print("MongoDB Connection Tester")
    print("=" * 60)
    
    try:
        # Load configuration
        from config import MONGODB_HOST, MONGODB_DB_NAME
        
        print(f"\n✓ Configuration loaded")
        print(f"  Database: {MONGODB_DB_NAME}")
        
        # Mask password if present
        display_host = MONGODB_HOST
        if '@' in MONGODB_HOST:
            parts = MONGODB_HOST.split('@')
            creds = parts[0].replace('mongodb://', '')
            rest = parts[1]
            display_host = f"mongodb://***:***@{rest}"
        
        print(f"  Connection String: {display_host}")
        
        print(f"\n⏳ Attempting connection...")
        
        # Attempt connection
        from db.models import init_db
        init_db(MONGODB_DB_NAME, MONGODB_HOST)
        
        print(f"✓ Successfully connected to MongoDB!")
        
        # Try to access the database
        from db.models import BurnoutSubmission
        count = BurnoutSubmission.objects.count()
        print(f"✓ Database accessible")
        print(f"  Total submissions in database: {count}")
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED - Connection is working!")
        print("=" * 60)
        return True
        
    except ConnectionError as e:
        print(f"\n✗ Connection Error: {e}")
        print("\n🔍 Troubleshooting:")
        print("   1. Verify remote device IP address is correct")
        print("   2. Check MongoDB is running on remote device")
        print("   3. Verify firewall allows port 27017")
        print("   4. Check username/password if using authentication")
        print("   5. Test connectivity: ping <remote-ip>")
        return False
        
    except Exception as e:
        print(f"\n✗ Error: {type(e).__name__}: {e}")
        print("\n🔍 Additional info:")
        print(f"   - Check .env file exists and is properly configured")
        print(f"   - Verify python-dotenv is installed: pip install python-dotenv")
        print(f"   - Check MongoEngine is installed: pip install mongoengine")
        return False

def show_setup_instructions():
    """Show setup instructions."""
    print("\n" + "=" * 60)
    print("Quick Setup Instructions")
    print("=" * 60)
    
    print("\n1. Copy .env configuration:")
    print("   cp .env.example .env")
    
    print("\n2. Edit .env with your MongoDB details:")
    print("   nano .env")
    
    print("\n3. Example configurations:")
    print("   Local:    MONGODB_HOST=mongodb://localhost:27017/")
    print("   Remote:   MONGODB_HOST=mongodb://192.168.1.100:27017/")
    print("   Auth:     MONGODB_HOST=mongodb://user:pass@192.168.1.100:27017/")
    print("   Atlas:    MONGODB_HOST=mongodb+srv://user:pass@cluster0.xxxx.mongodb.net/")
    
    print("\n4. Run test again:")
    print("   python3 test_mongodb_connection.py")

if __name__ == '__main__':
    # Check if .env exists
    env_path = Path(__file__).parent / '.env'
    if not env_path.exists():
        print("⚠ .env file not found!")
        print("Creating .env from template...")
        example_path = Path(__file__).parent / '.env.example'
        if example_path.exists():
            with open(example_path, 'r') as f:
                content = f.read()
            with open(env_path, 'w') as f:
                f.write(content)
            print("✓ .env file created from template")
            print("⚠ Please edit .env with your MongoDB connection details")
            show_setup_instructions()
            sys.exit(1)
    
    # Run test
    success = test_connection()
    
    if not success:
        show_setup_instructions()
        sys.exit(1)
    
    sys.exit(0)
