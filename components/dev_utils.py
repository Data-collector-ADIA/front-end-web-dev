"""
Development utilities for debugging and testing.
"""

import streamlit as st

def show_session_state():
    """Display current session state for debugging"""
    with st.expander("🔍 Debug: Session State", expanded=False):
        st.json(dict(st.session_state))

def show_page_info():
    """Display current page information"""
    with st.expander("📄 Debug: Page Info", expanded=False):
        st.write("**Current Page:**", st.session_state.get("page", "Home"))
        st.write("**Logged In:**", st.session_state.get("logged_in", False))
        st.write("**Username:**", st.session_state.get("username", "N/A"))

def mock_login():
    """Quick mock login for testing (development only)"""
    from components.mock_data import MOCK_USER
    from components.session import set_user_session
    
    st.sidebar.divider()
    st.sidebar.subheader("🧪 Development Tools")
    
    if not st.session_state.get("logged_in", False):
        if st.sidebar.button("🚀 Quick Mock Login"):
            set_user_session(MOCK_USER)
            st.sidebar.success("Logged in as demo_user!")
            st.rerun()
    else:
        st.sidebar.success(f"✅ Logged in as {st.session_state.username}")

def toggle_mock_mode():
    """Toggle between mock and real API"""
    if "use_mock_data" not in st.session_state:
        st.session_state.use_mock_data = True
    
    st.sidebar.divider()
    use_mock = st.sidebar.checkbox(
        "🎭 Use Mock Data",
        value=st.session_state.use_mock_data,
        help="Toggle between mock data and real API calls"
    )
    st.session_state.use_mock_data = use_mock
    
    return use_mock

# Set session after login
st.session_state.logged_in = True
st.session_state.username = "john_doe"

# Check session anywhere in the app
if st.session_state.get("logged_in", False):
    st.write(f"Hello, {st.session_state.username}")
