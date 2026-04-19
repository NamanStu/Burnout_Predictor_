#!/usr/bin/env python3
"""
MongoDB Remote Connection Troubleshooter
Diagnoses connection issues with remote MongoDB
"""

import socket
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_network_connectivity(host, port):
    """Test if we can reach the remote device on the specified port."""
    print(f"\n🔍 Testing network connectivity to {host}:{port}...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ Port {port} is OPEN and accessible")
            return True
        else:
            print(f"❌ Port {port} is CLOSED or BLOCKED")
            print("   → Check firewall settings on remote device")
            print("   → Ensure MongoDB bindIp includes 0.0.0.0")
            return False
    except socket.gaierror:
        print(f"❌ Cannot resolve hostname/IP: {host}")
        print("   → Check if IP address is correct")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_mongodb_connection():
    """Test actual MongoDB connection."""
    print(f"\n🔍 Testing MongoDB connection...")
    try:
        from config import MONGODB_HOST, MONGODB_DB_NAME
        from db.models import init_db, BurnoutSubmission
        
        print(f"   Host: {MONGODB_HOST}")
        print(f"   Database: {MONGODB_DB_NAME}")
        
        init_db(MONGODB_DB_NAME, MONGODB_HOST)
        print(f"✅ Successfully connected to MongoDB!")
        
        # Try to query
        count = BurnoutSubmission.objects.count()
        print(f"✅ Database accessible - {count} submissions found")
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {str(e)[:200]}")
        return False

def main():
    print("=" * 60)
    print("MongoDB Remote Connection Troubleshooter")
    print("=" * 60)
    
    try:
        from config import MONGODB_HOST, MONGODB_DB_NAME
        
        # Extract host and port from connection string
        if "mongodb://" in MONGODB_HOST:
            conn_string = MONGODB_HOST.replace("mongodb://", "").rstrip("/")
            if "@" in conn_string:
                conn_string = conn_string.split("@")[1]
            
            if ":" in conn_string:
                host, port = conn_string.split(":")
                port = int(port)
            else:
                host = conn_string
                port = 27017
        else:
            print("❌ Invalid MongoDB connection string")
            return False
        
        print(f"\n📍 Target: {host}:{port}")
        print(f"🗄️  Database: {MONGODB_DB_NAME}")
        
        # Test 1: Network connectivity
        network_ok = test_network_connectivity(host, port)
        
        # Test 2: MongoDB connection
        print("\n" + "-" * 60)
        mongodb_ok = test_mongodb_connection()
        
        # Summary
        print("\n" + "=" * 60)
        print("TROUBLESHOOTING SUMMARY")
        print("=" * 60)
        
        if network_ok and mongodb_ok:
            print("✅ ALL TESTS PASSED - Connection is working!")
            return True
        
        if not network_ok:
            print("\n⚠️  NETWORK ISSUE:")
            print("   1. Verify remote device IP: 192.168.1.186")
            print("   2. Check firewall allows port 27017")
            print("   3. On remote device, check MongoDB bindIp setting")
            print("\n   Linux/macOS config file:")
            print("   /etc/mongod.conf (Linux) or /usr/local/etc/mongod.conf (macOS)")
            print("\n   Change to:")
            print("   net:")
            print("     bindIp: 0.0.0.0")
        
        if network_ok and not mongodb_ok:
            print("\n⚠️  MONGODB ISSUE:")
            print("   1. Verify MongoDB is running on remote device")
            print("   2. Check MongoDB logs for errors")
            print("   3. Restart MongoDB service:")
            print("      Linux: sudo systemctl restart mongod")
            print("      macOS: brew services restart mongodb-community")
        
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
