# src/ui/styles.py

class GlassStyles:
    # Color Palette (Glassmorphism Professional)
    PRIMARY = "#2563EB"
    SECONDARY = "#3B82F6"
    ACCENT = "#F97316"
    TEXT_PRIMARY = "#FFFFFF"
    TEXT_SECONDARY = "#E2E8F0"
    
    # Glass Backgrounds
    GLASS_BASE = "rgba(255, 255, 255, 15)" # Very transparent for wallpaper bleed
    GLASS_MODAL = "rgba(255, 255, 255, 30)"
    BORDER_LIGHT = "rgba(255, 255, 255, 40)"
    
    MAIN_STYLE = f"""
    QMainWindow {{
        background: transparent;
    }}
    
    #CentralWidget {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                                    stop:0 rgba(15, 23, 42, 220), 
                                    stop:1 rgba(30, 41, 59, 200));
        border-radius: 20px;
        border: 1px solid {BORDER_LIGHT};
    }}
    
    #Sidebar {{
        background: rgba(255, 255, 255, 10);
        border-right: 1px solid {BORDER_LIGHT};
        border-top-left-radius: 20px;
        border-bottom-left-radius: 20px;
        min-width: 220px;
    }}
    
    #ContentArea {{
        background: transparent;
        padding: 20px;
    }}
    
    QPushButton {{
        background: {PRIMARY};
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: bold;
        font-size: 14px;
        border: none;
    }}
    
    QPushButton:hover {{
        background: {SECONDARY};
        transform: translateY(-1px);
    }}
    
    QPushButton#SecondaryButton {{
        background: rgba(255, 255, 255, 20);
        border: 1px solid {BORDER_LIGHT};
    }}
    
    QPushButton#SecondaryButton:hover {{
        background: rgba(255, 255, 255, 40);
    }}
    
    QLabel {{
        color: {TEXT_PRIMARY};
        font-family: 'Poppins', 'Segoe UI', sans-serif;
    }}
    
    QListWidget {{
        background: rgba(0, 0, 0, 100);
        border: 1px solid {BORDER_LIGHT};
        border-radius: 15px;
        color: white;
        padding: 10px;
    }}
    
    QListWidget::item {{
        background: rgba(255, 255, 255, 15);
        border-radius: 8px;
        margin-bottom: 5px;
        padding: 12px;
    }}
    
    QListWidget::item:selected {{
        background: {PRIMARY};
        color: white;
    }}
    
    #TitleBar {{
        background: rgba(255, 255, 255, 5);
        border-top-left-radius: 20px;
        border-top-right-radius: 20px;
        min-height: 40px;
    }}
    
    #TitleLabel {{
        font-weight: bold;
        font-size: 14px;
        margin-left: 15px;
    }}
    """
