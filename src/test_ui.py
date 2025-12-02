"""
Simple UI test to verify PySide6 overlay can display.
"""
import sys
from PySide6.QtWidgets import QApplication
from src.ui.overlay import SalesOverlay

def main():
    print("🎨 Testing UI Overlay...")
    app = QApplication(sys.argv)
    
    overlay = SalesOverlay()
    overlay.show()
    
    # Simulate a hint after 2 seconds
    from PySide6.QtCore import QTimer
    def show_test_hint():
        overlay.update_hint("PRICING", "Our Standard plan is $50/month. Pro is $150/month.")
        print("✅ Test hint displayed!")
    
    QTimer.singleShot(2000, show_test_hint)
    
    print("✅ UI Window should appear in top-right corner.")
    print("   Close the window with the 'x' button to exit.")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
