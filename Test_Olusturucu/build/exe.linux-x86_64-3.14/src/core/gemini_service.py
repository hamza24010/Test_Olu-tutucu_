import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Uyarı: GEMINI_API_KEY bulunamadı!")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def analyze_page(self, image_path):
        """Sayfadaki soruları tespit eder ve metin/koordinat döndürür."""
        prompt = """
        Sen profesyonel bir test editörüsün. Bu sayfa görüntüsündeki her bir soruyu tek tek tespit et.
        
        KURALLAR:
        1. Her bir soru için: soru numarası, soru metni, tüm şıklar (A, B, C, D, E) ve varsa sorunun yanındaki/üstündeki şekil, grafik veya görsellerin TAMAMINI kapsayan bir dikdörtgen koordinat belirle.
        2. Koordinatlar [ymin, xmin, ymax, xmax] formatında olmalı (0-1000 arası normalize edilmiş).
        3. 'text' alanına sorunun metnini ve şıklarını aynen yaz.
        4. Sadece geçerli bir JSON listesi döndür.
        
        Örnek Çıktı:
        [
          {"text": "1. Soru... A) şık B) şık...", "coordinates": [50, 40, 320, 960]},
          ...
        ]
        """
        
        try:
            # Görseli yükle
            img = genai.upload_file(image_path)
            
            response = self.model.generate_content([prompt, img])
            
            # JSON içeriğini ayıkla
            content = response.text
            # Use regex or simple string find if needed, but let's try direct json parse
            # Gemini sometimes wraps in ```json ... ```
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                 content = content.split("```")[1].split("```")[0].strip()
            
            return json.loads(content)
        except Exception as e:
            print(f"Gemini API hatası: {e}")
            return []
