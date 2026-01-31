from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from PIL import Image
import os

class TestGenerator:
    def __init__(self, output_dir='data/tests'):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_pdf(self, test_title, questions, output_path):
        """Seçilen sorulardan iki sütunlu bir PDF oluşturur."""
        if not os.path.isabs(output_path) and not os.path.dirname(output_path):
            output_path = os.path.join(self.output_dir, output_path)
            
        print(f"İki sütunlu PDF oluşturuluyor: {output_path}")
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4
        
        # Kenar boşlukları ve Sütun ayarları
        margin = 1.5 * cm
        col_gap = 1.0 * cm
        col_width = (width - 2 * margin - col_gap) / 2
        
        # Başlık (Sadece ilk sayfada)
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width/2, height - 1.5*cm, test_title)
        
        # Çizgi çek (Sütunlar arasına isteğe bağlı)
        c.setDash(1, 2)
        c.line(width/2, margin, width/2, height - 2.5*cm)
        c.setDash() # Reset
        
        y_positions = [height - 3*cm, height - 3*cm] # Sol ve Sağ sütun için Y
        current_col = 0 # 0: Sol, 1: Sağ
        
        for i, q in enumerate(questions):
            img_path = q[2]
            
            if img_path and os.path.exists(img_path):
                with Image.open(img_path) as img:
                    img_w, img_h = img.size
                    aspect = img_h / img_w
                    
                    display_w = col_width
                    display_h = display_w * aspect
                    
                    # Sayfa/Sütun sonu kontrolü
                    if y_positions[current_col] - display_h < margin:
                        if current_col == 0:
                            current_col = 1 # Sağ sütuna geç
                        else:
                            c.showPage() # Yeni sayfaya geç
                            # Yeni sayfa başlıkları ve çizgisi
                            c.setDash(1, 2)
                            c.line(width/2, margin, width/2, height - margin)
                            c.setDash()
                            current_col = 0
                            y_positions = [height - margin, height - margin]

                    # Koordinatları hesapla
                    x_pos = margin if current_col == 0 else margin + col_width + col_gap
                    
                    # Soru No yaz (isteğe bağlı, resmin üzerine binmesin diye yanına)
                    c.setFont("Helvetica-Bold", 10)
                    c.drawString(x_pos - 0.5*cm if current_col == 0 else x_pos - 0.5*cm, y_positions[current_col] - 0.4*cm, f"{i+1}.")
                    
                    # Resmi çiz
                    c.drawImage(img_path, x_pos, y_positions[current_col] - display_h, width=display_w, height=display_h)
                    y_positions[current_col] -= (display_h + 0.8*cm)
            
        c.save()
        return output_path
