from plyer import notification
import os

def send_notification(title, message):
    """Sends a desktop notification."""
    try:
        notification.notify(
            title=title,
            message=message,
            app_name='TestGen Pro',
            app_icon=None, # You can add a path to .ico file here later
            timeout=5
        )
    except Exception as e:
        print(f"Notification error: {e}")

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
