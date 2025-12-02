"""
Quick diagnostic to test the cognitive pipeline without UI.
"""
import time
from src.cognitive.controller import Controller

def main():
    print("🧪 Testing Sales AI Cognitive Layer...")
    print("=" * 60)
    
    controller = Controller()
    
    test_cases = [
        "How much does it cost?",
        "Is your platform secure?",
        "Can you send me a proposal?",
        "Hello there",
        "What is the weather today?"
    ]
    
    for query in test_cases:
        print(f"\n📝 Query: '{query}'")
        start = time.time()
        decision = controller.process(query, start)
        
        if decision:
            print(f"✅ RESPONSE: {decision['response'][:60]}...")
            print(f"   Intent: {decision['intent']}, Latency: {decision['latency']*1000:.1f}ms")
        else:
            print(f"🤫 SILENT (No response)")
    
    print("\n" + "=" * 60)
    print("✅ Diagnostic Complete. Check logs/interactions.jsonl for details.")

if __name__ == "__main__":
    main()
