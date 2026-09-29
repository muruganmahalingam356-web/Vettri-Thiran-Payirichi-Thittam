import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME = "PocketSmart AI"
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pocketsmart.db")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "5"))

settings = Settings()
