import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
    WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
    WEBHOOK_VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN")

config = Config()
