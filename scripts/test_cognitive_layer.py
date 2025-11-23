"""
Test Cognitive Layer (Text-Only).
Verifies Gate 1 (Intent) and Gate 2 (RAG) logic without audio dependencies.
"""

import time
from src.cognitive.controller import Controller

def test_cognitive_layer():
    print("🧠 Initializing Controller...")
    controller = Controller()
    
    test_cases = [
        {
            "text": "How much does it cost?",
            "expected_intent": "Pricing",
            "expect_response": True
        },
        {
            "text": "Is your platform secure?",
            "expected_intent": "Technical",
            "expect_response": True
        },
        {
            "text": "Hello there",
            "expected_intent": None, # Should fail Gate 1
            "expect_response": False
        },
        {
            "text": "What is the capital of France?",
            "expected_intent": None, # Should fail Gate 1 or 2
            "expect_response": False
        },
        {
            "text": "Can you send me a proposal?",
            "expected_intent": "NextSteps",
            "expect_response": True
        }
    ]
    
    print("\n🧪 Starting Verification Tests...")
    print("=" * 60)
    
    with open("verification_results.txt", "w", encoding="utf-8") as f:
        f.write("COGNITIVE LAYER VERIFICATION RESULTS\n")
        f.write("=" * 60 + "\n")
        
        passed = 0
        
        for i, case in enumerate(test_cases, 1):
            text = case['text']
            print(f"\nTest #{i}: '{text}'")
            f.write(f"\nTest #{i}: '{text}'\n")
            
            start_time = time.time()
            decision = controller.process(text, start_time)
            
            # Verification
            success = True
            
            if case['expect_response']:
                if not decision:
                    msg = f"❌ FAILED: Expected response, got None (Null Mode)"
                    print(msg)
                    f.write(msg + "\n")
                    success = False
                elif decision['intent'] != case['expected_intent']:
                    msg = f"❌ FAILED: Wrong intent. Expected {case['expected_intent']}, got {decision['intent']}"
                    print(msg)
                    f.write(msg + "\n")
                    success = False
                else:
                    msg = f"✅ PASSED: Got response ({decision['intent']})"
                    print(msg)
                    f.write(msg + "\n")
                    f.write(f"   Response: {decision['response'][:50]}...\n")
                    f.write(f"   Scores: Intent={decision['scores']['intent']:.3f}, RAG={decision['scores']['rag']:.3f}\n")
            else:
                if decision:
                    msg = f"❌ FAILED: Expected None, got response ({decision['intent']})"
                    print(msg)
                    f.write(msg + "\n")
                    f.write(f"   Scores: Intent={decision['scores']['intent']:.3f}, RAG={decision['scores']['rag']:.3f}\n")
                    success = False
                else:
                    msg = f"✅ PASSED: Correctly stayed silent"
                    print(msg)
                    f.write(msg + "\n")
                    
            if success:
                passed += 1
                
        f.write("=" * 60 + "\n")
        f.write(f"\n📊 Result: {passed}/{len(test_cases)} Tests Passed\n")
        
        if passed == len(test_cases):
            print("✅ COGNITIVE LAYER VERIFIED")
            f.write("✅ COGNITIVE LAYER VERIFIED\n")
        else:
            print("❌ VERIFICATION FAILED")
            f.write("❌ VERIFICATION FAILED\n")

if __name__ == "__main__":
    test_cognitive_layer()
