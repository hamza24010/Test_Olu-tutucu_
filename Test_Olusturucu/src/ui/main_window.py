import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFrame, QStackedWidget, 
                             QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QPoint, QUrl, pyqtSlot
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel

from src.ui.styles import GlassStyles
from src.ui.bridge import Bridge

class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("TitleBar")
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 0, 10, 0)
        
        self.title = QLabel("Test Oluşturucu Pro (Hybrid)")
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
        self.resize(1200, 800) # Increased size for web view
        
        # Bridge Setup
        self.bridge = Bridge(self)
        
        self.setup_ui()
        self.setStyleSheet(GlassStyles.MAIN_STYLE)
        
        # Initialize with first tab
        self.switch_tab(0)

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
        
        # 2. Main Body (Web Content Only)
        self.body_container = QWidget()
        self.body_layout = QHBoxLayout(self.body_container)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(0)
        
        # --- SIDEBAR REMOVED (Using Web Sidebar instead) ---
        
        # Web View Setup
        self.webview = QWebEngineView()
        self.webview.setStyleSheet("background: white;")
        
        # Setup WebChannel
        self.channel = QWebChannel()
        self.channel.registerObject("bridge", self.bridge)
        self.webview.page().setWebChannel(self.channel)
        
        # Configure Settings for CDN Access & Local File Access
        settings = self.webview.settings()
        try:
            from PyQt6.QtWebEngineCore import QWebEngineSettings
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
            # settings.setAttribute(QWebEngineSettings.WebAttribute.DeveloperExtrasEnabled, True) # Disabled for stability
        except ImportError:
            pass
        
        self.body_layout.addWidget(self.webview)
        
        self.main_layout.addWidget(self.body_container)
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.central_widget.setGraphicsEffect(shadow)

    def get_page_path(self, page_name):
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'web', 'pages'))
        return QUrl.fromLocalFile(os.path.join(base_path, page_name))

    def switch_tab(self, index):
        # Navigation logic handled by Web UI calling bridge.navigate ideally
        # But for initial load/testing:
        if index == 0:
            self.webview.load(self.get_page_path("question_bank.html"))
        elif index == 1:
            self.webview.load(self.get_page_path("test_generator.html"))
        elif index == 2:
            self.webview.load(self.get_page_path("dashboard.html"))
        elif index == 3:
            self.webview.load(self.get_page_path("archive.html"))

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = ModernMainWindow()
    window.show()
    sys.exit(app.exec())
