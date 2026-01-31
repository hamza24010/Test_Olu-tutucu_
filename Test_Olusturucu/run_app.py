import uvicorn
import webbrowser
import threading
import time
import os
import sys

def start_server():
    # Run the uvicorn server
    # host="0.0.0.0" makes it accessible on local network too if needed
    uvicorn.run("src.server:app", host="127.0.0.1", port=8000, log_level="info")

def open_browser():
    time.sleep(2) # Wait for server to start
    webbrowser.open("http://127.0.0.1:8000/question_bank.html")

if __name__ == "__main__":
    # Start server in a separate thread so we can open browser
    # Actually uvicorn blocks, so we open browser in thread and run uvicorn in main
    threading.Thread(target=open_browser, daemon=True).start()
    
    print("🚀 Test Oluşturucu Web Arayüzü Başlatılıyor...")
    print("👉 http://127.0.0.1:8000 adresine gidiliyor...")
    
    start_server()
