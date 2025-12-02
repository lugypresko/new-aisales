"""
Display transcribed words from the Sales AI app in a clean, organized format.
"""

import json
from pathlib import Path
from datetime import datetime
from collections import Counter

def show_transcripts():
    log_file = Path("logs/interactions.jsonl")
    
    if not log_file.exists():
        print("❌ No log file found. The app hasn't processed any audio yet.")
        return
    
    print("\n" + "="*80)
    print("📝 TRANSCRIBED WORDS - SALES AI")
    print("="*80 + "\n")
    
    transcripts = []
    spoken_count = 0
    silent_count = 0
    
    # Read all log entries
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    entry = json.loads(line.strip())
                    transcripts.append(entry)
                    if entry.get('outcome') == 'SPOKEN':
                        spoken_count += 1
                    else:
                        silent_count += 1
                except:
                    continue
    
    if not transcripts:
        print("📭 No transcripts found yet.\n")
        return
    
    # Group by date
    by_date = {}
    for entry in transcripts:
        iso_time = entry.get('iso_time', '')
        if iso_time:
            date = iso_time.split('T')[0]
            if date not in by_date:
                by_date[date] = []
            by_date[date].append(entry)
    
    # Display by date
    for date in sorted(by_date.keys(), reverse=True):
        entries = by_date[date]
        print(f"\n📅 {date}")
        print("-" * 80)
        
        for i, entry in enumerate(entries, 1):
            text = entry.get('input_text', '')
            outcome = entry.get('outcome', 'UNKNOWN')
            intent = entry.get('intent', 'None')
            iso_time = entry.get('iso_time', '')
            time_str = iso_time.split('T')[1][:8] if 'T' in iso_time else ''
            
            # Color coding
            if outcome == 'SPOKEN':
                status = "✅ SPOKEN"
            else:
                status = "🔇 SILENT"
            
            print(f"\n[{time_str}] {status}")
            print(f"   🎤 Heard: \"{text}\"")
            if intent and intent != 'None':
                print(f"   🧠 Intent: {intent}")
    
    # Summary statistics
    print("\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80)
    print(f"Total transcriptions: {len(transcripts)}")
    print(f"✅ Spoken (AI responded): {spoken_count}")
    print(f"🔇 Silent (AI stayed quiet): {silent_count}")
    
    # Most common phrases
    all_texts = [t.get('input_text', '') for t in transcripts]
    text_counts = Counter(all_texts)
    
    print("\n📈 Most Common Phrases:")
    for text, count in text_counts.most_common(10):
        print(f"   {count}x - \"{text}\"")
    
    # Intent breakdown
    intents = [t.get('intent') for t in transcripts if t.get('intent')]
    if intents:
        intent_counts = Counter(intents)
        print("\n🎯 Intent Breakdown:")
        for intent, count in intent_counts.most_common():
            print(f"   {count}x - {intent}")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    show_transcripts()
