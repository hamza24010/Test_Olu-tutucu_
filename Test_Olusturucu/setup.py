import sys
import os
from cx_Freeze import setup, Executable

# Dependencies
# cx_Freeze should find most, but we list the main ones to be safe
build_exe_options = {
    "packages": [
        "os", "sys", "PyQt6", "pdf2image", "PIL", 
        "google.generativeai", "dotenv", "reportlab",
        "src.core", "src.db"
    ],
    "include_files": [
        "assets",
        "data",
        ".env",
        "src"
    ],
    "excludes": ["tkinter"],
    "optimize": 2
}

# GUI tabanlı (konsol açılmayan) ayarı
base = None
if sys.platform == "win32":
    base = "Win32GUI"

executable = Executable(
    script="main_modern.py",
    base=base,
    icon=None, # İkonunuz varsa buraya ekleyebilirsiniz ekn: "assets/icon.ico"
    target_name="TestOlusturucu.exe" if sys.platform == "win32" else "TestOlusturucu"
)

setup(
    name="Test Olusturucu",
    version="1.0",
    description="Öğretmenler için PDF'den Soru Ayıklama ve Test Oluşturma Uygulaması",
    options={"build_exe": build_exe_options},
    executables=[executable]
)
