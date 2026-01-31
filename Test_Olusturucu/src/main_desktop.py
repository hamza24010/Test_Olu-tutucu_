import os
import sys
import threading
import time
import webview
import uvicorn

# Fix path issue for local imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.server import app
from src.core.system_tray import create_tray

def start_server():
    """Starts the FastAPI server in a dedicated thread."""
    uvicorn.run(app, host="127.0.0.1", port=21024, log_level="error")

def on_exit():
    """Cleanup when application exits."""
    # Add any cleanup logic here if needed
    os._exit(0)

def main():
    # 0. Set Wayland compatibility for Qt on Linux
    if sys.platform == 'linux':
        os.environ['QT_QPA_PLATFORM'] = 'wayland;xcb'

    # 0. Start Tray Icon (Only on Windows for now to avoid Linux/GNOME crashes)
    if sys.platform == 'win32':
        create_tray(on_exit)
    else:
        print("Sistem Tepsisi: Linux üzerinde geliştirme modunda devre dışı bırakıldı.")

    # 1. Start FastAPI server in the background
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # 2. Give the server a moment to boot up
    time.sleep(1.5)

    # 3. Create the desktop window
    # We use a non-standard port (21024) to avoid conflicts
    window = webview.create_window(
        'TestGen Pro - Desktop', 
        'http://127.0.0.1:21024',
        width=1280,
        height=800,
        min_size=(1000, 700),
        confirm_close=True
    )

    # 4. Start the application
    webview.start(debug=False)

if __name__ == '__main__':
    main()
