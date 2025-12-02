"""
Real-time Transcript Monitor
Watches the log file and displays new transcripts as they appear.
Run this while the Sales AI app is running to see live transcriptions.
"""

import json
import time
from pathlib import Path
from datetime import datetime

def monitor_transcripts():
    log_file = Path("logs/interactions.jsonl")
    
    print("\n" + "="*80)
    print("👀 REAL-TIME TRANSCRIPT MONITOR")
    print("="*80)
    print("\nWatching for new transcriptions... (Press Ctrl+C to stop)\n")
    
    # Track last position in file
    last_position = 0
    
    if log_file.exists():
        # Start from current end of file
        with open(log_file, 'r', encoding='utf-8') as f:
            f.seek(0, 2)  # Go to end
            last_position = f.tell()
    
    try:
        while True:
            if not log_file.exists():
                time.sleep(0.5)
                continue
            
            with open(log_file, 'r', encoding='utf-8') as f:
                f.seek(last_position)
                new_lines = f.readlines()
                last_position = f.tell()
            
            for line in new_lines:
                try:
                    entry = json.loads(line.strip())
                    
                    if entry.get('text'):
                        timestamp = entry.get('timestamp', 0)
                        dt = datetime.fromtimestamp(timestamp)
                        text = entry.get('text', '')
                        intent = entry.get('intent_category', 'None')
                        action = entry.get('action', 'SILENT')
                        
                        print(f"\n{'='*80}")
                        print(f"⏰ {dt.strftime('%H:%M:%S')}")
                        print(f"🎤 HEARD: \"{text}\"")
                        print(f"🧠 Intent: {intent} | Action: {action}")
                        
                        if action == 'SPEAK':
                            response = entry.get('response_text', '')
                            if response:
                                print(f"💬 Suggestion: {response[:100]}...")
                        
                        print("="*80)
                
                except:
                    continue
            
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("\n\n👋 Stopped monitoring.\n")

if __name__ == "__main__":
    monitor_transcripts()
