"""
API helper module to call backend REST endpoints.
Update the BASE_URL to match your backend server.
"""

import requests
import streamlit as st
import components.mock_data as mock_data

# Backend API configuration
BASE_URL = "http://localhost:8000/api"  # Update this to your backend URL

def get_headers():
    """Get headers with authentication token if available."""
    headers = {"Content-Type": "application/json"}
    
    if "token" in st.session_state:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    
    return headers

# Authentication APIs
def login_user(username: str, password: str):
    """
    Login user and return token.
    
    Returns:
        tuple: (success: bool, message: str, user_data: dict)
    """
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": username, "password": password},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return True, "Login successful!", data
        else:
            return False, response.json().get("message", "Login failed"), None
    
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to server. Please check if backend is running.", None
    except Exception as e:
        return False, f"Error: {str(e)}", None

def register_user(username: str, email: str, password: str):
    """
    Register a new user.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={"username": username, "email": email, "password": password},
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            return True, "Registration successful! Please login."
        else:
            return False, response.json().get("message", "Registration failed")
    
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to server. Please check if backend is running."
    except Exception as e:
        return False, f"Error: {str(e)}"

# Task APIs
def get_user_tasks(limit: int = None):
    """
    Get all tasks for the current user.
    
    Returns:
        list: List of task dictionaries
    """
    # Use mock data if enabled
    if mock_data.USE_MOCK_DATA:
        tasks = mock_data.MOCK_TASKS.copy()
        if limit:
            return tasks[:limit]
        return tasks
    
    try:
        params = {"limit": limit} if limit else {}
        response = requests.get(
            f"{BASE_URL}/tasks",
            headers=get_headers(),
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json().get("tasks", [])
        else:
            st.warning(f"Failed to fetch tasks: {response.json().get('message', 'Unknown error')}")
            return []
    
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to server")
        return []
    except Exception as e:
        st.error(f"Error fetching tasks: {str(e)}")
        return []

def create_task(title: str, description: str = "", status: str = "pending", priority: str = "medium"):
    """
    Create a new task.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    # Use mock data if enabled
    if mock_data.USE_MOCK_DATA:
        new_task = {
            "id": str(len(mock_data.MOCK_TASKS) + 1),
            "title": title,
            "description": description,
            "status": status,
            "priority": priority,
            "created_at": "2025-12-03 14:00:00"
        }
        mock_data.MOCK_TASKS.append(new_task)
        return True, "Task created successfully! (Mock Mode)"
    
    try:
        response = requests.post(
            f"{BASE_URL}/tasks",
            headers=get_headers(),
            json={
                "title": title,
                "description": description,
                "status": status,
                "priority": priority
            },
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            return True, "Task created successfully!"
        else:
            return False, response.json().get("message", "Failed to create task")
    
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to server"
    except Exception as e:
        return False, f"Error: {str(e)}"

def update_task(task_id: str, title: str, description: str, status: str, priority: str):
    """
    Update an existing task.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    # Use mock data if enabled
    if mock_data.USE_MOCK_DATA:
        for task in mock_data.MOCK_TASKS:
            if task["id"] == task_id:
                task["title"] = title
                task["description"] = description
                task["status"] = status
                task["priority"] = priority
                return True, "Task updated successfully! (Mock Mode)"
        return False, "Task not found"
    
    try:
        response = requests.put(
            f"{BASE_URL}/tasks/{task_id}",
            headers=get_headers(),
            json={
                "title": title,
                "description": description,
                "status": status,
                "priority": priority
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return True, "Task updated successfully!"
        else:
            return False, response.json().get("message", "Failed to update task")
    
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to server"
    except Exception as e:
        return False, f"Error: {str(e)}"

def delete_task(task_id: str):
    """
    Delete a task.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    # Use mock data if enabled
    if mock_data.USE_MOCK_DATA:
        original_len = len(mock_data.MOCK_TASKS)
        mock_data.MOCK_TASKS[:] = [task for task in mock_data.MOCK_TASKS if task["id"] != task_id]
        if len(mock_data.MOCK_TASKS) < original_len:
            return True, "Task deleted successfully! (Mock Mode)"
        return False, "Task not found"
    
    try:
        response = requests.delete(
            f"{BASE_URL}/tasks/{task_id}",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            return True, "Task deleted successfully!"
        else:
            return False, response.json().get("message", "Failed to delete task")
    
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to server"
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_task_statistics():
    """
    Get task statistics for the current user.
    
    Returns:
        dict: Statistics including total, pending, in_progress, completed
    """
    # Use mock data if enabled
    if mock_data.USE_MOCK_DATA:
        return mock_data.get_mock_statistics()
    
    try:
        response = requests.get(
            f"{BASE_URL}/tasks/stats",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            # Return default stats if API fails
            tasks = get_user_tasks()
            return {
                "total": len(tasks),
                "pending": len([t for t in tasks if t.get("status") == "pending"]),
                "in_progress": len([t for t in tasks if t.get("status") == "in_progress"]),
                "completed": len([t for t in tasks if t.get("status") == "completed"])
            }
    
    except Exception:
        # Fallback to calculating stats from tasks
        tasks = get_user_tasks()
        return {
            "total": len(tasks),
            "pending": len([t for t in tasks if t.get("status") == "pending"]),
            "in_progress": len([t for t in tasks if t.get("status") == "in_progress"]),
            "completed": len([t for t in tasks if t.get("status") == "completed"])
        }
