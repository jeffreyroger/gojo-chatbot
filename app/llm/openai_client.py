import os
import asyncio
from dotenv import load_dotenv
from openai import OpenAI
from .persona import build_persona_prompt
import random
import asyncio
load_dotenv()


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _sync_generate(prompt: str) -> str:
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )
    # Ensure at least an empty string is returned
    return response.output_text or "..."



import re

async def generate_response(user_message: str, conversation_history: list = None) -> str:
    prompt = build_persona_prompt(user_message, conversation_history)

    raw_reply = await asyncio.to_thread(_sync_generate, prompt)
    clean_reply = enforce_spacing(raw_reply)

    print("RAW:", raw_reply)
    print("CLEAN:", clean_reply)

    return clean_reply


async def simulate_typing_delay(text: str):
    """
    Simulates human-like typing delay.
    Can be used in frontend streaming later.
    """
    base_delay = 0.02  # 20ms per character
    variable_delay = [base_delay * random.uniform(0.8, 1.2) for _ in text]
    await asyncio.sleep(sum(variable_delay))
import re
import unicodedata
def enforce_spacing(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"([,.!?])(?=\S)", r"\1 ", text)
    # split lowercase-uppercase merges
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    # split letter-digit merges
    text = re.sub(r"([a-zA-Z])(\d)", r"\1 \2", text)
    text = re.sub(r"(\d)([a-zA-Z])", r"\1 \2", text)
    # collapse multiple spaces
    text = re.sub(r"\s+", " ", text)
    return text.strip()
