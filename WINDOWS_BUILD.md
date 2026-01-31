# Windows Build Guide (Docling Stitch)

This guide explains how to package the application as a standalone `.msi` or `.exe` installer on Windows.

## 1. Prerequisites (Kurulumlar)

Make sure you have the following installed on your Windows machine:

1.  **Microsoft Visual Studio C++ Build Tools:** (Rust ve Python için gerekli)
    *   İndirin: [https://visualstudio.microsoft.com/visual-cpp-build-tools/](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
    *   Kurarken "Desktop development with C++" seçeneğini işaretleyin.
2.  **Rust:**
    *   İndirin: [https://rustup.rs/](https://rustup.rs/) (rustup-init.exe)
3.  **Node.js (LTS):**
    *   İndirin: [https://nodejs.org/](https://nodejs.org/)
4.  **Python (3.10, 3.11 or 3.12):**
    *   **ÖNEMLİ:** Python 3.13 veya 3.14 kullanmayın (PyInstaller ile sorun çıkarabilir).
    *   Kurarken "Add Python to PATH" kutucuğunu MUTLAKA işaretleyin.

## 2. Setup Python Environment (Python Ortamı)

Open `PowerShell` or `Command Prompt` (Terminal) in the project root folder.

```powershell
# 1. Go to python folder
cd src-python

# 2. Create virtual environment
python -m venv .venv

# 3. Activate environment
.\.venv\Scripts\activate

# 4. Install dependencies
pip install google-generativeai python-dotenv pdf2image reportlab pypdf pyinstaller Pillow
```

## 3. Build Sidecar Binary (Sidecar Oluşturma)

We need to convert the Python engine into an executable (`.exe`) that Tauri can use. We have a script for this.

While still inside `src-python` folder and `.venv` is active:

```powershell
python build_engine.py
```

✅ **Success Check:**
Check if this file exists: `src-tauri/binaries/engine-x86_64-pc-windows-msvc.exe`

## 4. Build Application (Uygulamayı Paketleme)

Now, go back to the project root and build the Tauri app.

```powershell
# 1. Return to root
cd ..

# 2. Install frontend packages
npm install

# 3. Build the MSI installer
npm run tauri build
```

## 5. Locate Installer (Kurulum Dosyası)

After the build finishes successfully, you will find your installer here:

`src-tauri/target/release/bundle/msi/DoclingStitch_0.1.0_x64_en-US.msi`

You can run this `.msi` file to install the application on any Windows computer. It includes everything (Python engine, libraries, frontend, etc.). No extra installation is needed for the end user.
