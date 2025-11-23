import argparse
import time
from pathlib import Path
from src.pipeline.audio_stream import AudioStream
from src.pipeline.transcriber import Transcriber
from src.pipeline.buffer_manager import BufferManager
from src.cognitive.controller import Controller

def main():
    parser = argparse.ArgumentParser(description="Sales AI Pipeline")
    parser.add_argument("--test-file", type=str, help="Path to test audio file (simulates mic)")
    args = parser.parse_args()

    print("🚀 Initializing Sales AI Pipeline...")
    
    # Initialize components
    buffer_manager = BufferManager()
    transcriber = Transcriber()
    audio_stream = AudioStream()
    controller = Controller()
    
    print("\n✅ System Ready. Waiting for audio...")
    print("-" * 50)

    try:
        # Choose stream source
        if args.test_file:
            stream_gen = audio_stream.stream_from_file(args.test_file)
        else:
            stream_gen = audio_stream.stream()

        # Main Loop
        for audio_segment in stream_gen:
            # Start Latency Timer
            start_time = time.time()
            
            # 1. Transcribe
            text = transcriber.transcribe(audio_segment)
            
            if text:
                # 2. Update Buffer
                buffer_manager.add_segment(text)
                
                # 3. Cognitive Control (The Brain)
                # We pass the *current* text segment for immediate reaction
                # In V3, we might pass the full buffer context
                decision = controller.process(text, start_time)
                
                if decision:
                    print(f"\n🤖 AI RESPONSE ({decision['latency']:.2f}s):")
                    print(f"   [{decision['intent']}] {decision['response']}")
                else:
                    print("\n😶 AI Silent (Null Mode)")
                
                print("-" * 50)
                
    except KeyboardInterrupt:
        print("\n🛑 Stopping pipeline...")
    finally:
        audio_stream.stop()
        print("👋 Pipeline shutdown complete.")

if __name__ == "__main__":
    main()
