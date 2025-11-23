"""
Performance Validation Script.
Runs a batch of test cases to measure Latency, False Trigger Rate (FTR), and Accuracy.
"""

import time
import json
import numpy as np
from pathlib import Path
from src.cognitive.controller import Controller

def validate_performance():
    print("🚀 Starting Performance Validation...")
    
    # Initialize Controller
    controller = Controller()
    
    # Test Dataset (Synthetic)
    test_cases = [
        # Positive Cases (Should Speak)
        {"text": "How much does it cost?", "expect_speak": True, "intent": "Pricing"},
        {"text": "Is it secure?", "expect_speak": True, "intent": "Technical"},
        {"text": "Send me a proposal", "expect_speak": True, "intent": "NextSteps"},
        {"text": "Who are your competitors?", "expect_speak": True, "intent": "Competitors"},
        
        # Negative Cases (Should be Silent)
        {"text": "Hello", "expect_speak": False},
        {"text": "Can you hear me?", "expect_speak": False},
        {"text": "Just checking in", "expect_speak": False},
        {"text": "Um, ah, okay", "expect_speak": False},
        {"text": "What is the weather?", "expect_speak": False},
        {"text": "I like pizza", "expect_speak": False},
    ]
    
    # Metrics
    latencies = []
    false_triggers = 0
    missed_triggers = 0
    correct_intents = 0
    total_positive = sum(1 for c in test_cases if c['expect_speak'])
    total_negative = sum(1 for c in test_cases if not c['expect_speak'])
    
    print(f"\n🧪 Running {len(test_cases)} Test Cases...")
    print("-" * 60)
    
    with open("performance_report.txt", "w", encoding="utf-8") as f:
        f.write("PERFORMANCE VALIDATION REPORT\n")
        f.write("=" * 60 + "\n")
        
        for i, case in enumerate(test_cases, 1):
            text = case['text']
            start_time = time.time()
            
            # Run Controller
            decision = controller.process(text, start_time)
            
            latency = time.time() - start_time
            latencies.append(latency)
            
            # Analyze Result
            outcome = "SPOKEN" if decision else "SILENT"
            expected = "SPOKEN" if case['expect_speak'] else "SILENT"
            
            status = "✅"
            if outcome != expected:
                status = "❌"
                if outcome == "SPOKEN":
                    false_triggers += 1
                else:
                    missed_triggers += 1
            elif case.get('intent'):
                if decision['intent'] != case['intent']:
                    status = "⚠️ (Wrong Intent)"
                else:
                    correct_intents += 1
                    
            msg = f"{status} Case #{i}: '{text}' -> {outcome} ({latency*1000:.1f}ms)"
            print(msg)
            f.write(msg + "\n")
            
        # Calculate Stats
        avg_latency = np.mean(latencies) * 1000
        p95_latency = np.percentile(latencies, 95) * 1000
        ftr = (false_triggers / total_negative) * 100 if total_negative > 0 else 0.0
        recall = ((total_positive - missed_triggers) / total_positive) * 100 if total_positive > 0 else 0.0
        
        f.write("-" * 60 + "\n")
        f.write("📊 PERFORMANCE REPORT\n")
        f.write(f"   Avg Latency: {avg_latency:.1f} ms\n")
        f.write(f"   P95 Latency: {p95_latency:.1f} ms\n")
        f.write(f"   False Trigger Rate: {ftr:.1f}% (Target < 15%)\n")
        f.write(f"   Recall: {recall:.1f}% (Target > 75%)\n")
        f.write(f"   Intent Accuracy: {correct_intents}/{total_positive}\n")
        
        print("-" * 60)
        print(f"   Recall: {recall:.1f}%")
        
        # Validation Logic
        success = True
        if avg_latency > 2200:
            print("❌ FAILED: Latency too high (>2200ms)")
            f.write("❌ FAILED: Latency too high\n")
            success = False
        if ftr > 15.0:
            print("❌ FAILED: False Trigger Rate too high (>15%)")
            f.write("❌ FAILED: FTR too high\n")
            success = False
        if recall < 75.0:
            print("❌ FAILED: Recall too low (<75%)")
            f.write("❌ FAILED: Recall too low\n")
            success = False
            
        if success:
            print("\n✅ SYSTEM VALIDATED")
            f.write("\n✅ SYSTEM VALIDATED\n")
        else:
            print("\n❌ VALIDATION FAILED")
            f.write("\n❌ VALIDATION FAILED\n")

if __name__ == "__main__":
    validate_performance()
