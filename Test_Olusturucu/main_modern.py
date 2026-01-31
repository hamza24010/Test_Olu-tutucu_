# main_modern.py
import sys
import os
import json
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt

from src.core.pdf_processor import PDFProcessor
from src.core.gemini_service import GeminiService
from src.db.db_manager import DBManager
from src.core.test_generator import TestGenerator
from src.ui.main_window import ModernMainWindow

class AppController:
    def __init__(self):
        self.window = ModernMainWindow()
        
        # Services
        self.pdf_processor = PDFProcessor()
        self.gemini_service = GeminiService()
        self.db_manager = DBManager()
        self.test_generator = TestGenerator()
        
        # Connect Logic to Bridge
        self.window.bridge.set_logic(self)

    # --- Bridge Interface Methods ---

    def get_questions_json(self):
        """Returns all questions as JSON string"""
        try:
            questions = self.db_manager.get_all_questions()
            # Convert list of tuples to list of dicts for JSON
            # Schema assumption: ID, TEXT, IMAGE_PATH, SUBJECT, DIFFICULTY, GRADE_LEVEL
            q_list = []
            for q in questions:
                # Need to match DB schema safely
                q_dict = {
                    "id": q[0],
                    "text": q[1],
                    "image": q[2],
                    # Add error handling or schema check if needed
                }
                # Check for other fields (Subject, Grade, Difficulty)
                if len(q) > 3: q_dict["subject"] = q[3]
                if len(q) > 4: q_dict["difficulty"] = q[4]
                if len(q) > 5: q_dict["grade_level"] = q[5]
                
                q_list.append(q_dict)
                
            return json.dumps(q_list)
        except Exception as e:
            print(f"Error fetching questions: {e}")
            return "[]"

    def delete_question(self, q_id):
        try:
            self.db_manager.delete_question(q_id)
            return True
        except Exception as e:
            print(f"Error deleting question {q_id}: {e}")
            return False

    def generate_test(self, config_json):
        try:
            config = json.loads(config_json)
            # Logic to select questions and generate PDF
            # This is a placeholder for the actual implementation
            # which would parse 'config' (selected ids, title, etc.)
            
            # questions_to_export = ...
            # save_path = ...
            # self.test_generator.generate_pdf(...)
            return "Test generation started (Not fully implemented in bridge yet)"
        except Exception as e:
            return f"Error: {str(e)}"

    # --- Native Methods (called from legacy parts or internal) ---
    
    def load_pdf(self):
        # Can still be triggered if we add a native button for it or call from JS
        file_path, _ = QFileDialog.getOpenFileName(self.window, "PDF Seç", "", "PDF Dosyaları (*.pdf)")
        if file_path:
            self.process_pdf(file_path)

    def process_pdf(self, pdf_path):
        try:
            images = self.pdf_processor.convert_pdf_to_images(pdf_path)
            # ... (rest of logic same as before) ...
            # ...
            QMessageBox.information(self.window, "Başarılı", "İşlem Tamamlandı")
        except Exception as e:
            QMessageBox.critical(self.window, "Hata", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = AppController()
    controller.window.show()
    sys.exit(app.exec())
