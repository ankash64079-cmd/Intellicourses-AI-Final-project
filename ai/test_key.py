import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
dotenv_path = BASE_DIR / ".env"

print("Loading .env from:", dotenv_path)
load_dotenv(dotenv_path=str(dotenv_path))  # Ensure it's a string for Windows

api_key = os.getenv("GEMINI_API_KEY")
print("GEMINI_API_KEY loaded:", repr(api_key))