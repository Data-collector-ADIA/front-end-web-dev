"""
Mock data for front-end development without backend.
Use this to test UI components independently.
"""

# Mock user data
MOCK_USER = {
    "username": "demo_user",
    "user_id": "12345",
    "email": "demo@example.com",
    "token": "mock_token_123456"
}

# Mock tasks
MOCK_TASKS = [
    {
        "id": "1",
        "title": "Complete project documentation",
        "description": "Write comprehensive documentation for the task management system",
        "status": "in_progress",
        "priority": "high",
        "created_at": "2025-12-01 10:00:00"
    },
    {
        "id": "2",
        "title": "Review code changes",
        "description": "Review pull requests from team members",
        "status": "pending",
        "priority": "medium",
        "created_at": "2025-12-02 14:30:00"
    },
    {
        "id": "3",
        "title": "Update dependencies",
        "description": "Update Python packages to latest stable versions",
        "status": "completed",
        "priority": "low",
        "created_at": "2025-11-30 09:15:00"
    },
    {
        "id": "4",
        "title": "Design new features",
        "description": "Create mockups for upcoming features",
        "status": "pending",
        "priority": "high",
        "created_at": "2025-12-03 08:00:00"
    }
]

def get_mock_statistics():
    """Get mock task statistics"""
    return {
        "total": len(MOCK_TASKS),
        "pending": len([t for t in MOCK_TASKS if t["status"] == "pending"]),
        "in_progress": len([t for t in MOCK_TASKS if t["status"] == "in_progress"]),
        "completed": len([t for t in MOCK_TASKS if t["status"] == "completed"])
    }

# Enable/disable mock mode
USE_MOCK_DATA = True  # Set to False when backend is ready
