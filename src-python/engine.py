import os
import sys
import json
import base64
import argparse
import google.generativeai as genai
from pdf2image import convert_from_path
from dotenv import load_dotenv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from io import BytesIO

# Load Environment Variables
# Handle PyInstaller temporary path
if hasattr(sys, '_MEIPASS'):
    script_dir = sys._MEIPASS
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))

env_path = os.path.join(script_dir, '.env')
load_dotenv(env_path)

# Fallback: Check local dir if not found in bundle (dev mode priority)
if not os.getenv("GEMINI_API_KEY"):
     local_env = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
     load_dotenv(local_env)

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def log_debug(msg):
    # Optional: Log to a file if needed
    pass

def run_analysis(pdf_path):
    if not api_key:
        print(json.dumps({"type": "error", "message": "API Key missing"}))
        sys.stdout.flush()
        return

    try:
        model = genai.GenerativeModel('gemini-2.5-pro')
    except:
        model = genai.GenerativeModel('gemini-1.5-pro')
    
    try:
        # Get total info first (lightweight)
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        
        # Convert pages on demand or in batches would be better for memory, 
        # but for now let's convert all (pdf2image is fastish) or handle 1 by 1 if possible.
        # To avoid heavy memory on huge PDFs, we should convert page by page if possible,
        # but convert_from_path usually loads them. Let's stick to convert_from_path for simplicity
        # but we will emit events.
        pages = convert_from_path(pdf_path, dpi=300)
    except Exception as e:
        print(json.dumps({"type": "error", "message": f"PDF reading failed: {str(e)}"}))
        sys.stdout.flush()
        return

    # Notify Start
    print(json.dumps({"type": "start", "total": total_pages}))
    sys.stdout.flush()

    global_counter = 1

    for page_num, page_image in enumerate(pages):
        try:
            temp_img_path = f"/tmp/page_{page_num}.jpg"
            page_image.save(temp_img_path, "JPEG")
            
            prompt = """
            Görevin: Bu sayfadaki test sorularını ayrıştırmak.
            
            KURALLAR:
            1. Her soruyu (soru numarası, metni, şıkları ve varsa görseli) içine alan BİR DİKDÖRTGEN (Bounding Box) belirle.
            2. Soru numarasını (Örn: "1.", "24.") mutlaka yakala.
            3. Sorunun zorluk seviyesini (1-5 arası) ve konusunu tahmin et.
            
            ÇIKTI FORMATI (JSON):
            {
              "questions": [
                {
                  "number": 1,
                  "text_snippet": "Metin...",
                  "bbox": [ymin, xmin, ymax, xmax],
                  "difficulty": 3,
                  "topic": "Konu Başlığı"
                }
              ]
            }
            NOT: bbox koordinatları 0 ile 1000 arasında normalize edilmiş olmalıdır.
            """
            
            sample_file = genai.upload_file(path=temp_img_path, display_name=f"Page {page_num}")
            response = model.generate_content([prompt, sample_file])
            
            # Parse JSON
            text = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(text)
            
            width, height = page_image.size
            page_questions = []
            
            for q in data.get("questions", []):
                # Cut Image
                bbox = q["bbox"]
                ymin, xmin, ymax, xmax = bbox
                
                left = xmin * width / 1000
                top = ymin * height / 1000
                right = xmax * width / 1000
                bottom = ymax * height / 1000
                
                # Crop
                question_img = page_image.crop((left, top, right, bottom))
                
                save_dir = os.path.join(script_dir, "extracted_questions")
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, f"q_{global_counter}.jpg")
                question_img.save(save_path, "JPEG")
                
                # Base64
                buffered = BytesIO()
                question_img.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                base64_data = f"data:image/jpeg;base64,{img_str}"
                
                page_questions.append({
                    "id": f"q_{global_counter}",
                    "text": q.get("text_snippet", "") + "...",
                    "image": base64_data,
                    "image_path": str(save_path),
                    "page": page_num + 1,
                    "bbox": [left, top, right, bottom],
                    "difficulty": q.get("difficulty", 3),
                    "topic": q.get("topic", "Genel")
                })
                global_counter += 1
            
            # EMIT PROGRESS EVENT
            event = {
                "type": "progress",
                "current": page_num + 1,
                "total": total_pages,
                "questions": page_questions
            }
            print(json.dumps(event))
            sys.stdout.flush()
                
        except Exception as e:
            # Emit error for this page but continue
            log_debug(f"Page {page_num} Error: {e}")
            print(json.dumps({"type": "log", "message": f"Page {page_num + 1} Error: {str(e)}"}))
            sys.stdout.flush()
            continue

    # Notify Finish
    print(json.dumps({"type": "finish"}))
    sys.stdout.flush()

# --- TEMPLATE ANALYSIS LOGIC ---

