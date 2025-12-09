# Special Education IEP Management System (SEIMS)

A comprehensive Special Education IEP Management System built with Streamlit and deployed on Streamlit Cloud.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git
- PostgreSQL database (Supabase recommended)
- Streamlit Cloud account

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/imtiazindia/SEIMS.git
   cd SEIMS
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```
   DATABASE_URL=postgresql://user:password@host:port/database
   SECRET_KEY=your-secret-key-here
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Run the application**
   ```bash
   streamlit run app.py
   ```

## 🌐 Streamlit Cloud Deployment

### Step 1: Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Select repository: `imtiazindia/SEIMS`
5. Set main file path: `app.py`
6. Click "Deploy"

### Step 2: Configure Secrets
In Streamlit Cloud, go to your app settings and add secrets:

```toml
[secrets]
DATABASE_URL = "postgresql://user:password@host:port/database"
SECRET_KEY = "your-secret-key-here"
```

## 📚 Documentation

- [System Design](docs/SYSTEM_DESIGN.md)
- [Development Plan](docs/DEVELOPMENT_PLAN.md)
- [Deployment Guide](STREAMLIT_DEPLOYMENT.md)

## 🔄 Version History

- **v0.1.0** - Initial project structure and documentation

