"""
Sales AI Overlay.
A frameless, always-on-top window to display real-time hints.
"""

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QApplication
from PySide6.QtCore import Qt, Slot, QTimer
from PySide6.QtGui import QFont, QColor, QPalette

class SalesOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        # Window Flags: Frameless, Always on Top, Tool (no taskbar icon)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                            Qt.WindowType.WindowStaysOnTopHint | 
                            Qt.WindowType.Tool)
        
        # Translucent Background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)
        
        # Container Widget (for styling)
        self.container = QWidget()
        self.container.setObjectName("container")
        self.container.setStyleSheet("""
            #container {
                background-color: rgba(20, 20, 30, 230);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 30);
            }
        """)
        container_layout = QVBoxLayout()
        self.container.setLayout(container_layout)
        layout.addWidget(self.container)
        
        # Intent Label
        self.intent_label = QLabel("Listening...")
        self.intent_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.intent_label.setStyleSheet("color: #AAAAAA; margin-bottom: 5px;")
        container_layout.addWidget(self.intent_label)
        
        # Hint Text
        self.hint_label = QLabel("Waiting for customer input...")
        self.hint_label.setFont(QFont("Segoe UI", 14))
        self.hint_label.setStyleSheet("color: #FFFFFF;")
        self.hint_label.setWordWrap(True)
        container_layout.addWidget(self.hint_label)
        
        # Close Button (Small 'x' at top right)
        # For MVP, we just click the window to close or use a hotkey, 
        # but let's add a small button for safety.
        self.close_btn = QPushButton("×", self.container)
        self.close_btn.setGeometry(280, 10, 20, 20)
        self.close_btn.setStyleSheet("""
            QPushButton {
                color: #888888;
                background: transparent;
                border: none;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover { color: #FF5555; }
        """)
        self.close_btn.clicked.connect(QApplication.instance().quit)
        
        # Geometry (Top Right)
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen.width() - 350, 50, 320, 200)
        
        # Fade Timer (for auto-hide logic if needed)
        self.opacity_effect = None # TODO: Add fade animation

    @Slot(str, str)
    def update_hint(self, intent: str, text: str):
        """Update the overlay with new content."""
        self.intent_label.setText(intent.upper())
        self.hint_label.setText(text)
        self.show()  # Ensure it's visible
        self.raise_()

    def mousePressEvent(self, event):
        # Allow dragging
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()
