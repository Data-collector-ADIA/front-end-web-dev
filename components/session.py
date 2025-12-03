"""
Session management module for handling user authentication state.
"""

import streamlit as st

def set_user_session(user_data: dict):
    """
    Set user session data after successful login.
    
    Args:
        user_data: Dictionary containing user information and token
    """
    st.session_state.logged_in = True
    st.session_state.username = user_data.get("username", "")
    st.session_state.user_id = user_data.get("user_id", "")
    st.session_state.email = user_data.get("email", "")
    st.session_state.token = user_data.get("token", "")

def clear_user_session():
    """
    Clear user session data on logout.
    """
    # Clear all session state variables
    for key in ["logged_in", "username", "user_id", "email", "token"]:
        if key in st.session_state:
            del st.session_state[key]

def is_logged_in() -> bool:
    """
    Check if user is currently logged in.
    
    Returns:
        bool: True if user is logged in, False otherwise
    """
    return st.session_state.get("logged_in", False)

def get_current_user() -> dict:
    """
    Get current user information from session.
    
    Returns:
        dict: User information or empty dict if not logged in
    """
    if not is_logged_in():
        return {}
    
    return {
        "username": st.session_state.get("username", ""),
        "user_id": st.session_state.get("user_id", ""),
        "email": st.session_state.get("email", ""),
        "token": st.session_state.get("token", "")
    }

def require_login():
    """
    Decorator/guard function to require login for a page.
    Redirects to login page if user is not authenticated.
    """
    if not is_logged_in():
        st.warning("⚠️ Please login to access this page")
        st.info("Redirecting to login page...")
        
        if st.button("Go to Login"):
            st.switch_page("pages/login.py")
        
        # Auto redirect after 2 seconds
        st.markdown(
            """
            <meta http-equiv="refresh" content="2;url=/login">
            """,
            unsafe_allow_html=True
        )
        st.stop()

def get_auth_token() -> str:
    """
    Get the authentication token from session.
    
    Returns:
        str: Authentication token or empty string if not available
    """
    return st.session_state.get("token", "")
