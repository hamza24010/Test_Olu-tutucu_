# PLAN-yolo-integration

> **Goal:** Integrate a custom trained YOLO model (`best.pt`) as an offline-capable, image-based question extraction engine alongside the existing Gemini AI.

---

## 🏗️ Phase 1: Infrastructure & Dependencies (Architecture)
- [ ] **Model Management**
    - Create directory `src-python/models/`.
    - Move `best.pt` from root to `src-python/models/best.pt`.
- [ ] **Python Dependencies**
    - Update `src-python/build_engine.py` (or requirements) to include:
        - `ultralytics` (YOLO)
        - `torch` (Target CPU version for broader compatibility and reasonable size, despite user allowance).
    - Ensure PyInstaller hooks are configured for `ultralytics`.

## 🐍 Phase 2: Python Engine Implementation (Backend)
- [ ] **YOLO Logic**
    - Modify `src-python/engine.py`:
        - Load `best.pt` model on startup (lazy loading preferred to save RAM if not used).
        - Implement `analyze_page_with_yolo(image_path)` function.
        - **Logic:** Run inference -> Get Bounding Boxes -> Crop images -> Save to `APP_DATA_DIR/extracted_questions`.
        - **Output:** Format must match existing JSON structure.
            - `text`: Set to placeholder (e.g., *"Görsel Soru (OCR Yok)"*).
            - `bbox`: Normalized 0-1000 coordinates.
            - `difficulty`: Default to 3.
            - `topic`: Default to "Genel".
- [ ] **Engine Selection Logic**
    - Update `main` and `run_analysis` in `engine.py` to accept an `--engine` argument (`gemini` or `yolo`).

## ⚙️ Phase 3: Rust & Tauri Bridge
- [ ] **Settings Storage**
    - Database `settings` table already exists.
    - Add keys: `ai_engine` (values: "gemini", "yolo").
- [ ] **Tauri Command Update**
    - Update `analyze_pdf` command in `lib.rs`:
        - Read `ai_engine` setting from DB.
        - Pass `--engine yolo` or `--engine gemini` argument to the Python sidecar.

## 🖥️ Phase 4: Frontend (UI/UX)
- [ ] **Settings UI**
    - Update `src/components/views/SettingsView.tsx`:
        - Add "Ayrıştırma Motoru" (Extraction Engine) selector.
        - Options: "Google Gemini 2.5 (Önerilen/Yavaş/Detaylı)" vs "YOLOv8 Yerel (Hızlı/Sadece Görsel)".
        - Add warning for YOLO: *"Bu mod sadece soruların resmini alır, içindeki metni okumaz."*

## ✅ Phase 5: Verification & Build
- [ ] **Test Flow**
    - Switch to YOLO in settings.
    - Upload PDF.
    - Verify logs show YOLO loading.
    - Verify questions appear in UI (as images).
- [ ] **Windows Build**
    - Verify `best.pt` is correctly bundled in the `.exe` via PyInstaller (`--add-data`).

---

## 📝 User Notes
- Using Strategy C: Save images only, no OCR text.
- Build size will increase significantly due to PyTorch.
- `best.pt` is the source of truth for detection.
