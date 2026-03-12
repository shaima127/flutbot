from supabase import create_client, Client
from app.core.config import config

class SupabaseService:
    def __init__(self):
        self.supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

    async def get_user_progress(self, whatsapp_number: str):
        response = self.supabase.table("users").select("*").eq("whatsapp_number", whatsapp_number).execute()
        if response.data:
            return response.data[0]
        return None

    async def create_user(self, whatsapp_number: str):
        data = {
            "whatsapp_number": whatsapp_number,
            "level": "beginner",
            "current_lesson": 0,
            "score": 0,
            "status": "testing"  # testing, learning
        }
        response = self.supabase.table("users").insert(data).execute()
        return response.data[0]

    async def update_user_progress(self, whatsapp_number: str, data: dict):
        response = self.supabase.table("users").update(data).eq("whatsapp_number", whatsapp_number).execute()
        return response.data

supabase_service = SupabaseService()
