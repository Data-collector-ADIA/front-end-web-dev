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
        send = st.button("Send")

    if send and user_input and user_input.strip():
        st.session_state["clear_chat_input"] = True
        placeholder = st.empty()
        typing = st.empty()
        with st.spinner("Assistant is typing..."):
            stream = chatbot.get_response_stream(st, user_input.strip(), use_openai=use_openai)
            collected = ""
            hist = chatbot.get_chat_history(st)
            with placeholder.container():
                for m in hist:
                    render_chat_message(m)
            assistant_ph = st.empty()
            for chunk in stream:
                collected += chunk
                assistant_ph.markdown(f"<div style='padding:6px 0'>{collected}</div>", unsafe_allow_html=True)
                # show typing indicator while assistant timestamp is still empty
                typing.markdown("<div class='typing-dots'>.</div>", unsafe_allow_html=True)
            # after streaming completes, if assistant has a timestamp show final time
            hist_after = chatbot.get_chat_history(st)
            if hist_after and hist_after[-1].get('ts'):
                # replace typing area with final timestamp under the assistant message
                typing.empty()
            else:
                # fallback: clear typing indicator
                typing.empty()
        typing.empty()
        safe_rerun()

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Clear chat"):
            chatbot.clear_chat(st)
            safe_rerun()


if __name__ == "__main__":
    app()
