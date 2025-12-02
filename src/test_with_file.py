"""
Test transcription with the pre-recorded audio file.
This will verify that the transcription and cognitive layers work correctly.
"""

from src.pipeline.audio_stream import AudioStream
from src.pipeline.transcriber import Transcriber
from src.cognitive.controller import Controller
import time

def test_with_audio_file():
    print("\n" + "="*80)
    print("TESTING WITH PRE-RECORDED AUDIO FILE")
    print("="*80 + "\n")
    
    print("Loading components...")
    audio_stream = AudioStream()
    transcriber = Transcriber()
    controller = Controller()
    print("Components loaded!\n")
    
    print("Processing audio file: data/test_audio.wav\n")
    print("-"*80 + "\n")
    
    # Stream from file
    stream_gen = audio_stream.stream_from_file('data/test_audio.wav')
    
    transcript_count = 0
    
    for audio_segment in stream_gen:
        start_time = time.time()
        
        # Transcribe
        text = transcriber.transcribe(audio_segment)
        
        if text:
            transcript_count += 1
            print(f"\n[Transcript #{transcript_count}]")
            print(f"HEARD: {text}")
            
            # Process with cognitive layer
            decision = controller.process(text, start_time)
            
            if decision and decision.get('action') == 'SPEAK':
                print(f"ACTION: SPEAK")
                print(f"Intent: {decision.get('intent_category')} (score: {decision.get('intent_score'):.3f})")
                print(f"Response: {decision.get('response_text')[:80]}...")
            else:
                print(f"ACTION: SILENT (not business-relevant)")
            
            print("-"*80)
    
    print(f"\n\nTotal transcripts: {transcript_count}")
    print("="*80 + "\n")

if __name__ == "__main__":
    test_with_audio_file()
