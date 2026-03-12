from fastapi import FastAPI
from app.api.whatsapp import router as whatsapp_router
from app.services.rag_service import rag_service
from contextlib import asynccontextmanager
import logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Process PDFs on startup
    print("Pre-processing PDFs from /data folder...")
    info = rag_service.process_pdfs()
    print(f"RAG Info: {info}")
    yield

app = FastAPI(title="Flutter Tutor WhatsApp Chatbot", lifespan=lifespan)

@app.get("/")
def home():
    return {"message": "Flutter Tutor WhatsApp Bot is running! ⚡"}

app.include_router(whatsapp_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
