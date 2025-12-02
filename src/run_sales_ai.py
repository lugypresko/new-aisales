"""
Sales AI Launcher.
The main entry point. Initializes UI, Audio, and Brain.
"""

import sys
import time
import threading

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QThread, Signal

from src.ui.overlay import SalesOverlay
from src.ui.state_manager import StateManager
from src.pipeline.audio_stream import AudioStream
from src.pipeline.transcriber import Transcriber
from src.pipeline.buffer_manager import BufferManager
from src.cognitive.controller import Controller

class PipelineThread(QThread):
    """Runs the Audio Pipeline in a separate thread to keep UI responsive."""
    decision_made = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.running = True
        
    def run(self):
        print("🚀 Pipeline Thread Started...")
        
        # Initialize Components
        audio_stream = AudioStream()
        transcriber = Transcriber()
        buffer_manager = BufferManager()
        controller = Controller()
        
        print("✅ Pipeline Components Ready.")
        
        try:
            # Stream Audio
            stream_gen = audio_stream.stream()
            
            for audio_segment in stream_gen:
                if not self.running:
                    break
                    
                start_time = time.time()
                
                # 1. Transcribe
                text = transcriber.transcribe(audio_segment)
                
                if text:
                    # Show what was heard
                    print(f"\n{'='*60}")
                    print(f"🎤 HEARD: {text}")
                    print(f"{'='*60}\n")
                    
                    # 2. Update Buffer
                    buffer_manager.add_segment(text)
                    
                    # 3. Cognitive Control
                    decision = controller.process(text, start_time)
                    
                    if decision:
                        print(f"💡 ACTION: {decision.get('action')}")
                        if decision.get('action') == 'SPEAK':
                            print(f"📊 Intent: {decision.get('intent_category')} (score: {decision.get('intent_score'):.3f})")
                            print(f"💬 Suggestion: {decision.get('response_text')[:100]}...")
                        print()
                        # Emit signal to UI
                        self.decision_made.emit(decision)
                    else:
                        print(f"🤐 Staying silent (not business-relevant)\n")
                        
        except Exception as e:
            print(f"❌ Pipeline Error: {e}")
        finally:
            audio_stream.stop()
            print("👋 Pipeline Thread Stopped.")

    def stop(self):
        self.running = False

def main():
    app = QApplication(sys.argv)
    
    # 1. Create UI
    overlay = SalesOverlay()
    state_manager = StateManager(overlay)
    
    # 2. Create Pipeline Thread
    pipeline_thread = PipelineThread()
    
    # 3. Connect Pipeline -> UI
    pipeline_thread.decision_made.connect(state_manager.process_decision)
    
    # 4. Start
    overlay.show()
    pipeline_thread.start()
    
    print("✨ Sales AI Running. Press 'Ctrl+C' in terminal or click 'x' on overlay to exit.")
    
    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        print("\n🛑 Force Exit...")
        pipeline_thread.stop()
        pipeline_thread.wait()

if __name__ == "__main__":
    main()
