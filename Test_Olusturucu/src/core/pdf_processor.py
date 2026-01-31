import os
from pdf2image import convert_from_path
from PIL import Image

class PDFProcessor:
    def __init__(self, output_dir='data/temp_pages'):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def convert_pdf_to_images(self, pdf_path, dpi=300):
        """PDF dosyasını sayfa sayfa görsellere dönüştürür."""
        print(f"PDF dönüştürülüyor: {pdf_path}")
        try:
            pages = convert_from_path(pdf_path, dpi=dpi)
            image_paths = []
            
            for i, page in enumerate(pages):
                image_name = f"page_{i+1}.png"
                image_path = os.path.join(self.output_dir, image_name)
                page.save(image_path, 'PNG')
                image_paths.append(image_path)
                print(f"Kaydedildi: {image_path}")
                
            return image_paths
        except Exception as e:
            print(f"Dönüştürme hatası: {e}")
            return []

    def crop_question(self, page_image_path, coords, output_path, padding=10):
        """Belirtilen koordinatlara göre soruyu biraz pay bırakarak kırpar."""
        try:
            with Image.open(page_image_path) as img:
                width, height = img.size
                
                # Pay ekle (0-1000 arası koordinatlara 10 birim yani %1 ekliyoruz)
                ymin = max(0, coords[0] - padding)
                xmin = max(0, coords[1] - padding)
                ymax = min(1000, coords[2] + padding)
                xmax = min(1000, coords[3] + padding)
                
                # Piksele çevir
                left = xmin * width / 1000
                top = ymin * height / 1000
                right = xmax * width / 1000
                bottom = ymax * height / 1000
                
                cropped_img = img.crop((left, top, right, bottom))
                cropped_img.save(output_path)
                return output_path
        except Exception as e:
            print(f"Kırpma hatası: {e}")
            return None
