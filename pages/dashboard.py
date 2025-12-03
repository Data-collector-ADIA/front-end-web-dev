import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path to import components
sys.path.append(str(Path(__file__).parent.parent))

from components.api import get_user_tasks, get_task_statistics
from components.session import require_login, clear_user_session

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

# Require login
require_login()

st.title("📊 Dashboard")
st.write(f"Welcome, **{st.session_state.get('username', 'User')}**!")

# Logout button
if st.sidebar.button("Logout", use_container_width=True):
    clear_user_session()
    st.success("Logged out successfully")
    st.rerun()

# Fetch task statistics
with st.spinner("Loading dashboard..."):
    stats = get_task_statistics()

# Display metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Tasks",
        value=stats.get("total", 0),
        delta=None
    )

with col2:
    st.metric(
        label="Pending",
        value=stats.get("pending", 0),
        delta=None
    )

with col3:
    st.metric(
        label="In Progress",
        value=stats.get("in_progress", 0),
        delta=None
    )

with col4:
    st.metric(
        label="Completed",
        value=stats.get("completed", 0),
        delta=None
    )

# Task overview
st.divider()

# Recent tasks
st.subheader("Recent Tasks")

tasks = get_user_tasks(limit=5)

if tasks:
    for task in tasks:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{task.get('title', 'Untitled')}**")
                st.caption(task.get('description', 'No description')[:100])
            
            with col2:
                status = task.get('status', 'pending')
                status_colors = {
                    'pending': '🟡',
                    'in_progress': '🔵',
                    'completed': '🟢'
                }
                st.write(f"{status_colors.get(status, '⚪')} {status.replace('_', ' ').title()}")
            
            with col3:
                priority = task.get('priority', 'medium')
                priority_colors = {
                    'low': '🟢',
                    'medium': '🟡',
                    'high': '🔴'
                }
                st.write(f"{priority_colors.get(priority, '⚪')} {priority.title()}")
        
        st.divider()
else:
    st.info("No tasks yet. Create your first task!")

# Quick actions
st.subheader("Quick Actions")
col1, col2 = st.columns(2)

with col1:
    if st.button("➕ Create New Task", use_container_width=True):
        st.switch_page("pages/task.py")

with col2:
    if st.button("📋 View All Tasks", use_container_width=True):
        st.switch_page("pages/task.py")
