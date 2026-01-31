from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os
import shutil
import json
import time
import random
import sys
from typing import List, Optional

# Core Modules
from src.core.pdf_processor import PDFProcessor
from src.core.gemini_service import GeminiService
from src.db.db_manager import DBManager
from src.core.test_generator import TestGenerator
from src.core.desktop_utils import send_notification

app = FastAPI(title="TestGen Pro")

# --- Services ---
pdf_processor = PDFProcessor()
gemini_service = GeminiService()
db_manager = DBManager()
test_generator = TestGenerator()

# --- Config ---
def get_base_path():
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_path()
# If we are in MEIPASS, ASSETS_DIR is directly inside it if we bundled it that way
# Let's adjust based on common PyInstaller structures
if hasattr(sys, '_MEIPASS'):
    ASSETS_DIR = os.path.join(BASE_DIR, "src", "assets", "web")
    STATIC_IMG_DIR = os.path.join(BASE_DIR, "assets", "questions")
else:
    ASSETS_DIR = os.path.join(BASE_DIR, "assets", "web")
    STATIC_IMG_DIR = os.path.join(BASE_DIR, "..", "assets", "questions")

# Ensure directories exist
os.makedirs(STATIC_IMG_DIR, exist_ok=True)

# --- Mount Static Files ---
# Mounts 'src/assets/web' to '/static' for CSS/JS
app.mount("/static", StaticFiles(directory=ASSETS_DIR), name="static")
# Mounts 'assets/questions' to '/images' for Question Images
app.mount("/images", StaticFiles(directory=STATIC_IMG_DIR), name="images")

templates = Jinja2Templates(directory=os.path.join(ASSETS_DIR, "pages"))

# --- Page Routes ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request, "active_page": "dashboard"})

@app.get("/question_bank.html", response_class=HTMLResponse)
async def page_bank(request: Request):
    return templates.TemplateResponse("question_bank.html", {"request": request, "active_page": "question_bank"})

@app.get("/test_generator.html", response_class=HTMLResponse)
async def page_generator(request: Request):
    return templates.TemplateResponse("test_generator.html", {"request": request, "active_page": "test_generator"})

@app.get("/archive.html", response_class=HTMLResponse)
async def page_archive(request: Request):
    return templates.TemplateResponse("archive.html", {"request": request, "active_page": "archive"})

@app.get("/pdf_upload.html", response_class=HTMLResponse)
async def page_pdf_upload(request: Request):
    return templates.TemplateResponse("pdf_upload.html", {"request": request, "active_page": "pdf_upload"})

# --- API Routes ---

@app.get("/api/questions")
async def get_questions():
    questions = db_manager.get_all_questions()
    q_list = []
    for q in questions:
        # DB Schema: ID, TEXT, IMAGE_PATH, SUBJECT, DIFFICULTY, GRADE_LEVEL (Based on previous assumption)
        # We need to map local path to URL path
        img_path = q[2]
        img_url = ""
        if img_path:
            filename = os.path.basename(img_path)
            img_url = f"/images/{filename}"

        q_dict = {
            "id": q[0],
            "text": q[1],
            "image": img_url,
            "subject": q[3] if len(q) > 3 else "Genel",
            "difficulty": q[4] if len(q) > 4 else "Bilinmiyor",
            "grade_level": q[5] if len(q) > 5 else "",
        }
        q_list.append(q_dict)
    return q_list

