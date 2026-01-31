# src/ui/tabs/test_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt

class TestTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)
        
        # Header Section
        header_layout = QHBoxLayout()
        self.title = QLabel("Test Oluştur")
        self.title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(self.title)
        header_layout.addStretch()
        self.layout.addLayout(header_layout)
        
        self.instruction = QLabel("Lütfen test dosyasında yer almasını istediğiniz soruları seçin:")
        self.instruction.setStyleSheet("color: rgba(255,255,255,0.7);")
        self.layout.addWidget(self.instruction)
        
        # Selection List
        self.selection_list = QListWidget()
        self.selection_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.layout.addWidget(self.selection_list)
        
        # Action Buttons
        actions_layout = QHBoxLayout()
        
        self.btn_clear = QPushButton(" Seçimi Temizle")
        self.btn_clear.setObjectName("SecondaryButton")
        self.btn_clear.setMinimumHeight(50)
        actions_layout.addWidget(self.btn_clear)
        
        self.btn_generate = QPushButton(" Test Dosyasını Oluştur (PDF)")
        self.btn_generate.setMinimumHeight(50)
        self.btn_generate.setStyleSheet("padding: 0 30px; font-size: 16px;")
        actions_layout.addWidget(self.btn_generate)
        
        self.layout.addLayout(actions_layout)
