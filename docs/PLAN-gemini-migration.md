# PLAN-gemini-migration.md

## 1. Context & Goal
Migrate the PDF question extraction logic from the legacy `Tes_Olusturucu` project (Gemini 2.5 Pro based) to the current `Test_Olusturucu_Rust_Tauri` project.
Current `engine.py` uses `Docling` which failed to correctly group questions in complex layouts. The goal is to use Gemini's Multimodal Vision capabilities to identify and locate questions with near-human accuracy.

## 2. Architecture Changes

### Remove
- **Docling Library**: Remove `docling`, `docling-core` dependencies (optional to keep but unused).
- **Heuristic Regex Logic**: Replace hardcoded regex parsing (`^\d+`) with AI-driven detection.

### Add
- **Google Generative AI SDK**: `google-generativeai`
- **PDF2Image**: `pdf2image` (Requires `poppler-utils`)
- **Pillow (PIL)**: For image manipulation (already present but will be primary tool).
- **Environment Management**: `.env` file for `GEMINI_API_KEY`.

## 3. Implementation Steps

### Phase 1: Environment Setup
1.  [ ] Install Python dependencies: `pip install google-generativeai pdf2image python-dotenv`.
2.  [ ] Verify `poppler-utils` is installed on the system (required for `pdf2image`).
3.  [ ] Create `.env` file in `src-python/` or root project for API Key storage.

### Phase 2: Refactoring `engine.py`
The new `engine.py` will follow this pipeline:

1.  **PDF Pre-processing**:
    - Convert PDF pages to high-quality images (300 DPI) using `pdf2image`.
    - Save temporary full-page images to `~/Documents/DoclingStitch/temp_pages`.

2.  **Gemini Analysis**:
    - Iterate through page images.
    - Upload each image to Gemini API.
    - Send the "Analyze Protocol" prompt (from `gemini_service.py`) asking for:
        - Bounding Box [ymin, xmin, ymax, xmax] (0-1000 scale)
        - Metadata (Subject, Difficulty, etc.)
    
3.  **Post-Processing**:
    - Parse Gemini's JSON response.
    - **Crop**: Convert normalized coordinates (0-1000) to actual pixels.
    - Crop the question images using `PIL`.
    - Save cropped images to `~/Documents/DoclingStitch/temp_crops`.
    - Encode cropped images to Base64 for immediate frontend display.

4.  **Output**:
    - Print the final list of questions (id, text, image_path, base64) as JSON for Tauri.

### Phase 3: Frontend Integration
- No major changes needed in `App.tsx` if the JSON structure remains compatible (`id`, `text`, `image` fields).
- Ensure `image` field contains the Base64 string for instant loading.

## 4. Verification
- **Success Criteria**:
    - PDF with multi-column layout is correctly parsed.
    - Individual questions are separated (no merging of 2 questions).
    - Images are correctly cropped around the question.
    - No "Question not found" errors.

## 5. Agent Assignment
- **Agent**: `backend-specialist` or `orchestrator`
- **Skills**: `python-patterns`, `api-patterns` (Gemini usage)

---
**Note**: The user must provide a valid `GEMINI_API_KEY`.