@app.delete("/api/questions/{q_id}")
async def delete_question(q_id: str):
    try:
        db_manager.delete_question(q_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        # Save uploaded file momentarily
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process PDF (This logic mirrors main_modern.py)
        # TODO: This is blocking. In production, use background tasks.
        # For local app, it's acceptable but UI will spin.
        images = pdf_processor.convert_pdf_to_images(temp_path)
        
        # Note: This loop might need async adaptation or run in threadpool
        # But for now keeping it simple as per "Local App" requirement
        for img_path in images:
            questions_data = gemini_service.analyze_page(img_path)
            for idx, q_data in enumerate(questions_data):
                q_id_file = f"{os.path.basename(img_path)}_{idx}"
                out_path = os.path.join(STATIC_IMG_DIR, f"{q_id_file}.png")
                
                pdf_processor.crop_question(img_path, q_data['coordinates'], out_path)
                
                db_manager.add_question(
                    text=q_data['text'], 
                    image_path=out_path,
                    subject=q_data.get('subject'),
                    grade_level=q_data.get('grade_level'),
                    difficulty=q_data.get('difficulty')
                )
        
        # Cleanup
        os.remove(temp_path)
        
        send_notification("İşlem Tamamlandı", "PDF başarıyla işlendi ve sorular bankaya eklendi.")
        return {"status": "success", "message": "PDF processed successfully"}
    except Exception as e:
        print(f"Upload Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

from pydantic import BaseModel

class GenerateTestRequest(BaseModel):
    title: str
    question_ids: List[str]

@app.post("/api/generate-test")
async def generate_test(req: GenerateTestRequest):
    try:
        if not req.question_ids:
            raise HTTPException(status_code=400, detail="No questions selected")
            
        # Fetch all questions to filter
        all_questions = db_manager.get_all_questions()
        # Filter selected questions and keep tuple format for generator
        # DB: (id, text, image_path, subject, diff, grade)
        # We need to preserve this order for TestGenerator (expects q[2] as image)
        selected_questions = [q for q in all_questions if str(q[0]) in req.question_ids]
        
        if not selected_questions:
            raise HTTPException(status_code=404, detail="Selected questions not found")

        filename = f"test_{int(time.time())}.pdf"
        output_path = os.path.join(STATIC_IMG_DIR, filename) # Saving in static dir to serve it
        
        test_generator.generate_pdf(req.title, selected_questions, output_path)
        
        return {
            "status": "success", 
            "url": f"/images/{filename}",
            "filename": filename
        }
    except Exception as e:
        print(f"Generation Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class GenerateRandomTestRequest(BaseModel):
    title: str
    subject: str
    difficulty: str
    count: int

@app.post("/api/generate-random-test")
async def generate_random_test(req: GenerateRandomTestRequest):
    try:
        all_questions = db_manager.get_all_questions()
        # Filter by subject if specified (and not 'All')
        filtered = all_questions
        if req.subject and req.subject != "All":
            filtered = [q for q in filtered if q[3] == req.subject]
            
        # Filter by difficulty
        # Map frontend values (1-5) to DB values (Kolay, Orta, Zor) if needed
        # Assuming frontend sends compatible strings or we map them.
        # Let's map for robustness: 
        # 1-2: Kolay, 3: Orta, 4-5: Zor
        diff_map = {
            "1": "Kolay", "2": "Kolay",
            "3": "Orta", 
            "4": "Zor", "5": "Zor"
        }
        target_diff = diff_map.get(req.difficulty, "Orta")
        
        # Priority filter: Try to match difficulty, if not enough, take mixed
        perfect_matches = [q for q in filtered if q[4] == target_diff]
        
        import random
        selected_questions = []
        
        if len(perfect_matches) >= req.count:
            selected_questions = random.sample(perfect_matches, req.count)
        else:
            # Fill with others
            others = [q for q in filtered if q[4] != target_diff]
            remainder = req.count - len(perfect_matches)
            if len(others) >= remainder:
                 selected_questions = perfect_matches + random.sample(others, remainder)
            else:
                 selected_questions = perfect_matches + others # Take all available

        if not selected_questions:
             raise HTTPException(status_code=404, detail="No questions found matching criteria")

        filename = f"auto_test_{int(time.time())}.pdf"
        output_path = os.path.join(STATIC_IMG_DIR, filename)
        
        test_generator.generate_pdf(req.title, selected_questions, output_path)
        
        return {
            "status": "success", 
            "url": f"/images/{filename}",
            "filename": filename,
            "question_count": len(selected_questions)
        }
    except Exception as e:
        print(f"Random Generation Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tests")
async def list_tests():
    try:
        files = os.listdir(STATIC_IMG_DIR)
        test_files = [f for f in files if f.endswith(".pdf")]
        
        result = []
        for f in test_files:
            file_path = os.path.join(STATIC_IMG_DIR, f)
            stats = os.stat(file_path)
            
            result.append({
                "filename": f,
                "url": f"/images/{f}",
                "date": stats.st_mtime, # Epoch time
                "size": stats.st_size
            })
            
        # Sort by date descending
        result.sort(key=lambda x: x['date'], reverse=True)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats():
    try:
        questions = db_manager.get_all_questions()
        files = os.listdir(STATIC_IMG_DIR)
        tests = [f for f in files if f.endswith(".pdf")]
        
        return {
            "total_questions": len(questions),
            "total_tests": len(tests)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    import time
    uvicorn.run("src.server:app", host="127.0.0.1", port=8000, reload=True)
