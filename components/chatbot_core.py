"""Clean, minimal chatbot helper (stable copy used while refactoring).

This module exposes the same public API as `components.chatbot` but is
implemented as a single, non-duplicated file to avoid mid-rewrite instability.
Use this as the source-of-truth while the main `components.chatbot` is rebuilt.
"""
from __future__ import annotations

import os
import time
import json
from datetime import datetime, timezone
from typing import List, Dict

try:
    import requests
except Exception:
    requests = None

CHAT_HISTORY_KEY = "chat_history"

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
HISTORY_FILE = os.path.join(DATA_DIR, "chat_history.json")


def _ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
        except Exception:
            pass


def _load_history_from_disk() -> List[Dict[str, str]]:
    _ensure_data_dir()
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save_history_to_disk(history: List[Dict[str, str]]) -> None:
    _ensure_data_dir()
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _ensure_history(st):
    if CHAT_HISTORY_KEY not in st.session_state:
        st.session_state[CHAT_HISTORY_KEY] = _load_history_from_disk()


def get_chat_history(st) -> List[Dict[str, str]]:
    _ensure_history(st)
    return st.session_state[CHAT_HISTORY_KEY]


def clear_chat(st) -> None:
    st.session_state[CHAT_HISTORY_KEY] = []
    _save_history_to_disk(st.session_state[CHAT_HISTORY_KEY])


def append_message(st, role: str, content: str, timestamp: str = None) -> None:
    _ensure_history(st)
    # Normalize content and avoid appending duplicate consecutive messages
    content = (content or "").strip()
    if not content and role == "user":
        # don't append empty user messages
        return
    last = None
    if st.session_state[CHAT_HISTORY_KEY]:
        last = st.session_state[CHAT_HISTORY_KEY][-1]
    if last and last.get("role") == role and last.get("content") == content:
        # idempotent: same role + content as last message -> skip
        return
    if timestamp is None:
        timestamp = datetime.now(timezone.utc).isoformat()
    st.session_state[CHAT_HISTORY_KEY].append({"role": role, "content": content, "ts": timestamp})
    _save_history_to_disk(st.session_state[CHAT_HISTORY_KEY])


def _mock_response(user_text: str) -> str:
    text = (user_text or "").lower()
    if "hello" in text or "hi" in text:
        return "Hi there! How can I help you today?"
    if "task" in text:
        return "You can create a new task from the Tasks page."
    if "dashboard" in text:
        return "The dashboard shows metrics and recent tasks. Which metric?"
    if "help" in text or "how" in text:
        return "Ask me about creating, updating, or deleting tasks, or about user accounts."
    return "Thanks — I got that. Can you tell me more?"


def _call_openai_chat(messages: List[Dict[str, str]], model: str = "gpt-4o-mini") -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or requests is None:
        raise RuntimeError("OPENAI_API_KEY not set or requests not available")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": messages, "temperature": 0.2, "max_tokens": 512}
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return str(data)


def get_response_stream(st, user_text: str, use_openai: bool = False, model: str = "gpt-4o-mini"):
    if st.session_state.get("_is_streaming"):
        return
    st.session_state["_is_streaming"] = True

    # Append user message if needed
    hist = get_chat_history(st)
    if not hist or not (hist[-1]["role"] == "user" and hist[-1]["content"] == user_text):
        append_message(st, "user", user_text)

    _ensure_history(st)
    hist = get_chat_history(st)
    if not hist or not (hist[-1]["role"] == "assistant" and hist[-1]["content"] == "" and hist[-1].get("ts", "") == ""):
        st.session_state[CHAT_HISTORY_KEY].append({"role": "assistant", "content": "", "ts": ""})
    assistant_idx = len(st.session_state[CHAT_HISTORY_KEY]) - 1
    _save_history_to_disk(st.session_state[CHAT_HISTORY_KEY])

    try:
        api_key = os.environ.get("OPENAI_API_KEY")
        if use_openai and api_key and requests is not None:
            try:
                messages = [{"role": m["role"], "content": m["content"]} for m in get_chat_history(st)]
                assistant_text = _call_openai_chat(messages, model=model)
                st.session_state[CHAT_HISTORY_KEY][assistant_idx]["content"] = assistant_text
                yield assistant_text
            except Exception as e:
                err = f"(OpenAI error) {e}"
                st.session_state[CHAT_HISTORY_KEY][assistant_idx]["content"] = err
                yield err
        else:
            full = _mock_response(user_text)
            chunk_size = 12
            buffer = ""
            for i in range(0, len(full), chunk_size):
                part = full[i : i + chunk_size]
                buffer += part
                st.session_state[CHAT_HISTORY_KEY][assistant_idx]["content"] = buffer
                yield part
                time.sleep(0.06)
    finally:
        st.session_state[CHAT_HISTORY_KEY][assistant_idx]["ts"] = datetime.now(timezone.utc).isoformat()
        _save_history_to_disk(st.session_state[CHAT_HISTORY_KEY])
        st.session_state["_is_streaming"] = False
