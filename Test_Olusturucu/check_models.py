import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

def list_models():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("HATA: .env dosyasında GEMINI_API_KEY bulunamadı!")
        return
    
    genai.configure(api_key=api_key)
    
    print("Mevcut Modeller:")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except Exception as e:
        print(f"Modeller listelenirken hata oluştu: {e}")

if __name__ == "__main__":
    list_models()
