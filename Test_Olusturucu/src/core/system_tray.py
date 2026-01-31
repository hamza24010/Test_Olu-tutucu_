import pystray
from PIL import Image
import threading
import os

def create_tray(on_exit):
    """Creates a system tray icon."""
    try:
        icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icon.png")
        if not os.path.exists(icon_path):
            # Fallback if icon doesn't exist
            image = Image.new('RGB', (64, 64), color=(19, 91, 236))
        else:
            image = Image.open(icon_path)

        def exit_action(icon, item):
            icon.stop()
            on_exit()

        menu = pystray.Menu(
            pystray.MenuItem('Aç', lambda: None), # PyWebView handles showing
            pystray.MenuItem('Çıkış', exit_action)
        )

        icon = pystray.Icon("TestGen", image, "TestGen Pro", menu)
        
        # Start tray in a separate thread so it doesn't block
        def safe_run():
            try:
                icon.run()
            except Exception:
                # Silently fail on systems that don't support system tray (like GNOME without extensions)
                pass

        threading.Thread(target=safe_run, daemon=True).start()
    except Exception:
        pass
