#!/usr/bin/env python3
"""Simple test runner for basic unit checks without pytest.

This script mirrors the two unit tests in `tests/test_components_chatbot.py`
but does not depend on pytest being installed. It exits with code 0 on
success and non-zero on failure.
"""
import json
import os
import sys
import tempfile
from datetime import timezone

import components.chatbot as chatbot
try:
    import components.chatbot_core as chatbot_core
except Exception:
    chatbot_core = None


class DummySt:
    def __init__(self):
        self.session_state = {}


def fail(msg: str):
    print("FAIL:", msg)
    sys.exit(2)


def test_append_and_clear():
    tmp = tempfile.TemporaryDirectory()
    data_dir = os.path.join(tmp.name, "data")
    os.makedirs(data_dir, exist_ok=True)
    chatbot.DATA_DIR = data_dir
    chatbot.HISTORY_FILE = os.path.join(data_dir, "chat_history.json")
    if chatbot_core is not None:
        chatbot_core.DATA_DIR = data_dir
        chatbot_core.HISTORY_FILE = chatbot.HISTORY_FILE

    st = DummySt()
    chatbot.clear_chat(st)
    if chatbot.get_chat_history(st) != []:
        fail("clear_chat did not produce empty history")

    chatbot.append_message(st, "user", "Hello")
    h = chatbot.get_chat_history(st)
    if len(h) != 1 or h[0]["role"] != "user" or h[0]["content"] != "Hello":
        fail("append_message did not record user message correctly")

    # ensure saved to disk
    try:
        with open(chatbot.HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        fail(f"failed reading history file: {e}")
    if len(data) != 1:
        fail("history file does not contain expected number of messages")

    chatbot.append_message(st, "assistant", "Hi")
    if len(chatbot.get_chat_history(st)) != 2:
        fail("assistant message not appended")

    chatbot.clear_chat(st)
    if chatbot.get_chat_history(st) != []:
        fail("clear_chat did not clear history second time")


def test_stream_placeholder_and_final_ts():
    tmp = tempfile.TemporaryDirectory()
    data_dir = os.path.join(tmp.name, "data")
    os.makedirs(data_dir, exist_ok=True)
    chatbot.DATA_DIR = data_dir
    chatbot.HISTORY_FILE = os.path.join(data_dir, "chat_history.json")
    if chatbot_core is not None:
        chatbot_core.DATA_DIR = data_dir
        chatbot_core.HISTORY_FILE = chatbot.HISTORY_FILE

    st = DummySt()
    gen = chatbot.get_response_stream(st, "Hi there", use_openai=False)
    parts = []
    for p in gen:
        parts.append(p)

    hist = chatbot.get_chat_history(st)
    if not hist:
        fail("history empty after streaming")
    if hist[-1]["role"] != "assistant":
        fail("last message is not assistant")
    if not hist[-1]["content"]:
        fail("assistant content empty after stream")
    if not hist[-1].get("ts"):
        fail("assistant timestamp not set after stream")


def main():
    print("Running lightweight unit checks...")
    test_append_and_clear()
    print("test_append_and_clear: OK")
    test_stream_placeholder_and_final_ts()
    print("test_stream_placeholder_and_final_ts: OK")
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
