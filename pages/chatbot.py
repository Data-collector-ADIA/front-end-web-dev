"""Chatbot page (clean, single-file).

Provides a minimal, robust chat UI that shows persisted history and streaming.
"""

import streamlit as st
from components import chatbot
from datetime import datetime, timezone


def _relative_time(ts: str) -> str:
    if not ts:
        return ""
    try:
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
    except Exception:
        try:
            dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S UTC").replace(tzinfo=timezone.utc)
        except Exception:
            return ts
    now = datetime.now(timezone.utc)
    secs = (now - dt).total_seconds()
    if secs < 5:
        return "just now"
    if secs < 60:
        return f"{int(secs)}s ago"
    mins = secs / 60
    if mins < 60:
        return f"{int(mins)}m ago"
    hours = mins / 60
    if hours < 24:
        return f"{int(hours)}h ago"
    days = hours / 24
    if days < 7:
        return f"{int(days)}d ago"
    return dt.strftime("%b %d, %Y")


def safe_rerun():
    try:
        st.experimental_rerun()
    except Exception:
        try:
            from streamlit.runtime.scriptrunner import RerunException

            raise RerunException()
        except Exception:
            st.session_state["_rerun_toggle"] = not st.session_state.get("_rerun_toggle", False)


def render_chat_message(m: dict) -> None:
    role = m.get("role")
    content = m.get("content") or ""
    ts = m.get("ts", "")
    rel = _relative_time(ts)
    if role == "user":
        html = f"""
        <div style='display:flex; align-items:flex-end; justify-content:flex-end; gap:8px; margin:8px 0;'>
          <div style='max-width:75%;'>
            <div style='background:linear-gradient(90deg,#0ea5e9,#06b6d4); color:white; padding:10px 14px; border-radius:16px;'>
              {content}
            </div>
            <div style='font-size:11px; color:rgba(255,255,255,0.6); text-align:right; margin-top:4px;'>{rel}</div>
          </div>
          <div style='width:40px; height:40px; border-radius:50%; background:linear-gradient(135deg,#06b6d4,#0ea5e9); display:flex; align-items:center; justify-content:center; color:white;'>Y</div>
        </div>
        """
    else:
        html = f"""
        <div style='display:flex; align-items:flex-start; gap:12px; margin:8px 0;'>
          <div style='width:40px; height:40px; border-radius:50%; background:linear-gradient(135deg,#667eea,#9d4edd); display:flex; align-items:center; justify-content:center; color:white;'>A</div>
          <div style='max-width:80%;'>
            <div style='background:rgba(255,255,255,0.04); color:#e6f7ff; padding:10px 14px; border-radius:14px;'>
              {content}
            </div>
            <div style='font-size:11px; color:rgba(230,247,255,0.7); margin-top:4px;'>{rel}</div>
          </div>
        </div>
        """
    st.markdown(html, unsafe_allow_html=True)


def app():
    st.set_page_config(page_title="Assistant", page_icon="💬")
    st.title("Assistant")
    use_openai = st.checkbox("Use OpenAI (requires OPENAI_API_KEY)")

    # Streaming / queue state: ensure these keys exist in session state
    if "_is_streaming" not in st.session_state:
        st.session_state["_is_streaming"] = False
    if "_message_queue" not in st.session_state:
        st.session_state["_message_queue"] = []
    if "_auto_send" not in st.session_state:
        st.session_state["_auto_send"] = False

    # Single container for chat history. We'll re-render this container when
    # new messages arrive to avoid duplicate rendering.
    chat_container = st.container()
    with chat_container:
        history = chatbot.get_chat_history(st)
        for m in history:
            render_chat_message(m)

    if st.session_state.get("clear_chat_input"):
        st.session_state["chat_input"] = ""
        st.session_state["clear_chat_input"] = False

    col1, col2 = st.columns([8, 1])
    with col1:
        # Provide a non-empty label but hide it for visual cleanliness to satisfy
        # Streamlit's accessibility checks (avoids the empty-label warning).
        user_input = st.text_area(label="Chat input", key="chat_input", placeholder="Ask me anything...", height=80, label_visibility="collapsed")
    with col2:
        # Disable send while a response is being streamed to avoid duplicate sends
        is_streaming = st.session_state.get("_is_streaming", False)
        # Show queued count next to Send button
        queued = len(st.session_state.get("_message_queue", []))
        send_label = "Send"
        if queued:
            send_label = f"Send ({queued})"
        send = st.button(send_label, disabled=is_streaming)

    def process_message(message_text: str):
        # Called to process a single message: renders chat, streams response,
        # and when finished will trigger processing of the next queued message.
        st.session_state["clear_chat_input"] = True
        typing = st.empty()
        with st.spinner("Assistant is typing..."):
            stream = chatbot.get_response_stream(st, message_text, use_openai=use_openai)
            collected = ""
            # Re-render the chat inside the single container so we don't duplicate
            # messages that were previously rendered at the top of the page.
            chat_container.empty()
            with chat_container:
                hist = chatbot.get_chat_history(st)
                for m in hist:
                    render_chat_message(m)
                # create an assistant placeholder inside the chat container
                assistant_ph = st.empty()

            for chunk in stream:
                collected += chunk
                assistant_ph.markdown(f"<div style='padding:6px 0'>{collected}</div>", unsafe_allow_html=True)
                # show typing indicator while assistant timestamp is still empty
                typing.markdown("<div class='typing-dots'>.</div>", unsafe_allow_html=True)
            # after streaming completes, clear the assistant placeholder and typing indicator
            try:
                assistant_ph.empty()
            except Exception:
                pass
            typing.empty()

        # If a queued message exists, prepare it to be auto-sent and rerun
        if st.session_state["_message_queue"]:
            next_msg = st.session_state["_message_queue"].pop(0)
            st.session_state["chat_input"] = next_msg
            st.session_state["_auto_send"] = True
        else:
            st.session_state["_auto_send"] = False

        # Trigger a rerun so the next message (if any) is picked up and processed.
        safe_rerun()

    # If auto-send flag is set (we placed a queued message into `chat_input`),
    # process it immediately (as if the user had pressed Send).
    if st.session_state.get("_auto_send") and st.session_state.get("chat_input"):
        # clear the flag before processing to avoid loops
        st.session_state["_auto_send"] = False
        process_message(st.session_state.get("chat_input"))

    # Normal send handling: enqueue if currently streaming, otherwise process now
    if send and user_input and user_input.strip():
        if st.session_state.get("_is_streaming"):
            # Queue the message to be sent when the current stream finishes
            q = st.session_state["_message_queue"]
            next_msg = user_input.strip()
            # avoid queuing the identical message twice in a row
            if not q or q[-1] != next_msg:
                q.append(next_msg)
                st.session_state["_message_queue"] = q
            st.session_state["clear_chat_input"] = True
            st.info("Message queued — it will be sent when the assistant finishes typing.")
            safe_rerun()
        else:
            process_message(user_input.strip())

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Clear chat"):
            chatbot.clear_chat(st)
            safe_rerun()


if __name__ == "__main__":
    app()
