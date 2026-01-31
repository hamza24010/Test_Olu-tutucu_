import google.generativeai as genai
import os
import json
import time
from dotenv import load_dotenv

load_dotenv()

class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Uyarı: GEMINI_API_KEY bulunamadı!")
        genai.configure(api_key=api_key)
        # Kullanıcının listesinde bulunan en güçlü modeli seçiyoruz
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        self.chat = None

    def start_new_session(self):
        """Yeni bir analiz oturumu başlatır."""
        self.chat = self.model.start_chat(history=[])

    def analyze_chunk(self, image_paths):
        """Gemini 2.5 Pro ile Gelişmiş 2 Aşamalı Analiz ve Doğrulama."""
        prompt = """
        Görevin: Gönderilen sayfa görüntülerindeki soruları %100 hassasiyetle ayıklamak ve sınıflandırmak.
        
        ANALİZ PROTOKOLÜ:
        1. Önce görseli tara ve toplam soru sayısını kesin olarak belirle.
        2. Her soru için en geniş kapsayıcı dikdörtgeni (bounding box) çiz. 
           BU KUTU ŞUNLARI İÇERMELİDİR: Soru numarası, metin, tüm şıklar, soruya ait tüm görseller, tablolar ve şekiller.
        3. Sorunun içeriğini analiz et ve şunları belirle:
           - Ders (Örn: Matematik, Fizik, Tarih)
           - Sınıf Seviyesi (Örn: 9. Sınıf, 10. Sınıf, TYT, AYT)
           - Zorluk Seviyesi (1-5 arası tam sayı; 1: Çok Kolay, 5: Çok Zor)

        ÇIKTI KURALLARI:
        - Yanıtın SADECE aşağıda belirtilen JSON formatında olmalı.
        - JSON dışında hiçbir açıklama veya metin ekleme.
        
        FORMAT:
        {
          "summary": {"total_questions_on_pages": X},
          "questions": [
            {
              "page_index": 0,
              "text": "Soru metninin tamamı...",
              "subject": "Ders Adı",
              "grade_level": "Sınıf Bilgisi",
              "difficulty": 3,
              "coordinates": [ymin, xmin, ymax, xmax]
            }
          ]
        }
        """
        
        try:
            content_parts = [prompt]
            for path in image_paths:
                img = genai.upload_file(path)
                content_parts.append(img)
            
            # 2.5 Pro için chat veya doğrudan generate_content kullanabiliriz
            if self.chat:
                response = self.chat.send_message(content_parts)
            else:
                response = self.model.generate_content(content_parts)
            
            content = response.text
            
            # JSON Temizleme (Markdown bloklarını kaldır)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            data = json.loads(content)
            
            # Doğrulama ve loglama
            detected_list = data.get("questions", [])
            summary_count = data.get("summary", {}).get("total_questions_on_pages", 0)
            
            print(f"Gemini 2.5 Pro: {summary_count} soru tespit edildi, {len(detected_list)} veri döndü.")
            
            return detected_list
                
        except Exception as e:
            print(f"Gemini 2.5 Pro API hatası: {e}")
            return []

    def analyze_page(self, image_path):
        """Geriye dönük uyumluluk için tek sayfa analizi (analyze_chunk kullanır)."""
        return self.analyze_chunk([image_path])

