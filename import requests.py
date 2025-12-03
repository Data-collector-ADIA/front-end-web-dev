import requests

def check_server():
    try:
        # TODO: perform request here, e.g.:
        # response = requests.get("http://localhost:8000")
        # response.raise_for_status()
        pass
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to server. Please check if backend is running."
    return True, "Server reachable"