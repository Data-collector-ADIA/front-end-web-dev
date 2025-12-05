"""Chatbot helper component.

Provides a lightweight chat session stored in Streamlit's session state,
with a simple mock responder and optional OpenAI Chat Completions fallback
when `OPENAI_API_KEY` is present in the environment.

Usage:
  from components.chatbot import send_user_message, get_chat_history, clear_chat

The implementation uses `requests` to call the OpenAI REST API if available.
If no API key is set, the chatbot uses simple keyword-based canned replies.
"""
from __future__ import annotations

import os
import time
import requests
from typing import List, Dict

CHAT_HISTORY_KEY = "chat_history"


def _ensure_history(st):
    if CHAT_HISTORY_KEY not in st.session_state:
        st.session_state[CHAT_HISTORY_KEY] = []


def get_chat_history(st) -> List[Dict[str, str]]:
    _ensure_history(st)
    return st.session_state[CHAT_HISTORY_KEY]


def clear_chat(st) -> None:
    st.session_state[CHAT_HISTORY_KEY] = []


def append_message(st, role: str, content: str) -> None:
    _ensure_history(st)
    st.session_state[CHAT_HISTORY_KEY].append({"role": role, "content": content})


def _mock_response(user_text: str) -> str:
    text = user_text.lower()
    # Simple keyword responses
    if "hello" in text or "hi" in text:
        return "Hi there! How can I help you today?"
    if "task" in text:
        return "You can create a new task from the 'Tasks' page — would you like a quick link?"
    if "dashboard" in text:
        return "The dashboard shows metrics and recent tasks. Which metric do you want to explore?"
    if "help" in text or "how" in text:
        return "Ask me about creating, updating, or deleting tasks, or about user accounts."
    # fallback
    return "Thanks — I got that. Can you tell me more or be more specific?"


def _call_openai_chat(messages: List[Dict[str, str]], model: str = "gpt-4o-mini") -> str:
    """Call OpenAI Chat Completions via REST. Requires OPENAI_API_KEY env var.

    This is a thin wrapper — we keep the call simple so the app doesn't depend
    on the `openai` package. If the request fails the function raises.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 512,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    # Safely extract content
    try:
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        # Fallback — return the raw JSON string if structure differs
        return str(data)


def get_response(st, user_text: str, use_openai: bool = False, model: str = "gpt-4o-mini") -> str:
    """Get a chatbot response. Appends both user and assistant messages to session state.

    If `use_openai` is True and `OPENAI_API_KEY` is set, it will attempt to call OpenAI's
    Chat Completions endpoint. Otherwise, a mock responder will be used.
    """
    append_message(st, "user", user_text)

    # Prepare messages for OpenAI if requested
    history = get_chat_history(st)
    messages = []
    for m in history:
        messages.append({"role": m["role"], "content": m["content"]})

    # Try OpenAI when requested and key present
    api_key = os.environ.get("OPENAI_API_KEY")
    if use_openai and api_key:
        try:
            # Allow a small delay to give a natural feel
            time.sleep(0.25)
            assistant_text = _call_openai_chat(messages, model=model)
        except Exception as e:
            assistant_text = f"(OpenAI error) {str(e)}"
    else:
        assistant_text = _mock_response(user_text)

    append_message(st, "assistant", assistant_text)
    return assistant_text
