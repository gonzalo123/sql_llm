import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-70b-8192")

DB_NAME = os.getenv("DB_NAME", 'gonzalo123')
DB_USER = os.getenv("DB_USER", 'username')
DB_HOST = os.getenv("DB_HOST", 'localhost')
DB_PASS = os.getenv("DB_PASS", 'password')
DB_PORT = os.getenv("DB_PORT", '5432')

DSN = (f"dbname='{DB_NAME}' "
       f"user='{DB_USER}' "
       f"host='{DB_HOST}' "
       f"password='{DB_PASS}' "
       f"port='{DB_PORT}'")
