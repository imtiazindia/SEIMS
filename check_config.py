"""
Quick script to check what configuration is being loaded
Run this to diagnose configuration issues
"""

import os
import sys

# Try to import streamlit
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False
    print("⚠ Streamlit not installed (this is OK for testing)")

# Load dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False
    print("⚠ python-dotenv not installed")

print("=" * 60)
print("Configuration Diagnostic")
print("=" * 60)

# Check environment variables
print("\n1. Environment Variables (.env file):")
env_db_url = os.getenv('DATABASE_URL')
env_secret = os.getenv('SECRET_KEY')

if env_db_url:
    # Mask password
    if '@' in env_db_url:
        parts = env_db_url.split('@')
        if '://' in parts[0] and ':' in parts[0].split('://')[1]:
            user = parts[0].split('://')[1].split(':')[0]
            display = f"{parts[0].split('://')[0]}://{user}:***@{'@'.join(parts[1:])}"
        else:
            display = env_db_url
    else:
        display = env_db_url
    print(f"   ✅ DATABASE_URL found: {display}")
else:
    print("   ❌ DATABASE_URL not found in environment")

if env_secret:
    print(f"   ✅ SECRET_KEY found: {env_secret[:20]}...")
else:
    print("   ❌ SECRET_KEY not found in environment")

# Check Streamlit secrets (if available)
if HAS_STREAMLIT:
    print("\n2. Streamlit Secrets:")
    try:
        if hasattr(st, 'secrets'):
            print("   ✅ st.secrets is available")
            
            # Try to access secrets
            try:
                if 'DATABASE_URL' in st.secrets:
                    secret_db_url = st.secrets['DATABASE_URL']
                    # Mask password
                    if '@' in secret_db_url:
                        parts = secret_db_url.split('@')
                        if '://' in parts[0] and ':' in parts[0].split('://')[1]:
                            user = parts[0].split('://')[1].split(':')[0]
                            display = f"{parts[0].split('://')[0]}://{user}:***@{'@'.join(parts[1:])}"
                        else:
                            display = secret_db_url
                    else:
                        display = secret_db_url
                    print(f"   ✅ DATABASE_URL in secrets: {display}")
                else:
                    print("   ❌ DATABASE_URL not found in st.secrets")
                    print(f"   Available keys: {list(st.secrets.keys()) if hasattr(st.secrets, 'keys') else 'N/A'}")
            except Exception as e:
                print(f"   ❌ Error accessing secrets: {e}")
                print(f"   Secrets type: {type(st.secrets)}")
        else:
            print("   ❌ st.secrets not available (not running in Streamlit context)")
    except Exception as e:
        print(f"   ❌ Error checking secrets: {e}")
else:
    print("\n2. Streamlit Secrets:")
    print("   ⚠ Cannot check (Streamlit not available)")

# Test load_config
print("\n3. Testing load_config():")
try:
    from src.config.settings import load_config
    config = load_config()
    
    db_url = config.get('database_url', 'Not set')
    source = config.get('_config_source', 'unknown')
    
    # Mask password
    if db_url != 'Not set' and '@' in db_url:
        parts = db_url.split('@')
        if '://' in parts[0] and ':' in parts[0].split('://')[1]:
            user = parts[0].split('://')[1].split(':')[0]
            display = f"{parts[0].split('://')[0]}://{user}:***@{'@'.join(parts[1:])}"
        else:
            display = db_url
    else:
        display = db_url
    
    print(f"   Database URL: {display}")
    print(f"   Source: {source}")
    
    if 'localhost' in db_url and source != 'environment_variable':
        print("\n   ⚠ WARNING: Using localhost default!")
        print("   This means secrets/env vars are not being read.")
        print("   Solutions:")
        print("   - For local: Create .env file with DATABASE_URL")
        print("   - For Streamlit Cloud: Check secrets configuration")
    
except Exception as e:
    print(f"   ❌ Error loading config: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Diagnostic Complete")
print("=" * 60)


