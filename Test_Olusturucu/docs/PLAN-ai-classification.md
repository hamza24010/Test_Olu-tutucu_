# Plan: AI Question Classification & Grading

## Overview
Enhance the existing "Test Oluşturucu" (PyQt6) application to automatically classify questions extracted from PDFs.
The AI (Gemini 2.5) will determine:
1.  **Ders (Subject)**: e.g., Matematik, Fizik.
2.  **Sınıf (Grade Level)**: e.g., 9. Sınıf, 10. Sınıf.
3.  **Zorluk (Difficulty)**: 1-5 scale.

This feature applies ONLY to newly scanned questions. The UI will be updated to display and allow manual editing of these fields.

## Project Type
**Desktop Application (PyQt6)** with Python Backend & SQLite.

## Success Criteria
- [ ] Database supports `subject`, `grade_level`, `difficulty` columns.
- [ ] Gemini API prompt extracts these 3 fields accurately in JSON.
- [ ] `process_pdf` correctly saves these fields to DB.
- [ ] Main Window displays these fields in the question list or details view.
- [ ] Users can manually edit these fields if AI makes a mistake.
- [ ] "Grade Level" is standardized (e.g., integer 1-12 or string "9. Sınıf").

## Tech Stack
- **Language**: Python 3.10+
- **GUI**: PyQt6
- **Database**: SQLite3
- **AI**: Google Gemini 2.5 Pro

## File Structure
No major structure changes. Updates to existing files:
- `src/db/db_manager.py`: Schema update.
- `src/core/gemini_service.py`: Prompt engineering.
- `main_modern.py`: Controller logic update.
- `src/ui/`: (If split) or modify `ModernMainWindow` (if inline, assumed based on code style).

## Task Breakdown

### Phase 1: Database & Backend (P1)
- **Task 1.1: Database Migration**
    - Agent: `backend-specialist`
    - Desc: Modify `DBManager`'s `create_tables` (create new migration function or updated init) to add `subject`, `grade_level`, `difficulty` columns.
    - Input: `src/db/db_manager.py`
    - Output: Updated `questions` table schema.
    - Verify: `sqlite3 data/test_olusturucu.db ".schema questions"` shows new columns.

- **Task 1.2: Update DB Insert Logic**
    - Agent: `backend-specialist`
    - Desc: Update `add_question` method to accept new arguments.
    - Input: `src/db/db_manager.py`
    - Output: `add_question` handles optional new fields.
    - Verify: Calling `add_question` with new fields saves data correctly.

### Phase 2: AI Integration (P1)
- **Task 2.1: Prompt Engineering**
    - Agent: `backend-specialist`
    - Desc: Update `GeminiService.analyze_chunk` prompt to request strict JSON with new fields: `subject` (string), `grade_level` (string/int), `difficulty` (int 1-5).
    - Input: `src/core/gemini_service.py`
    - Output: Improved prompt and JSON parsing logic.
    - Verify: Run script with a sample image, check if JSON contains new keys.

### Phase 3: Application Logic (P2)
- **Task 3.1: Connect Controller**
    - Agent: `frontend-specialist` (acting as GUI dev)
    - Desc: Update `process_pdf` in `main_modern.py` to extract new fields from Gemini response and pass to `db_manager.add_question`.
    - Input: `main_modern.py`
    - Output: New data flows from `gemini_service` to `db_manager`.
    - Verify: Scan a PDF, check DB to see filled columns.

### Phase 4: UI Updates (P2)
- **Task 4.1: Display Metadata**
    - Agent: `frontend-specialist` (PyQt)
    - Desc: Update `load_questions_to_list` in `main_modern.py` to show "Subject - Grade (Diff: X)" in the list item text.
    - Input: `main_modern.py`
    - Output: List items show richer info.
    - Verify: Run app, list shows tags.

- **Task 4.2: Edit Dialog (Optional/Stretch)**
    - Agent: `frontend-specialist`
    - Desc: Add a double-click event or "Edit" button to modify these fields manually.
    - Input: `main_modern.py`
    - Output: A simple dialog to update Question fields.
    - Verify: Editing a question updates the DB.

## Phase X: Verification
- [ ] Run `pytest` if applicable (currently one test fails/passes).
- [ ] Manual Test: Run app -> Load PDF -> Check if questions have tags.
- [ ] Manual Test: Check DB persistence.

