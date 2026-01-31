# Project Handover & Status Report

**Date:** 2026-01-31
**Project:** Docling Stitch (Test Oluşturucu)
**State:** Feature Complete / Ready for Windows Build

## 1. Project Overview
This application is a Desktop Test Generator built with **Tauri (Rust)**, **React**, and a **Python Sidecar** for AI operations.

## 2. Completed Features
- **PDF Analysis:** Extracts questions from PDFs using Gemini AI (`engine.py`).
- **Test Creation:** Drag & drop questions to create tests.
- **Templates:** Apply custom PDF templates/headers to tests.
- **Student Management:** basic student tracking database.
- **Archive System:**
    - Saves generated tests to SQLite.
    - View past tests and their questions.
    - **Answer Key Generation:** Uses Gemini to solve questions and generate an answer key on demand.
- **Infrastructure:**
    - Python engine is decoupled as a Sidecar.
    - `build_engine.py` script created for PyInstaller packaging.

## 3. Architecture Status
- **Backend (Rust):** `src-tauri/src/lib.rs` and `db.rs`. All Python calls use `app.shell().sidecar()`.
- **AI Engine (Python):** `src-python/engine.py`. Handles Scan, Export, and Solve.
- **Database:** `sqlite.db` (local). Migrations for `tests` and `answer_key` are applied.

## 4. Immediate Next Steps (Windows Migration)
The project is being moved to a Windows environment. The new agent needs to guide the user through:

1.  **Environment Setup:**
    - Install VS C++ Build Tools.
    - Install Rust, Node.js.
    - Install Python 3.10-3.12 (Avoid 3.13+ for now due to PyInstaller issues).

2.  **Sidecar Building (Critical):**
    - Must run `python build_engine.py` in `src-python` to generate `engine-x86_64-pc-windows-msvc.exe`.
    - Verify it is placed in `src-tauri/binaries/`.

3.  **Application Build:**
    - `npm install`
    - `npm run tauri build` to create the MSI installer.

## 5. Known Issues / Notes
- **Python Version:** Use Python 3.12 or lower. 3.14 caused `struct.error` with PyInstaller on Linux.
- **API Key:** `GEMINI_API_KEY` must be set in `.env` (in `src-python/.env` for dev, or injected for prod). The user handles this.

## 6. Commands to Run (On Windows)
Refer to `WINDOWS_BUILD.md` for the exact step-by-step guide.
