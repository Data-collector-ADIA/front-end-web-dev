import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path to import components
sys.path.append(str(Path(__file__).parent.parent))

from components.api import get_user_tasks, create_task, update_task, delete_task
from components.session import require_login, clear_user_session

st.set_page_config(page_title="Tasks", page_icon="✅", layout="wide")

# Require login
require_login()

st.title("✅ Task Management")

# Logout button
if st.sidebar.button("Logout", use_container_width=True):
    clear_user_session()
    st.success("Logged out successfully")
    st.rerun()

# Tabs for different views
tab1, tab2 = st.tabs(["📋 All Tasks", "➕ Create Task"])

# Tab 1: View and manage tasks
with tab1:
    # Filters
    st.subheader("Filter Tasks")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "Status",
            ["all", "pending", "in_progress", "completed"],
            format_func=lambda x: x.replace("_", " ").title()
        )
    
    with col2:
        priority_filter = st.selectbox(
            "Priority",
            ["all", "low", "medium", "high"],
            format_func=lambda x: x.title()
        )
    
    with col3:
        sort_by = st.selectbox(
            "Sort By",
            ["created_date", "priority", "status"],
            format_func=lambda x: x.replace("_", " ").title()
        )
    
    st.divider()
    
    # Fetch tasks
    tasks = get_user_tasks()
    
    # Apply filters
    if status_filter != "all":
        tasks = [t for t in tasks if t.get("status") == status_filter]
    
    if priority_filter != "all":
        tasks = [t for t in tasks if t.get("priority") == priority_filter]
    
    # Display tasks
    if tasks:
        st.write(f"Showing {len(tasks)} task(s)")
        
        for idx, task in enumerate(tasks):
            with st.expander(f"**{task.get('title', 'Untitled')}** - {task.get('status', 'pending').replace('_', ' ').title()}"):
                # Display task details
                st.write(f"**Description:** {task.get('description', 'No description')}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Status:** {task.get('status', 'pending').replace('_', ' ').title()}")
                with col2:
                    st.write(f"**Priority:** {task.get('priority', 'medium').title()}")
                with col3:
                    st.write(f"**Created:** {task.get('created_at', 'N/A')}")
                
                # Edit task
                st.subheader("Update Task")
                
                with st.form(f"update_form_{idx}"):
                    new_title = st.text_input("Title", value=task.get('title', ''))
                    new_description = st.text_area("Description", value=task.get('description', ''))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        new_status = st.selectbox(
                            "Status",
                            ["pending", "in_progress", "completed"],
                            index=["pending", "in_progress", "completed"].index(task.get('status', 'pending')),
                            format_func=lambda x: x.replace("_", " ").title()
                        )
                    with col2:
                        new_priority = st.selectbox(
                            "Priority",
                            ["low", "medium", "high"],
                            index=["low", "medium", "high"].index(task.get('priority', 'medium')),
                            format_func=lambda x: x.title()
                        )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Update Task", use_container_width=True):
                            success, message = update_task(
                                task.get('id'),
                                new_title,
                                new_description,
                                new_status,
                                new_priority
                            )
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                    
                    with col2:
                        if st.form_submit_button("🗑️ Delete Task", use_container_width=True):
                            success, message = delete_task(task.get('id'))
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
    else:
        st.info("No tasks found. Create your first task!")

# Tab 2: Create new task
with tab2:
    st.subheader("Create New Task")
    
    with st.form("create_task_form"):
        title = st.text_input("Task Title *", placeholder="Enter task title")
        description = st.text_area("Description", placeholder="Enter task description (optional)")
        
        col1, col2 = st.columns(2)
        with col1:
            priority = st.selectbox(
                "Priority",
                ["low", "medium", "high"],
                index=1,
                format_func=lambda x: x.title()
            )
        
        with col2:
            status = st.selectbox(
                "Status",
                ["pending", "in_progress", "completed"],
                format_func=lambda x: x.replace("_", " ").title()
            )
        
        submit = st.form_submit_button("Create Task", use_container_width=True)
        
        if submit:
            if not title:
                st.error("Task title is required")
            else:
                success, message = create_task(title, description, status, priority)
                if success:
                    st.success(message)
                    st.balloons()
                    st.rerun()
                else:
                    st.error(message)
