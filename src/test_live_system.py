"""
Quick diagnostic test to verify the Sales AI system is working.
This simulates speaking a question and checks if the system responds.
"""

from src.cognitive.controller import Controller
import time

def test_system():
    print("🧪 Testing Sales AI System...\n")
    
    # Initialize controller
    print("1️⃣ Loading Controller...")
    controller = Controller()
    print("✅ Controller loaded\n")
    
    # Test questions
    test_cases = [
        ("How much does it cost?", True, "Pricing"),
        ("Is your platform secure?", True, "Technical"),
        ("Can you send me a proposal?", True, "NextSteps"),
        ("Hello there", False, "Small talk"),
        ("What is the weather?", False, "Irrelevant"),
    ]
    
    print("2️⃣ Testing Questions:\n")
    
    for text, should_respond, category in test_cases:
        print(f"   Question: '{text}'")
        start_time = time.time()
        
        decision = controller.process(text, start_time)
        
        if decision and decision.get('action') == 'SPEAK':
            print(f"   ✅ RESPONDED: {category}")
            print(f"      Intent: {decision.get('intent_category')} (score: {decision.get('intent_score'):.3f})")
            print(f"      Response: {decision.get('response_text')[:60]}...")
        elif should_respond:
            print(f"   ❌ SHOULD HAVE RESPONDED but stayed silent")
        else:
            print(f"   ✅ CORRECTLY STAYED SILENT")
        
        print()
    
    print("\n🎯 Test Complete!")
    print("\nIf all tests passed, the cognitive layer is working correctly.")
    print("If the overlay isn't showing, it might be a UI/display issue.")

if __name__ == "__main__":
    test_system()
