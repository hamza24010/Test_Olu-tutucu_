import subprocess
import os
import shutil
import sys

def build():
    # 1. Eski build klasörlerini temizle
    print("Temizlik yapılıyor...")
    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    
    spec_file = "TestGenPro.spec"
    if os.path.exists(spec_file):
        os.remove(spec_file)

    # 2. PyInstaller Komutu (Hata riskini sıfırlayan versiyon)
    # Bağımlılıkları tek tek zorla (collect-all)
    cmd = [
        "pyinstaller",
        "--noconsole",
        "--onefile", 
        "--name=TestGenPro",
        "--clean",
        # Assetlerin yolları (Windows'ta ; kullanılır)
        "--add-data=src/assets/web;src/assets/web",
        "--add-data=assets/questions;assets/questions",
        # Kritik kütüphaneleri tamamen topla
        "--collect-all=webview",
        "--collect-all=fastapi",
        "--collect-all=uvicorn",
        "--collect-all=jinja2",
        "--collect-all=pystray",
        "--collect-all=plyer",
        "--collect-all=google", 
        "--collect-all=pdf2image",
        "--collect-all=PIL",
        "--collect-all=reportlab", # PDF oluşturma için kritik
        # Gizli importları zorla
        "--hidden-import=pdf2image",
        "--hidden-import=PIL",
        "--hidden-import=PIL._imaging",
        "--hidden-import=reportlab",
        "--hidden-import=reportlab.graphics.barcode.common",
        "--hidden-import=reportlab.graphics.barcode.code128",
        "--hidden-import=uvicorn.logging",
        "--hidden-import=uvicorn.loops",
        "--hidden-import=uvicorn.protocols",
        "--hidden-import=uvicorn.lifespan",
        "--hidden-import=fastapi.openapi",
        "src/main_desktop.py"
    ]

    # Icon varsa ekle
    icon_path = "src/assets/icon.png"
    if os.path.exists(icon_path):
        cmd.insert(4, f"--icon={icon_path}")

    print("PyInstaller build (Windows Modu) başlatılıyor...")
    print("Bu işlem tüm kütüphaneler paketlendiği için biraz uzun sürebilir (2-5 dk)...")
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n" + "="*30)
        print("BAŞARI: Build tamamlandı!")
        print("Dosyanız: dist/TestGenPro.exe")
        print("="*30)
    else:
        print("\nHATA: Derleme sırasında bir sorun oluştu.")

if __name__ == "__main__":
    build()
