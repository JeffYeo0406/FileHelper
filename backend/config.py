import os
from pathlib import Path
from dotenv import load_dotenv

# Look for .env in the project root (parent of backend/)
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_API_KEY_FALLBACK = os.getenv("GEMINI_API_KEY01", "")

# Build ordered list of available API keys (skip empty)
GEMINI_API_KEYS = [k for k in [GEMINI_API_KEY, GEMINI_API_KEY_FALLBACK] if k]
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./file_helper.db")

# Max file upload size: 10 MB
MAX_UPLOAD_SIZE = 10 * 1024 * 1024

# Allowed file extensions
ALLOWED_EXTENSIONS = {".pdf", ".csv", ".xlsx"}

# Output directory for generated Excel files
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
