from collections import defaultdict, deque
from typing import List, Dict

# Store last N messages per session (user + gojo)
MAX_HISTORY = 12

# session_id -> deque of {role, content}
session_memory = defaultdict(lambda: deque(maxlen=MAX_HISTORY))


def get_history(session_id: str) -> List[Dict[str, str]]:
    """
    Returns conversation history in structured format:
    [
      {"role": "user", "content": "..."},
      {"role": "gojo", "content": "..."}
    ]
    """
    return list(session_memory[session_id])


def add_message(session_id: str, role: str, message: str):
    """
    role: 'user' or 'gojo'
    """
    session_memory[session_id].append({
        "role": role,
        "content": message.strip()
    })


def reset_session(session_id: str):
    """Clear conversation memory for a session"""
    session_memory[session_id].clear()
