"""
Test database connection script
Run this to verify your database connection is working correctly.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection():
    """Test database connection"""
    print("=" * 60)
    print("Database Connection Test")
    print("=" * 60)
    
    # Check for DATABASE_URL
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("\n❌ ERROR: DATABASE_URL not found!")
        print("\nPlease create a .env file with your DATABASE_URL:")
        print("\nExample:")
        print("  DATABASE_URL=postgresql://user:password@host:port/database")
        print("\nFor cloud databases (Supabase/Railway):")
        print("  DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.xxxxx.supabase.co:5432/postgres")
        print("\nSee DATABASE_SETUP.md for detailed instructions.")
        return False
    
    # Mask password in URL for display
    display_url = database_url
    if '@' in database_url:
        parts = database_url.split('@')
        if ':' in parts[0]:
            user_pass = parts[0].split('://')[1] if '://' in parts[0] else parts[0]
            if ':' in user_pass:
                user = user_pass.split(':')[0]
                display_url = database_url.split('://')[0] + '://' + user + ':***@' + '@'.join(parts[1:])
    
    print(f"\n✓ DATABASE_URL found: {display_url}")
    
    # Try to import and test connection
    try:
        from src.database.connection import get_db_session, _get_engine
        
        # Check if engine can be initialized
        db_engine, _ = _get_engine()
        if db_engine is None:
            print("\n❌ ERROR: Database engine not initialized")
            return False
        
        print("\nAttempting to connect to database...")
        
        with get_db_session() as session:
            # Test query
            result = session.execute("SELECT version();")
            version = result.scalar()
            print(f"\n✅ SUCCESS! Connected to database")
            print(f"   PostgreSQL version: {version.split(',')[0]}")
            
            # Test if tables exist
            result = session.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                LIMIT 5;
            """)
            tables = [row[0] for row in result]
            
            if tables:
                print(f"\n✓ Found {len(tables)} table(s): {', '.join(tables)}")
            else:
                print("\n⚠ WARNING: No tables found. You may need to run database migrations.")
                print("   See DATABASE_SETUP.md for instructions.")
            
            return True
            
    except ImportError as e:
        print(f"\n❌ ERROR: Could not import database modules: {e}")
        print("   Make sure you're running from the project root directory.")
        return False
    except ConnectionError as e:
        print(f"\n❌ CONNECTION ERROR:")
        print(f"   {str(e)}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
        return False

def check_postgresql_running():
    """Check if PostgreSQL is running locally (Windows)"""
    import subprocess
    
    print("\n" + "=" * 60)
    print("Checking if PostgreSQL is running locally...")
    print("=" * 60)
    
    try:
        # Try to connect to PostgreSQL on default port
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 5432))
        sock.close()
        
        if result == 0:
            print("✓ PostgreSQL appears to be running on localhost:5432")
            return True
        else:
            print("❌ PostgreSQL is NOT running on localhost:5432")
            print("\nTo start PostgreSQL on Windows:")
            print("  1. Open Services (Win+R, type 'services.msc')")
            print("  2. Find 'postgresql-x64-XX' service")
            print("  3. Right-click and select 'Start'")
            print("\nOr use a cloud database (Supabase/Railway) - see DATABASE_SETUP.md")
            return False
    except Exception as e:
        print(f"⚠ Could not check PostgreSQL status: {e}")
        return False

if __name__ == "__main__":
    # Check if PostgreSQL is running (for local setups)
    database_url = os.getenv('DATABASE_URL', '')
    if 'localhost' in database_url or '127.0.0.1' in database_url:
        check_postgresql_running()
    
    # Test connection
    success = test_connection()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Database connection test PASSED!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("❌ Database connection test FAILED!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Review DATABASE_SETUP.md for setup instructions")
        print("2. Verify your DATABASE_URL is correct")
        print("3. For local PostgreSQL: Make sure the service is running")
        print("4. For cloud databases: Verify your connection string")
        sys.exit(1)

