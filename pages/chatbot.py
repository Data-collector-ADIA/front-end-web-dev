import streamlit as st
from components import chatbot


def render_chat_message(message: dict):
        role = message.get("role")
        content = message.get("content") or ""
        ts = message.get("ts", "")
        # bubble HTML with avatar, content and timestamp
        if role == "user":
                html = f"""
                <div style='display:flex; align-items:flex-end; justify-content:flex-end; gap:8px; margin:8px 0;'>
                    <div style='max-width:75%;'>
                        <div style='background:linear-gradient(90deg,#0ea5e9,#06b6d4); color:white; padding:10px 14px; border-radius:16px; border-bottom-right-radius:4px; box-shadow:0 6px 18px rgba(0,0,0,0.3);'>
                            {content}
                        </div>
                        <div style='font-size:11px; color:rgba(255,255,255,0.6); text-align:right; margin-top:4px;'>{ts}</div>
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
                        <div style='font-size:11px; color:rgba(230,247,255,0.7); margin-top:4px;'>{ts}</div>
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
        placeholder = st.empty()
        typing_placeholder = st.empty()
        # Stream the assistant response and show typing indicator
        with st.spinner("Assistant is typing..."):
            stream = chatbot.get_response_stream(st, user_input.strip(), use_openai=use_openai)
            collected = ""
            for chunk in stream:
                collected += chunk
                # Re-render history + the partial reply
                with placeholder.container():
                    history = chatbot.get_chat_history(st)
                    for m in history:
                        render_chat_message(m)
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
        st.experimental_rerun()

    # Controls
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Clear chat"):
            chatbot.clear_chat(st)
            st.experimental_rerun()
    with c2:
        st.write("\n")


if __name__ == "__main__":
    app()
