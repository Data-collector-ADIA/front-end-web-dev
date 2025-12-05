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


def get_response_stream(st, user_text: str, use_openai: bool = False, model: str = "gpt-4o-mini"):
    """Stream assistant response.

    Yields successive text chunks (strings). For mock mode this simulates typing.
    For OpenAI mode it uses the streaming Chat Completions API (if `OPENAI_API_KEY`
    is set) and yields delta content as it arrives.

    The function also appends a placeholder assistant message to session state and
    updates its content progressively so `get_chat_history` remains accurate.
    """
    append_message(st, "user", user_text)
    # add placeholder assistant message and get its index
    _ensure_history(st)
    st.session_state[CHAT_HISTORY_KEY].append({"role": "assistant", "content": ""})
    assistant_idx = len(st.session_state[CHAT_HISTORY_KEY]) - 1

    api_key = os.environ.get("OPENAI_API_KEY")
    if use_openai and api_key:
        # Stream from OpenAI
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        messages = get_chat_history(st)  # includes user + placeholder assistant
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 512,
            "stream": True,
        }
        try:
            with requests.post(url, headers=headers, json=payload, stream=True, timeout=60) as resp:
                resp.raise_for_status()
                buffer = ""
                for line in resp.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    # OpenAI streaming sends lines like: "data: {json}" or "data: [DONE]"
                    try:
                        text_line = line.decode() if isinstance(line, bytes) else line
                    except Exception:
                        text_line = line
                    if text_line.startswith("data: "):
                        data = text_line[len("data: "):].strip()
                    else:
                        data = text_line.strip()
                    if data == "[DONE]":
                        break
                    try:
                        chunk = requests.utils.json.loads(data)
                        # navigate to delta content
                        for choice in chunk.get("choices", []):
                            delta = choice.get("delta", {})
                            content = delta.get("content")
                            if content:
                                buffer += content
                                # update session state and yield
                                st.session_state[CHAT_HISTORY_KEY][assistant_idx]["content"] = buffer
                                yield content
                    except Exception:
                        # ignore parse errors
                        continue
        except Exception as e:
            err = f"(OpenAI stream error) {e}"
            st.session_state[CHAT_HISTORY_KEY][assistant_idx]["content"] = err
            yield err
        return

    # Mock streaming: simulate typing by splitting into chunks
    full = _mock_response(user_text)
    chunk_size = 12
    buffer = ""
    for i in range(0, len(full), chunk_size):
        part = full[i : i + chunk_size]
        buffer += part
        st.session_state[CHAT_HISTORY_KEY][assistant_idx]["content"] = buffer
        yield part
        time.sleep(0.06)
