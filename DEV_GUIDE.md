# Front-End Development Guide

## Quick Start

Your Streamlit app is running at: http://localhost:8501

### Development Workflow

1. **Make changes** to any `.py` or `.css` file
2. **Save the file** (Cmd+S / Ctrl+S)
3. **See "Source file changed"** notification in browser
4. **Click "Rerun"** or enable "Always rerun"

### Development Mode Features

#### Mock Data Testing
To test UI without backend:
```python
# In components/mock_data.py
USE_MOCK_DATA = True  # Enable mock mode
```

#### Debug Session State
Add to any page:
```python
from components.dev_utils import show_session_state
show_session_state()  # Shows all session variables
```

#### Quick Mock Login
Add to sidebar:
```python
from components.dev_utils import mock_login
mock_login()  # Adds quick login button
```

### File Structure

```
front-end-web-dev/
├── streamlit_app.py          # Main entry (home page)
├── pages/
│   ├── login.py              # Login form
│   ├── register.py           # Registration form
│   ├── dashboard.py          # Statistics & overview
│   └── task.py               # Task CRUD operations
├── components/
│   ├── api.py                # Backend API calls
│   ├── session.py            # Session management
│   ├── mock_data.py          # Mock data for testing
│   └── dev_utils.py          # Development utilities
└── assets/
    └── styles.css            # Custom CSS styling
```

### Common Development Tasks

#### 1. Change Page Title/Icon
Edit the page:
```python
st.set_page_config(
    page_title="Your Title",
    page_icon="🎯"
)
```

#### 2. Add New Page
Create `pages/your_page.py`:
```python
import streamlit as st
st.title("Your New Page")
```
It appears automatically in sidebar!

#### 3. Modify Styling
Edit `assets/styles.css` and save - changes apply immediately

#### 4. Test Without Backend
Set `USE_MOCK_DATA = True` in `components/mock_data.py`

### Keyboard Shortcuts in Browser

- `R` - Rerun the app
- `C` - Clear cache
- `Cmd/Ctrl + K` - Open command palette

### Tips

✅ Enable "Always rerun" in settings (⋮ menu top-right)
✅ Use st.write() for quick debugging
✅ Check browser console for errors (F12)
✅ Use st.sidebar for development tools
✅ Test on different screen sizes

### Next Steps

1. **Test the UI flow** - Register → Login → Dashboard → Tasks
2. **Customize styling** - Update colors/fonts in `assets/styles.css`
3. **Add mock data** - Use `components/mock_data.py` for testing
4. **Connect backend** - Update `BASE_URL` in `components/api.py`

Happy coding! 🚀
