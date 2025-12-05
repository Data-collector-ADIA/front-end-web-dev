import streamlit as st
from components import chatbot
from datetime import datetime, timezone
import math


def _relative_time(ts: str) -> str:
    """Return a short human-friendly relative time for an ISO timestamp.

    Handles legacy timestamp formats by falling back to returning the raw string.
    """
    if not ts:
        return ""
    try:
        # Prefer ISO 8601 parsing
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
    except Exception:
        # Try parsing older format like 'YYYY-MM-DD HH:MM:SS UTC'
        try:
            dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S UTC").replace(tzinfo=timezone.utc)
        except Exception:
            return ts

    now = datetime.now(timezone.utc)
    diff = now - dt
    secs = diff.total_seconds()
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
    # older: show date
    return dt.strftime("%b %d, %Y")


def safe_rerun():
    """Safely trigger a Streamlit rerun across Streamlit versions.

    This attempts the public API first, then falls back to internal
    RerunException imports. If all else fails it toggles a session_state
    key which can prompt a UI change on some Streamlit builds.
    """
    try:
        st.experimental_rerun()
        return
    except AttributeError:
        # Try internal runtime exception used by some Streamlit versions
        try:
            from streamlit.runtime.scriptrunner import RerunException

            raise RerunException()
        except Exception:
            try:
                from streamlit.runtime.scriptrunner.script_runner import RerunException

                raise RerunException()
            except Exception:
                # Last-resort: toggle a session flag to provoke a rerun on next interaction
                st.session_state["_rerun_toggle"] = not st.session_state.get("_rerun_toggle", False)
                return


def render_chat_message(message: dict):
        role = message.get("role")
        content = message.get("content") or ""
    ts = message.get("ts", "")
    rel_ts = _relative_time(ts)
        # bubble HTML with avatar, content and timestamp
        if role == "user":
                html = f"""
                <div style='display:flex; align-items:flex-end; justify-content:flex-end; gap:8px; margin:8px 0;'>
                    <div style='max-width:75%;'>
                        <div style='background:linear-gradient(90deg,#0ea5e9,#06b6d4); color:white; padding:10px 14px; border-radius:16px; border-bottom-right-radius:4px; box-shadow:0 6px 18px rgba(0,0,0,0.3);'>
                            {content}
                        </div>
                        <div style='font-size:11px; color:rgba(255,255,255,0.6); text-align:right; margin-top:4px;'>{rel_ts}</div>
                    </div>
                    <div style='width:40px; height:40px; border-radius:50%; background:linear-gradient(135deg,#06b6d4,#0ea5e9); display:flex; align-items:center; justify-content:center; color:white; font-weight:700;'>
                        Y
                    </div>
                </div>
                """
                st.markdown(html, unsafe_allow_html=True)
        else:
                html = f"""
                <div style='display:flex; align-items:flex-start; gap:12px; margin:8px 0;'>
                    <div style='width:40px; height:40px; border-radius:50%; background:linear-gradient(135deg,#667eea,#9d4edd); display:flex; align-items:center; justify-content:center; color:white; font-weight:700;'>
                        A
                    </div>
                    <div style='max-width:80%;'>
                        <div style='background:rgba(255,255,255,0.04); color:#e6f7ff; padding:10px 14px; border-radius:14px; border-bottom-left-radius:4px; box-shadow:0 6px 18px rgba(0,0,0,0.3);'>
                            {content}
                        </div>
                        <div style='font-size:11px; color:rgba(230,247,255,0.7); margin-top:4px;'>{rel_ts}</div>
                    </div>
                </div>
                """
                st.markdown(html, unsafe_allow_html=True)


def app():
    st.set_page_config(page_title="Assistant", page_icon="💬")
    st.title("Assistant")

    use_openai = st.checkbox("Use OpenAI (requires OPENAI_API_KEY)", value=False)

    # Render history
    history = chatbot.get_chat_history(st)
    chat_box = st.container()
    with chat_box:
        for m in history:
            render_chat_message(m)

    # Input area
    # If a previous run requested the input to be cleared, apply it before creating the widget
    if st.session_state.get("clear_chat_input"):
        st.session_state["chat_input"] = ""
        st.session_state["clear_chat_input"] = False

    col1, col2 = st.columns([8, 1])
    with col1:
        user_input = st.text_area("", key="chat_input", placeholder="Ask me anything...", height=80)
    with col2:
        send = st.button("Send")

    if send and user_input and user_input.strip():
        # Request the input be cleared on the next rerun (can't modify widget value after instantiation)
        st.session_state["clear_chat_input"] = True
        container = st.empty()
        typing_placeholder = st.empty()
        # Stream the assistant response and show typing indicator
        with st.spinner("Assistant is typing..."):
            stream = chatbot.get_response_stream(st, user_input.strip(), use_openai=use_openai)
            collected = ""
            # Render full history once (includes the new user + placeholder assistant)
            history = chatbot.get_chat_history(st)
            with container.container():
                for m in history:
                    render_chat_message(m)

            # Create a dedicated placeholder for the streaming assistant message
            assistant_placeholder = st.empty()

            for chunk in stream:
                collected += chunk
                # update only the assistant placeholder with incremental content
                # get latest assistant timestamp (may be ISO string)
                hist = chatbot.get_chat_history(st)
                assistant_ts = ""
                if hist and hist[-1].get("role") == "assistant":
                    assistant_ts = hist[-1].get("ts", "")

                assistant_html = f"""
                <div style='display:flex; align-items:flex-start; gap:12px; margin:8px 0;'>
                    <div style='width:40px; height:40px; border-radius:50%; background:linear-gradient(135deg,#667eea,#9d4edd); display:flex; align-items:center; justify-content:center; color:white; font-weight:700;'>
                        A
                    </div>
                    <div style='max-width:80%;'>
                        <div style='background:rgba(255,255,255,0.04); color:#e6f7ff; padding:10px 14px; border-radius:14px; border-bottom-left-radius:4px; box-shadow:0 6px 18px rgba(0,0,0,0.3);'>
                            {collected}
                        </div>
                        <div style='font-size:11px; color:rgba(230,247,255,0.7); margin-top:4px;'>{_relative_time(assistant_ts)}</div>
                    </div>
                </div>
                """
                assistant_placeholder.markdown(assistant_html, unsafe_allow_html=True)

                # show typing indicator below the last message while streaming
                typing_html = """
                <div style='display:flex; align-items:center; gap:10px; margin:6px 0;'>
                  <div style='width:36px; height:36px; border-radius:50%; background:linear-gradient(135deg,#06b6d4,#0ea5e9);'></div>
                  <div style='background:rgba(255,255,255,0.03); padding:8px 12px; border-radius:12px;'>
                    <span class='typing-dots'>.</span>
                  </div>
                </div>
                """
                typing_placeholder.markdown(typing_html, unsafe_allow_html=True)

        # clear typing indicator and rerun to show final state
        typing_placeholder.empty()
        safe_rerun()

    # Controls
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Clear chat"):
            chatbot.clear_chat(st)
            safe_rerun()
    with c2:
        st.write("\n")


if __name__ == "__main__":
    app()