def analyze_template_with_gemini(model, image_path):
    prompt = """
    Görevin: Bu PDF şablon sayfasının "Güvenli Baskı Alanını" (Safe Print Area) belirlemek.
    
    Analiz Et:
    1. Üst kısımdaki Logo/Header nerede bitiyor? (Top margin)
    2. Alt kısımdaki Footer/Sayfa numarası nerede başlıyor? (Bottom margin)
    3. Sol ve Sağ kenar süslemeleri var mı? (Left/Right margins)
    
    Çıktı olarak, içerik (sorular) basılabilecek BOŞ alanın koordinatlarını JSON olarak ver.
    Koordinatlar 0-1000 aralığında normalize edilmelidir (0,0 sol üst).
    
    JSON FORMATI:
    {
      "safe_area": {
        "top": 150,    // Header bitişi
        "bottom": 900, // Footer başlangıcı
        "left": 50,
        "right": 950
      }
    }
    """
    try:
        sample_file = genai.upload_file(path=image_path, display_name="Template Page")
        response = model.generate_content([prompt, sample_file])
        text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        return data.get("safe_area", {"top": 50, "bottom": 950, "left": 50, "right": 950})
    except Exception as e:
        log_debug(f"Gemini Template Error: {e}")
        # Default safe area (standard margins)
        return {"top": 50, "bottom": 950, "left": 50, "right": 950}

def run_template_analysis(pdf_path):
    if not api_key:
        print(json.dumps({"error": "API Key missing"}))
        return

    try:
        model = genai.GenerativeModel('gemini-2.5-pro')
    except:
        model = genai.GenerativeModel('gemini-1.5-pro')

    try:
        # Convert first page to image
        pages = convert_from_path(pdf_path, dpi=150, first_page=1, last_page=1)
        if not pages:
            print(json.dumps({"error": "Empty PDF"}))
            return
            
        temp_path = "/tmp/template_preview.jpg"
        pages[0].save(temp_path, "JPEG")
        
        # Analyze
        safe_area = analyze_template_with_gemini(model, temp_path)
        
        # Return result + preview image base64
        buffered = BytesIO()
        pages[0].save(buffered, format="JPEG", quality=50) # Low quality for UI preview
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        output = {
            "margins": safe_area,
            "preview_base64": f"data:image/jpeg;base64,{img_str}"
        }
        print(json.dumps(output))

    except Exception as e:
        log_debug(f"Template Analysis Error: {e}")
        print(json.dumps({"error": str(e)}))

# --- EXPORT LOGIC ---

def run_export(output_path, image_paths, template_path=None, margins=None):
    # 1. Create content PDF (Questions) in memory
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=A4)
    width, height = A4
    
    # Default Margins (Points) - A4 is approx 595x842 points
    # 0-1000 normalized to Points
    def norm_to_pt_y(val): return height - (val * height / 1000)
    def norm_to_pt_x(val): return val * width / 1000

    if margins:
        # User/AI Provided Margins (0-1000 scale)
        # Top in PDF is Height - TopMargin
        start_y = norm_to_pt_y(margins.get('top', 50))
        end_y = norm_to_pt_y(margins.get('bottom', 950))
        left_margin = norm_to_pt_x(margins.get('left', 50))
        right_margin = norm_to_pt_x(margins.get('right', 950))
        
        # Validation
        if start_y < end_y: start_y, end_y = end_y, start_y # Ensure start > end (Coordinate system)
    else:
        # Defaults
        if template_path:
            start_y = height - 120
            end_y = 50
            left_margin = 50
            right_margin = width - 50
        else:
            start_y = height - 50
            end_y = 50
            left_margin = 50
            right_margin = width - 50
            
    current_y = start_y
    available_width = right_margin - left_margin
    col_width = available_width / 2 - 10 # Gap
    
    current_col = 0
    
    # Title (Only if no template)
    if not template_path:
        c.setFont("Helvetica-Bold", 16)
        c.drawString(left_margin, height - 30, "Test Oluşturucu - Deneme Sınavı")
        c.line(left_margin, height - 35, width - 50, height - 35)
    
    q_num = 1

    for img_path in image_paths:
        if not os.path.exists(img_path):
            continue
            
        try:
            img = ImageReader(img_path)
            img_w, img_h = img.getSize()
            aspect = img_h / float(img_w)
            
            display_w = col_width
            display_h = display_w * aspect
            
            # Check limits
            if current_y - display_h < end_y:
                if current_col == 0:
                    current_col = 1
                    current_y = start_y
                else:
                    c.showPage() # Create new page
                    current_col = 0
                    current_y = start_y
            
            x_pos = left_margin if current_col == 0 else (left_margin + col_width + 20)
            
            c.setFont("Helvetica-Bold", 12)
            c.drawString(x_pos, current_y - 12, f"{q_num}.")
            
            c.drawImage(img, x_pos + 20, current_y - display_h, width=display_w - 20, height=display_h)
            
            current_y -= (display_h + 30)
            q_num += 1
            
        except Exception as ex:
             log_debug(f"Image Export Error: {ex}")
             
    c.save()
    packet.seek(0)
    
    # 2. Merge with Template (if exists)
    if template_path and os.path.exists(template_path):
        try:
            from pypdf import PdfReader, PdfWriter, PageObject, Transformation
            
            new_pdf = PdfReader(packet)
            template_pdf = PdfReader(template_path)
            template_page = template_pdf.pages[0] # Use first page as template
            
            output = PdfWriter()
            
            for page_index in range(len(new_pdf.pages)):
                content_page = new_pdf.pages[page_index]
                
                # Clone template for this page
                base_page = PageObject.create_blank_page(width=width, height=height)
                base_page.merge_page(template_page) # Background
                base_page.merge_page(content_page)  # Foreground (Questions)
                
                output.add_page(base_page)
                
            with open(output_path, "wb") as f_out:
                output.write(f_out)
                
        except Exception as e:
            log_debug(f"Template Merge Error: {e}")
            with open(output_path, "wb") as f:
                f.write(packet.getbuffer())
    else:
        with open(output_path, "wb") as f:
            f.write(packet.getbuffer())

    print(json.dumps({"status": "success", "path": output_path}))


