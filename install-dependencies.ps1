# PowerShell script to install SEIMS dependencies on Windows
# Run with: .\install-dependencies.ps1

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "SEIMS - Dependency Installation Script" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found!" -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Upgrade pip
Write-Host "`nUpgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel

# Try to install psycopg2-binary with binary-only flag
Write-Host "`nInstalling psycopg2-binary (this may take a moment)..." -ForegroundColor Yellow
try {
    pip install --only-binary :all: psycopg2-binary
    Write-Host "✓ psycopg2-binary installed successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠ psycopg2-binary installation failed" -ForegroundColor Yellow
    Write-Host "This is okay - Streamlit Cloud will install it automatically" -ForegroundColor Cyan
    Write-Host "You can continue with other dependencies..." -ForegroundColor Cyan
}

# Install other dependencies
Write-Host "`nInstalling other dependencies..." -ForegroundColor Yellow
pip install streamlit streamlit-authenticator streamlit-option-menu sqlalchemy alembic bcrypt python-jose passlib pandas numpy plotly matplotlib reportlab weasyprint jinja2 Pillow python-multipart python-dateutil pytz python-dotenv pyyaml requests

# Optional dependencies
Write-Host "`nInstalling optional dependencies..." -ForegroundColor Yellow
pip install sendgrid boto3 pytest pytest-cov black flake8

Write-Host "`n" + "=" * 60 -ForegroundColor Cyan
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "`nNote: If psycopg2-binary failed, don't worry!" -ForegroundColor Yellow
Write-Host "Streamlit Cloud will install it automatically when you deploy." -ForegroundColor Yellow
Write-Host ""

