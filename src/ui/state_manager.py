"""
UI State Manager.
Handles debounce logic and updates the Overlay.
"""

from PySide6.QtCore import QObject, Signal, QTimer
from typing import Dict, Optional

class StateManager(QObject):
    # Signal to update UI: (intent, hint_text)
    update_ui_signal = Signal(str, str)
    
    def __init__(self, overlay):
        super().__init__()
        self.overlay = overlay
        self.update_ui_signal.connect(self.overlay.update_hint)
        
        # Debounce Timer
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self._apply_update)
        
        self.pending_update = None
        self.debounce_ms = 200  # Configurable

    def process_decision(self, decision: Optional[Dict]):
        """
        Called by the main loop when a decision is made.
        """
        if not decision:
            return
            
        # If we have a new decision, schedule update
        self.pending_update = decision
        self.debounce_timer.start(self.debounce_ms)

    def _apply_update(self):
        """Apply the pending update to the UI."""
        if self.pending_update:
            intent = self.pending_update.get('intent', 'Unknown')
            response = self.pending_update.get('response', '...')
            self.update_ui_signal.emit(intent, response)
            self.pending_update = None
