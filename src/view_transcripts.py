"""
Transcript Viewer - Shows all words the Sales AI app understood.
Reads from logs/interactions.jsonl and displays transcribed text.
"""

import json
from pathlib import Path
from datetime import datetime

def view_transcripts():
    log_file = Path("logs/interactions.jsonl")
    
    if not log_file.exists():
        print("❌ No log file found. The app hasn't processed any audio yet.")
        print("   Start the app with: python run_sales_ai.py")
        return
    
    print("\n" + "="*80)
    print("📝 SALES AI TRANSCRIPT LOG")
    print("="*80 + "\n")
    
    transcripts = []
    
    # Read all log entries
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if entry.get('text'):  # Only entries with transcribed text
                    transcripts.append(entry)
            except:
                continue
    
    if not transcripts:
        print("📭 No transcripts found yet. The app is running but hasn't heard anything.")
        print("   Try speaking into your microphone!")
        return
    
    print(f"Found {len(transcripts)} transcribed segments:\n")
    
    for i, entry in enumerate(transcripts, 1):
        timestamp = entry.get('timestamp', 0)
        dt = datetime.fromtimestamp(timestamp)
        text = entry.get('text', '')
        intent = entry.get('intent_category', 'None')
        action = entry.get('action', 'SILENT')
        
        print(f"[{i}] {dt.strftime('%H:%M:%S')}")
        print(f"    🎤 HEARD: \"{text}\"")
        print(f"    🧠 Intent: {intent}")
        print(f"    💡 Action: {action}")
        
        if action == 'SPEAK':
            response = entry.get('response_text', '')
            if response:
                print(f"    💬 Suggested: {response[:80]}...")
        
        print()
    
    print("="*80)
    print(f"\n✅ Total transcripts: {len(transcripts)}")
    print(f"📁 Log file: {log_file.absolute()}\n")

if __name__ == "__main__":
    view_transcripts()
