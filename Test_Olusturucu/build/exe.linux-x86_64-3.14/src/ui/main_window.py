# src/ui/main_window.py
import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFrame, QStackedWidget, 
                             QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QIcon
from src.ui.styles import GlassStyles
from src.ui.tabs.bank_tab import BankTab
from src.ui.tabs.test_tab import TestTab

class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("TitleBar")
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 0, 10, 0)
        
        self.title = QLabel("Test Oluşturucu Pro")
        self.title.setObjectName("TitleLabel")
        self.layout.addWidget(self.title)
        
        self.layout.addStretch()
        
        # Window Controls
        self.btn_min = QPushButton("–")
        self.btn_min.setFixedSize(30, 30)
        self.btn_min.setStyleSheet("background: transparent; font-size: 18px;")
        self.btn_min.clicked.connect(self.parent.showMinimized)
        self.layout.addWidget(self.btn_min)
        
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.setStyleSheet("background: transparent; font-size: 14px;")
        self.btn_close.clicked.connect(self.parent.close)
        self.layout.addWidget(self.btn_close)
        
        self.start_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.start_pos:
            delta = event.globalPosition().toPoint() - self.start_pos
            self.parent.move(self.parent.x() + delta.x(), self.parent.y() + delta.y())
            self.start_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.start_pos = None

class ModernMainWindow(QMainWindow):
    def __init__(self, original_logic_callback=None):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setWindowTitle("Test Oluşturucu")
        self.resize(1000, 700)
        
        self.setup_ui()
        self.setStyleSheet(GlassStyles.MAIN_STYLE)

    def setup_ui(self):
        # Container Widget with Rounded Corners and Glass Effect
        self.central_widget = QWidget()
        self.central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 1. Custom Title Bar
        self.title_bar = TitleBar(self)
        self.main_layout.addWidget(self.title_bar)
        
        # 2. Main Body (Sidebar + Content)
        self.body_container = QWidget()
        self.body_layout = QHBoxLayout(self.body_container)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(20, 30, 20, 30)
        self.sidebar_layout.setSpacing(15)
        
        # Sidebar Menu Items
        self.btn_bank = QPushButton(" Soru Bankası")
        self.btn_bank.setObjectName("SecondaryButton")
        self.btn_bank.setCheckable(True)
        self.btn_bank.setChecked(True)
        self.sidebar_layout.addWidget(self.btn_bank)
        
        self.btn_test = QPushButton(" Test Oluştur")
        self.btn_test.setObjectName("SecondaryButton")
        self.btn_test.setCheckable(True)
        self.sidebar_layout.addWidget(self.btn_test)
        
        self.sidebar_layout.addStretch()
        
        # Version Tag
        self.version_label = QLabel("v1.2.0")
        self.version_label.setStyleSheet("color: rgba(255,255,255,0.4); font-size: 10px;")
        self.sidebar_layout.addWidget(self.version_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.body_layout.addWidget(self.sidebar)
        
        # Content Stack
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("ContentArea")
        
        self.bank_tab = BankTab()
        self.test_tab = TestTab()
        
        self.content_stack.addWidget(self.bank_tab)
        self.content_stack.addWidget(self.test_tab)
        
        self.body_layout.addWidget(self.content_stack)
        
        self.main_layout.addWidget(self.body_container)
        
        # Connect Sidebar Buttons
        self.btn_bank.clicked.connect(lambda: self.switch_tab(0))
        self.btn_test.clicked.connect(lambda: self.switch_tab(1))
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.central_widget.setGraphicsEffect(shadow)

    def switch_tab(self, index):
        self.content_stack.setCurrentIndex(index)
        self.btn_bank.setChecked(index == 0)
        self.btn_test.setChecked(index == 1)

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = ModernMainWindow()
    window.show()
    sys.exit(app.exec())