# --- SOLVER LOGIC ---

def run_solver(questions_json):
    if not api_key:
        print(json.dumps({"error": "API Key missing"}))
        return

    try:
        data = json.loads(questions_json)
        # data is List of {id, text, image_path}
        
        try:
            model = genai.GenerativeModel('gemini-2.5-pro')
        except:
            model = genai.GenerativeModel('gemini-1.5-pro')

        prompt = """
        Görevin: Aşağıdaki test sorularını çözmek ve bir CEVAP ANAHTARI oluşturmak.
        
        KURALLAR:
        1. Her soru için doğru şıkkı (A, B, C, D, E) belirle.
        2. Eğer şık yoksa veya açık uçluysa cevabı kısa ve net yaz (Örn: "25", "x=5").
        3. Çıktıyı SADECE aşağıdaki JSON formatında ver, başka hiçbir açıklama yapma.
        
        ÇIKTI FORMATI (JSON):
        {
          "answers": [
            {"q_num": 1, "answer": "A"},
            {"q_num": 2, "answer": "C", "detail": "Çözüm özeti (opsiyonel)"}
          ]
        }
        """
        
        content_parts = [prompt]
        
        for i, q in enumerate(data):
            q_text = f"\nSoru {i+1}:\n{q.get('text', '')}"
            content_parts.append(q_text)
            
            # Add Image if exists
            img_path = q.get('image_path')
            if img_path and os.path.exists(img_path):
                 file_ref = genai.upload_file(path=img_path, display_name=f"Q{i+1}")
                 content_parts.append(file_ref)
        
        response = model.generate_content(content_parts)
        text = response.text.replace("```json", "").replace("```", "").strip()
        
        try:
            result = json.loads(text)
            print(json.dumps(result)) # Output to stdout
         except Exception as e:
            log_debug(f"Solver Error: {e}")
            print(json.dumps({"error": str(e)}))

def main():
    # Windows Check: Poppler is required for pdf2image
    if sys.platform == "win32":
        import subprocess
        try:
            subprocess.run(["pdftoppm", "-h"], capture_output=True)
        except FileNotFoundError:
            print(json.dumps({
                "type": "error", 
                "message": "Sistemde 'Poppler' bulunamadı. Lütfen Poppler kütüphanesini kurun ve PATH değişkenine ekleyin veya uygulama dizinine kopyalayın."
            }))
            sys.exit(1)

    parser = argparse.ArgumentParser(description="AI Test Engine")
    subparsers = parser.add_subparsers(dest="command")
    
    parser_analyze = subparsers.add_parser("analyze")
    parser_analyze.add_argument("pdf_path")
    
    parser_export = subparsers.add_parser("export")
    parser_export.add_argument("output_path")
    parser_export.add_argument("--images", nargs="+", required=True)
    parser_export.add_argument("--template", required=False, help="Path to PDF template file")
    parser_export.add_argument("--margins", required=False, help="JSON string of margins {top, bottom, left, right}")

    parser_tpl = subparsers.add_parser("analyze-template")
    parser_tpl.add_argument("pdf_path")
    
    # NEW SOLVER COMMAND
    parser_solve = subparsers.add_parser("solve")
    parser_solve.add_argument("--questions", required=True, help="JSON string of questions list")

    if len(sys.argv) > 1 and sys.argv[1] not in ["analyze", "export", "analyze-template", "solve"]:
         run_analysis(sys.argv[1])
         return

    args = parser.parse_args()
    
    if args.command == "analyze":
        run_analysis(args.pdf_path)
    elif args.command == "analyze-template":
        run_template_analysis(args.pdf_path)
    elif args.command == "export":
        margins = None
        if args.margins:
            try:
                margins = json.loads(args.margins)
            except:
                pass
        run_export(args.output_path, args.images, args.template, margins)
    elif args.command == "solve":
         run_solver(args.questions)
    else:
        parser.print_help()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)
