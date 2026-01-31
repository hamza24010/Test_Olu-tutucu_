import os
import platform
import shutil
import subprocess
import sys

# Configuration
SCRIPT_NAME = "engine.py"
APP_NAME = "engine"
TAURI_BIN_DIR = "../src-tauri/binaries"

def clean():
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    spec_file = f"{APP_NAME}.spec"
    if os.path.exists(spec_file):
        os.remove(spec_file)

def get_target_name():
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == "windows":
        return f"{APP_NAME}-x86_64-pc-windows-msvc.exe"
    elif system == "linux":
        return f"{APP_NAME}-x86_64-unknown-linux-gnu"
    elif system == "darwin": # macOS
        return f"{APP_NAME}-x86_64-apple-darwin"
    else:
        raise Exception(f"Unsupported platform: {system}")

def build():
    print(f"Building {APP_NAME} for {platform.system()}...")
    
    # Check if pyinstaller is installed
    try:
        subprocess.run(["pyinstaller", "--version"], check=True, stdout=subprocess.DEVNULL)
    except:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Build command
    # --onefile: Create a single executable
    # --name: Executable name
    # --hidden-import: Explicitly include hidden modules (often needed for google-generativeai, reportlab, etc.)
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--onefile",
        "--name", APP_NAME,
        "--hidden-import", "google.generativeai",
        "--hidden-import", "reportlab",
        "--hidden-import", "pypdf",
        "--hidden-import", "pdf2image",
        "--hidden-import", "PIL", # Pillow
        SCRIPT_NAME
    ]
    
    subprocess.check_call(cmd)
    
    # Move to Tauri binaries folder
    dist_file = os.path.join("dist", APP_NAME + (".exe" if platform.system().lower() == "windows" else ""))
    target_name = get_target_name()
    
    os.makedirs(TAURI_BIN_DIR, exist_ok=True)
    target_path = os.path.join(TAURI_BIN_DIR, target_name)
    
    shutil.copy2(dist_file, target_path)
    print(f"Build successful! Binary moved to: {target_path}")

if __name__ == "__main__":
    clean()
    build()
