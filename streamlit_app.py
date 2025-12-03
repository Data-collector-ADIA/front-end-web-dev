import streamlit as st
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Task Management System",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS if available
css_file = Path(__file__).parent / "assets" / "styles.css"
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Display logo if available
logo_file = Path(__file__).parent / "assets" / "logo.png"
if logo_file.exists():
    st.sidebar.image(str(logo_file), use_container_width=True)

# Main app
def main():
    st.title("Welcome to Task Management System")
    
    # Check if user is logged in
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        st.info("👈 Please login or register using the sidebar")
        st.markdown("""
        ### Features
        - 📝 Create and manage tasks
        - 📊 Track your progress
        - 🔐 Secure authentication
        - 💼 Personal dashboard
        
        Get started by logging in or creating a new account!
        """)
    else:
        st.success(f"Welcome back, {st.session_state.get('username', 'User')}!")
        st.markdown("""
        ### Quick Navigation
        - 📊 **Dashboard** - View your task overview
        - ✅ **Tasks** - Manage your tasks
        
        Use the sidebar to navigate between pages.
        """)

if __name__ == "__main__":
    main()
