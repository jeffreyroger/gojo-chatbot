from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

from app.llm.openai_client import generate_response, simulate_typing_delay
from app.llm.memory import get_history, add_message

# -------------------- APP --------------------
app = FastAPI(
    title="Gojo-Style Persona Chatbot",
    version="0.3.0"
)

# -------------------- CORS --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- STATIC FILES --------------------
app.mount("/static", StaticFiles(directory="static"), name="static")

# -------------------- MODELS --------------------
class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    reply: str

# -------------------- ROUTES --------------------
@app.get("/")
async def serve_frontend():
    """Serve frontend index.html"""
    return FileResponse("static/index.html")

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    session_id = payload.session_id
    user_message = payload.message.strip()

    history = get_history(session_id)

    llm_reply = await generate_response(
        user_message=user_message,
        conversation_history=history
    )

    add_message(session_id, "user", user_message)
    add_message(session_id, "gojo", llm_reply)

    await simulate_typing_delay(llm_reply)

    return ChatResponse(reply=llm_reply)
