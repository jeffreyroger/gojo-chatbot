from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.llm.openai_client import generate_response, simulate_typing_delay
from app.llm.memory import get_history, add_message, reset_session

# -------------------- APP --------------------
app = FastAPI(
    title="Gojo-Style Persona Chatbot",
    version="0.3.0"
)

# -------------------- CORS --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev only
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

# -------------------- ENDPOINTS --------------------
@app.get("/")
async def health_check():
    return {"status": "ok"}  # original behavior

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    session_id = payload.session_id
    user_message = payload.message.strip()

    # Fetch conversation history
    history = get_history(session_id)

    # Generate Gojo reply using history
    llm_reply = await generate_response(
        user_message=user_message,
        conversation_history=history
    )

    # Store conversation
    add_message(session_id, "user", user_message)
    add_message(session_id, "gojo", llm_reply)

    # Optional human-like delay
    await simulate_typing_delay(llm_reply)

    return ChatResponse(reply=llm_reply)
