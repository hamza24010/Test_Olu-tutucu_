from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal
import json
import sys

class Bridge(QObject):
    """
    Bridge class for communication between Python and JavaScript.
    Do not rename methods as they are called from JS.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logic = None

    def set_logic(self, logic_interface):
        self.logic = logic_interface

    @pyqtSlot(str)
    def log(self, message):
        """Log message from JS to Python console"""
        print(f"[JS-LOG]: {message}")

    @pyqtSlot(result=str)
    def getVersion(self):
        """Return application version"""
        return "1.2.0-hybrid"

    @pyqtSlot(str)
    def navigate(self, page_name):
        """Handle navigation requests from within JS if needed"""
        print(f"Navigating to {page_name}")
        # Logic to switch pages could be here or handled in main_window
    
    # --- Question Bank API ---
    
    @pyqtSlot(result=str)
    def getQuestions(self):
        """Fetch all questions"""
        if self.logic:
            return self.logic.get_questions_json()
        return "[]"

    @pyqtSlot(str, result=str)
    def deleteQuestion(self, q_id):
        """Delete a question by ID"""
        if self.logic:
            success = self.logic.delete_question(q_id)
            return "success" if success else "failed"
        return "no-logic"

    @pyqtSlot(str, result=str)
    def generateTest(self, config_json):
        """Generate test PDF"""
        if self.logic:
            return self.logic.generate_test(config_json)
        return "error: no logic"
