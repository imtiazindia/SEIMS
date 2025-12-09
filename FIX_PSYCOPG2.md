# Fix psycopg2-binary Installation Error on Windows

## The Problem
`psycopg2-binary` is trying to build from source instead of using the pre-built binary wheel, which requires PostgreSQL development tools that aren't installed.

## Solution 1: Force Binary Installation (Easiest)

Try installing with the `--only-binary` flag:

```powershell
pip install --only-binary :all: psycopg2-binary
```

Then install the rest:
```powershell
pip install -r requirements.txt --no-deps
pip install streamlit streamlit-authenticator streamlit-option-menu sqlalchemy alembic bcrypt python-jose passlib pandas numpy plotly matplotlib reportlab weasyprint jinja2 Pillow python-multipart python-dateutil pytz python-dotenv pyyaml requests
```

## Solution 2: Install Pre-built Wheel Directly

Download and install a pre-built wheel:

```powershell
pip install https://files.pythonhosted.org/packages/[find-latest-psycopg2-binary-wheel]
```

Or try:
```powershell
pip install psycopg2-binary --prefer-binary
```

## Solution 3: Use Alternative Package

Replace `psycopg2-binary` with `psycopg2` (but this still needs build tools) or use `pg8000` as an alternative:

Update `requirements.txt` to use:
```
pg8000>=1.31.0
```

Then update `src/database/connection.py` to use:
```python
# Change from: postgresql://
# To: postgresql+pg8000://
```

## Solution 4: Install Build Tools (For Development)

If you need to build from source:

1. **Install Microsoft Visual C++ Build Tools:**
   - Download from: https://visualstudio.microsoft.com/downloads/
   - Install "Build Tools for Visual Studio"
   - Select "C++ build tools" workload

2. **Or install PostgreSQL:**
   - Download from: https://www.postgresql.org/download/windows/
   - This includes `pg_config` which is needed

## Solution 5: Use Updated Requirements (Recommended)

I've created `requirements-windows.txt` with fixes. Try:

```powershell
pip install -r requirements-windows.txt
```

## Solution 6: Skip psycopg2 for Now (Streamlit Cloud Will Handle It)

Since you're deploying to Streamlit Cloud, you can:
1. Skip local installation of psycopg2
2. Streamlit Cloud will install it automatically when deploying
3. Just make sure it's in requirements.txt for deployment

To test locally without psycopg2:
```powershell
pip install -r requirements.txt --ignore-installed psycopg2-binary
```

## Quick Fix Command

Try this sequence:

```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install psycopg2-binary with specific flags
pip install --only-binary :all: --upgrade psycopg2-binary

# Then install everything else
pip install -r requirements.txt
```

## Alternative: Use Python 3.11 or 3.12

If you're using an older Python version, try upgrading:
- Python 3.11+ has better wheel support
- Download from: https://www.python.org/downloads/

## For Streamlit Cloud Deployment

**Good news:** Streamlit Cloud will handle psycopg2-binary installation automatically! The error you're seeing is only for local development.

You can:
1. **Skip local installation** - Just deploy to Streamlit Cloud
2. **Or fix it** using one of the solutions above

## Recommended Approach

Since you're deploying to Streamlit Cloud:

1. **For now:** Just deploy to Streamlit Cloud - it will install dependencies correctly
2. **For local development later:** Use Solution 1 or install Visual C++ Build Tools

The app will work on Streamlit Cloud even if local installation fails!

