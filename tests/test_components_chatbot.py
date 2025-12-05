import json
import os
import tempfile
from datetime import timezone

import pytest

import components.chatbot as chatbot


class DummySt:
    def __init__(self):
        self.session_state = {}


def test_append_and_clear(tmp_path):
    # Redirect HISTORY_FILE to temp file
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    chatbot.DATA_DIR = str(data_dir)
    chatbot.HISTORY_FILE = str(data_dir / "chat_history.json")

    st = DummySt()
    chatbot.clear_chat(st)
    assert chatbot.get_chat_history(st) == []

    chatbot.append_message(st, "user", "Hello")
    h = chatbot.get_chat_history(st)
    assert len(h) == 1
    assert h[0]["role"] == "user"
    assert h[0]["content"] == "Hello"
    # ensure saved to disk
    with open(chatbot.HISTORY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 1

    chatbot.append_message(st, "assistant", "Hi")
    assert len(chatbot.get_chat_history(st)) == 2

    chatbot.clear_chat(st)
    assert chatbot.get_chat_history(st) == []


def test_stream_placeholder_and_final_ts(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    chatbot.DATA_DIR = str(data_dir)
    chatbot.HISTORY_FILE = str(data_dir / "chat_history.json")

    st = DummySt()
    # start stream (mock) and exhaust generator
    gen = chatbot.get_response_stream(st, "Hi there", use_openai=False)
    parts = []
    for p in gen:
        parts.append(p)

    # after generator completes, last message should be assistant with ts set
    hist = chatbot.get_chat_history(st)
    assert hist[-1]["role"] == "assistant"
    assert hist[-1]["content"]
    assert hist[-1]["ts"]  # timestamp should be set
