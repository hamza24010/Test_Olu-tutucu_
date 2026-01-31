import sys
import os
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QListWidget, 
                             QHBoxLayout, QMessageBox, QTabWidget, QListWidgetItem)
from PyQt6.QtCore import Qt
from src.core.pdf_processor import PDFProcessor
from src.core.gemini_service import GeminiService
from src.db.db_manager import DBManager
from src.core.test_generator import TestGenerator

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Oluşturucu - Öğretmen Paneli")
        self.setMinimumSize(900, 700)
        
        self.pdf_processor = PDFProcessor()
        self.gemini_service = GeminiService()
        self.db_manager = DBManager()
        self.test_generator = TestGenerator()
        
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # TAB 1: Soru Bankası
        self.bank_tab = QWidget()
        self.setup_bank_tab()
        self.tabs.addTab(self.bank_tab, "Soru Bankası")
        
        # TAB 2: Test Oluştur
        self.test_tab = QWidget()
        self.setup_test_tab()
        self.tabs.addTab(self.test_tab, "Test Oluştur")
        
        self.load_questions_to_list()

    def setup_bank_tab(self):
        layout = QVBoxLayout(self.bank_tab)
        
        # Header & Upload
        top_layout = QHBoxLayout()
        header = QLabel("Soru Bankası")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        top_layout.addWidget(header)
        
        self.btn_load_pdf = QPushButton("Yeni PDF Analiz Et")
        self.btn_load_pdf.clicked.connect(self.load_pdf)
        self.btn_load_pdf.setStyleSheet("background-color: #2ecc71; color: white; padding: 10px;")
        top_layout.addWidget(self.btn_load_pdf)
        layout.addLayout(top_layout)
        
        # List
        self.questions_list = QListWidget()
        layout.addWidget(self.questions_list)
        
        # Actions
        actions_layout = QHBoxLayout()
        self.btn_delete = QPushButton("Seçili Soruyu Sil")
        self.btn_delete.clicked.connect(self.delete_selected_question)
        actions_layout.addWidget(self.btn_delete)
        
        self.btn_delete_all = QPushButton("Tüm Soru Bankasını Temizle")
        self.btn_delete_all.clicked.connect(self.delete_all_questions)
        self.btn_delete_all.setStyleSheet("background-color: #e74c3c; color: white;")
        actions_layout.addWidget(self.btn_delete_all)
        
        layout.addLayout(actions_layout)

    def setup_test_tab(self):
        layout = QVBoxLayout(self.test_tab)
        
        layout.addWidget(QLabel("Test İçin Soru Seçin:"))
        self.selection_list = QListWidget()
        self.selection_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        layout.addWidget(self.selection_list)
        
        self.btn_generate = QPushButton("Seçili Sorulardan Test Oluştur (PDF)")
        self.btn_generate.clicked.connect(self.generate_test)
        self.btn_generate.setStyleSheet("background-color: #3498db; color: white; padding: 15px; font-size: 16px;")
        layout.addWidget(self.btn_generate)
        
        self.btn_clear_selection = QPushButton("Seçimi Temizle")
        self.btn_clear_selection.clicked.connect(lambda: self.selection_list.clearSelection())
        layout.addWidget(self.btn_clear_selection)

    def load_questions_to_list(self):
        self.questions_list.clear()
        self.selection_list.clear()
        
        questions = self.db_manager.get_all_questions()
        for q in questions:
            # q: (id, text, image_path, ...)
            item_text = f"#{q[0]} - {q[1][:120]}..."
            
            # Banka listesi
            self.questions_list.addItem(item_text)
            
            # Seçim listesi
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, q) # Tüm datayı sakla
            self.selection_list.addItem(item)

    def delete_selected_question(self):
        current_row = self.questions_list.currentRow()
        if current_row >= 0:
            questions = self.db_manager.get_all_questions()
            q_id = questions[current_row][0]
            
            reply = QMessageBox.question(self, 'Onay', "Soru silinsin mi?", 
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.db_manager.delete_question(q_id)
                self.load_questions_to_list()

    def delete_all_questions(self):
        reply = QMessageBox.question(self, 'KRİTİK ONAY', 
                                   "Soru bankasındaki TÜM sorular silinecek. Bu işlem geri alınamaz!\nEmin misiniz?", 
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.db_manager.delete_all_questions()
            self.load_questions_to_list()
            QMessageBox.information(self, "Bilgi", "Soru bankası tamamen temizlendi.")

    def generate_test(self):
        selected_items = self.selection_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir soru seçin!")
            return
            
        questions_to_export = [item.data(Qt.ItemDataRole.UserRole) for item in selected_items]
        
        save_path, _ = QFileDialog.getSaveFileName(self, "Testi Kaydet", "yeni_test.pdf", "PDF Dosyaları (*.pdf)")
        
        if save_path:
            try:
                # Full path gönderiyoruz
                self.test_generator.generate_pdf("Öğretmen Testi", questions_to_export, save_path)
                QMessageBox.information(self, "Başarılı", f"Test başarıyla oluşturuldu:\n{save_path}")
            except Exception as e:
                import traceback
                traceback.print_exc()
                QMessageBox.critical(self, "Hata", f"PDF oluşturulamadı: {str(e)}")

    def load_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "PDF Seç", "", "PDF Dosyaları (*.pdf)")
        if file_path:
            reply = QMessageBox.question(self, 'Onay', 
                                       f"'{os.path.basename(file_path)}' dosyası analiz edilsin mi?\nBu işlem biraz zaman alabilir.",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                self.process_pdf(file_path)

    def process_pdf(self, pdf_path):
        from PyQt6.QtWidgets import QProgressDialog
        
        try:
            # Önce tüm sayfaları görsele çevir
            images = self.pdf_processor.convert_pdf_to_images(pdf_path)
            if not images:
                return

            chunk_size = 5
            chunks = [images[i:i + chunk_size] for i in range(0, len(images), chunk_size)]
            total_chunks = len(chunks)
            
            progress = QProgressDialog("PDF İşleniyor...", "İptal", 0, total_chunks, self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setWindowTitle("Analiz Durumu")
            progress.setMinimumDuration(0)
            
            # Yeni bir Gemini oturumu başlat
            self.gemini_service.start_new_session()
            
            for i, chunk in enumerate(chunks):
                if progress.wasCanceled():
                    break
                    
                progress.setLabelText(f"{i+1}/{total_chunks}. parça işleniyor...\n(Sayfa {i*chunk_size + 1} - {min((i+1)*chunk_size, len(images))})")
                
                # Tekrar deneme mantığı
                max_retries = 2
                questions_data = []
                for attempt in range(max_retries + 1):
                    questions_data = self.gemini_service.analyze_chunk(chunk)
                    if questions_data or attempt == max_retries:
                        break
                    print(f"Parça {i+1} başarısız oldu, yeniden deneniyor... (Deneme {attempt + 1})")
                
                # Soruları işle
                for idx, q_data in enumerate(questions_data):
                    # page_index varsa ona göre img_path seç, yoksa chunk'ın ilk görselini varsay
                    p_idx = q_data.get('page_index', 0)
                    # p_idx, chunk içindeki index mi? Yoksa genel mi? 
                    # Prompt'ta 'page_index' demedik ama mantıken chunk içindeki index olmalı.
                    # Ancak Gemini bazen genel index verebilir. Kontrol edelim.
                    
                    # Güvenli index seçimi
                    img_to_crop = chunk[p_idx] if p_idx < len(chunk) else chunk[0]
                    
                    q_id = f"q_{time.time_ns()}_{idx}"
                    os.makedirs(os.path.join('assets', 'questions'), exist_ok=True)
                    out_path = os.path.join('assets', 'questions', f"{q_id}.png")
                    
                    if 'coordinates' in q_data:
                        self.pdf_processor.crop_question(img_to_crop, q_data['coordinates'], out_path, padding=25)
                        self.db_manager.add_question(q_data.get('text', 'Metin bulunamadı'), out_path)
                
                progress.setValue(i + 1)

            progress.close()
            QMessageBox.information(self, "Başarılı", "Sorular başarıyla ayıklandı.")
            self.load_questions_to_list()
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Hata", f"İşlem hatası: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
