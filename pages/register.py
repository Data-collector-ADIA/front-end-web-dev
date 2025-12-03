import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path to import components
sys.path.append(str(Path(__file__).parent.parent))

from components.api import register_user

st.set_page_config(page_title="Register", page_icon="📝")

st.title("📝 Register")

# Registration form
with st.form("register_form"):
    st.subheader("Create a new account")
    
    username = st.text_input("Username", placeholder="Choose a username")
    email = st.text_input("Email", placeholder="Enter your email")
    password = st.text_input("Password", type="password", placeholder="Choose a password")
    password_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        submit = st.form_submit_button("Register", use_container_width=True)
    with col2:
        if st.form_submit_button("Login Instead", use_container_width=True):
            st.switch_page("pages/login.py")
    
    if submit:
        # Validation
        if not username or not email or not password or not password_confirm:
            st.error("Please fill in all fields")
        elif password != password_confirm:
            st.error("Passwords do not match")
        elif len(password) < 6:
            st.error("Password must be at least 6 characters long")
        else:
            with st.spinner("Creating account..."):
                success, message = register_user(username, email, password)
                
                if success:
                    st.success(message)
                    st.info("Please login with your credentials")
                    st.balloons()
                    if st.button("Go to Login"):
                        st.switch_page("pages/login.py")
                else:
                    st.error(message)

# Show registration tips
with st.expander("ℹ️ Registration Tips"):
    st.markdown("""
    - Choose a unique username
    - Use a valid email address
    - Password must be at least 6 characters
    - Remember your credentials for login
    """)
