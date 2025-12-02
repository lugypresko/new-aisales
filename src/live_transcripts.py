"""
Real-Time Transcript Monitor
Shows transcriptions as they happen with color-coded output and live statistics.
"""

import json
import time
from pathlib import Path
from datetime import datetime
import os

class LiveTranscriptMonitor:
    def __init__(self):
        self.log_file = Path("logs/interactions.jsonl")
        self.last_position = 0
        self.total_count = 0
        self.spoken_count = 0
        self.silent_count = 0
        
    def clear_screen(self):
        """Clear the console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Print the monitor header."""
        print("\n" + "="*80)
        print("🎤 LIVE TRANSCRIPT MONITOR - Sales AI")
        print("="*80)
        print("Watching for new transcriptions... (Press Ctrl+C to stop)\n")
        print(f"📊 Stats: Total: {self.total_count} | ✅ Spoken: {self.spoken_count} | 🔇 Silent: {self.silent_count}")
        print("-"*80 + "\n")
    
    def format_entry(self, entry):
        """Format a log entry for display."""
        text = entry.get('input_text', '')
        outcome = entry.get('outcome', 'UNKNOWN')
        intent = entry.get('intent')
        iso_time = entry.get('iso_time', '')
        latency = entry.get('latency_seconds', 0)
        
        # Extract time
        time_str = iso_time.split('T')[1][:8] if 'T' in iso_time else datetime.now().strftime('%H:%M:%S')
        
        # Status emoji
        if outcome == 'SPOKEN':
            status = "✅ SPOKEN"
            self.spoken_count += 1
        else:
            status = "🔇 SILENT"
            self.silent_count += 1
        
        self.total_count += 1
        
        # Build output
        output = f"[{time_str}] {status}\n"
        output += f"   🎤 Heard: \"{text}\"\n"
        
        if intent:
            output += f"   🧠 Intent: {intent}\n"
        
        output += f"   ⚡ Latency: {latency*1000:.1f}ms\n"
        
        if outcome == 'SPOKEN':
            response = entry.get('response_text', '')
            if response:
                # Truncate long responses
                response_preview = response[:100] + "..." if len(response) > 100 else response
                output += f"   💬 Response: {response_preview}\n"
        
        return output
    
    def monitor(self):
        """Main monitoring loop."""
        # Initialize position
        if self.log_file.exists():
            with open(self.log_file, 'r', encoding='utf-8') as f:
                f.seek(0, 2)  # Go to end
                self.last_position = f.tell()
        
        self.clear_screen()
        self.print_header()
        
        print("⏳ Waiting for transcriptions...\n")
        
        try:
            while True:
                if not self.log_file.exists():
                    time.sleep(0.5)
                    continue
                
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    f.seek(self.last_position)
                    new_lines = f.readlines()
                    self.last_position = f.tell()
                
                if new_lines:
                    for line in new_lines:
                        if line.strip():
                            try:
                                entry = json.loads(line.strip())
                                
                                # Print the new entry
                                print(self.format_entry(entry))
                                print("-"*80 + "\n")
                                
                            except json.JSONDecodeError:
                                continue
                
                time.sleep(0.3)  # Check every 300ms
        
        except KeyboardInterrupt:
            print("\n" + "="*80)
            print("👋 Stopped monitoring.")
            print("="*80)
            print(f"\n📊 Final Stats:")
            print(f"   Total transcriptions: {self.total_count}")
            print(f"   ✅ Spoken (AI responded): {self.spoken_count}")
            print(f"   🔇 Silent (AI stayed quiet): {self.silent_count}")
            print()

if __name__ == "__main__":
    monitor = LiveTranscriptMonitor()
    monitor.monitor()
