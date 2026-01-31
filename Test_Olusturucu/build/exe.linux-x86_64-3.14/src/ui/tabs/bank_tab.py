# src/ui/tabs/bank_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt

class BankTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)
        
        # Header Section
        header_layout = QHBoxLayout()
        self.title = QLabel("Soru Bankası")
        self.title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(self.title)
        
        header_layout.addStretch()
        
        self.btn_analyze = QPushButton("  Yeni PDF Analiz Et")
        self.btn_analyze.setMinimumHeight(45)
        # We can add an icon here later
        header_layout.addWidget(self.btn_analyze)
        
        self.layout.addLayout(header_layout)
        
        # Search Bar (Optional but nice)
        # self.search_bar = QLineEdit()
        # self.search_bar.setPlaceholderText("Soru ara...")
        # self.layout.addWidget(self.search_bar)
        
        # List Section
        self.questions_list = QListWidget()
        self.questions_list.setObjectName("QuestionsList")
        self.layout.addWidget(self.questions_list)
        
        # Footer Actions
        footer_layout = QHBoxLayout()
        self.btn_delete = QPushButton(" Seçili Soruyu Sil")
        self.btn_delete.setObjectName("SecondaryButton")
        self.btn_delete.setMinimumHeight(40)
        footer_layout.addWidget(self.btn_delete)
        
        footer_layout.addStretch()
        
        self.count_label = QLabel("Toplam Soru: 0")
        self.count_label.setStyleSheet("opacity: 0.7;")
        footer_layout.addWidget(self.count_label)
        
        self.layout.addLayout(footer_layout)
