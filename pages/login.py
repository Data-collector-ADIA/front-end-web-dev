import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path to import components
sys.path.append(str(Path(__file__).parent.parent))

from components.api import login_user
from components.session import set_user_session

st.set_page_config(page_title="Login", page_icon="🔐")

st.title("🔐 Login")

# Login form
with st.form("login_form"):
    st.subheader("Sign in to your account")
    
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        submit = st.form_submit_button("Login", use_container_width=True)
    with col2:
        if st.form_submit_button("Register Instead", use_container_width=True):
            st.switch_page("pages/register.py")
    
    if submit:
        if not username or not password:
            st.error("Please enter both username and password")
        else:
            with st.spinner("Logging in..."):
                success, message, user_data = login_user(username, password)
                
                if success:
                    set_user_session(user_data)
                    st.success(message)
                    st.balloons()
                    st.rerun()
                else:
                    st.error(message)

# Display current session status
if st.session_state.get("logged_in", False):
    st.success(f"✅ Already logged in as: {st.session_state.get('username')}")
    if st.button("Go to Dashboard"):
        st.switch_page("pages/dashboard.py")
