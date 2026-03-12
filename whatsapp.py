from fastapi import APIRouter, Request, HTTPException
from app.core.config import config
from app.services.supabase_service import supabase_service
from app.services.groq_service import groq_service
from app.services.rag_service import rag_service
import httpx
import logging

router = APIRouter()

META_API_URL = "https://graph.facebook.com/v19.0"

async def send_whatsapp_message(to_number: str, message: str):
    url = f"{META_API_URL}/{config.WHATSAPP_PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {config.META_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": message}
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
        return response.json()

@router.get("/webhook")
async def verify_webhook(request: Request):
    query_params = request.query_params
    mode = query_params.get("hub.mode")
    token = query_params.get("hub.verify_token")
    challenge = query_params.get("hub.challenge")

    if mode == "subscribe" and token == config.WEBHOOK_VERIFY_TOKEN:
        return int(challenge)
    raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/webhook")
async def handle_whatsapp_message(request: Request):
    body = await request.json()
    
    try:
        # Check standard Meta JSON structure
        if "messages" not in body["entry"][0]["changes"][0]["value"]:
            return {"status": "ok"}
            
        message_data = body["entry"][0]["changes"][0]["value"]["messages"][0]
        whatsapp_number = message_data["from"]
        user_message = message_data["text"]["body"]

        # 1. Fetch user progress from Supabase
        user = await supabase_service.get_user_progress(whatsapp_number)
        
        if not user:
            # First interaction
            await supabase_service.create_user(whatsapp_number)
            welcome_msg = (
                "مرحباً بك في بوت تعليم Flutter! 🚀\n"
                "سأقوم أولاً بإجراء اختبار قصير لتحديد مستواك.\n"
                "يرجى الإجابة على الأسئلة التالية:\n"
                "1. هل سبق لك البرمجة بأي لغة؟\n"
                "2. هل تعرف مفهوم الـ Widgets في Flutter؟\n"
                "3. هل سبق لك التعامل مع State Management؟"
            )
            await send_whatsapp_message(whatsapp_number, welcome_msg)
            return {"status": "ok"}

        # 2. Process logic based on user status
        if user["status"] == "testing":
            # Level assessment
            level = await groq_service.evaluate_test(user_message)
            await supabase_service.update_user_progress(whatsapp_number, {"level": level, "status": "learning"})
            level_msg = f"تم تحديد مستواك كـ: {level}. \nلنبدأ دروسنا الآن! قل 'ابدأ' لنبدأ أول درس."
            await send_whatsapp_message(whatsapp_number, level_msg)
            
        else:
            # Normal teaching interaction (RAG + AI)
            context = rag_service.retrieve_context(user_message)
            response = await groq_service.generate_response(
                prompt=f"User asked: {user_message}. Based on their level {user['level']}, please provide an educational response and codes to practice.",
                context=context
            )
            await send_whatsapp_message(whatsapp_number, response)
            
        return {"status": "ok"}
        
    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "message": str(e)}
