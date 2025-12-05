import streamlit as st
from components import chatbot


def render_chat_message(message: dict):
    role = message.get("role")
    content = message.get("content") or ""
    if role == "user":
        st.markdown(
            f"<div style='text-align:right; color: #cfeefe; margin:6px 0'>{content}</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<div style='text-align:left; color:#e6f7ff; background:rgba(255,255,255,0.03); padding:10px; border-radius:10px; margin:6px 0'>{content}</div>",
            unsafe_allow_html=True,
        )


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
    col1, col2 = st.columns([8, 1])
    with col1:
        user_input = st.text_area("", key="chat_input", placeholder="Ask me anything...", height=80)
    with col2:
        send = st.button("Send")

    if send and user_input and user_input.strip():
        # Clear input immediately
        st.session_state["chat_input"] = ""

        placeholder = st.empty()
        # Stream the assistant response
        with st.spinner("Assistant is typing..."):
            stream = chatbot.get_response_stream(st, user_input.strip(), use_openai=use_openai)
            collected = ""
            for chunk in stream:
                collected += chunk
                # Re-render history + the partial reply
                with placeholder.container():
                    # recreate full history including partial assistant
                    history = chatbot.get_chat_history(st)
                    for m in history:
                        render_chat_message(m)
        # final render to ensure complete history shown
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
