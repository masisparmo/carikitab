import asyncio
import os
import sys

# Ensure app is in path
sys.path.append(os.getcwd())

from app.services.gemini_key_rotator import GeminiKeyRotator

async def test_key_rotator_fixed():
    print("Testing KeyRotator with simulated error (should not crash)...")
    rotator = GeminiKeyRotator()
    # Simulate a key if none exist
    if not rotator.keys:
        rotator.keys = ["AIzaSyDummyKeyForTesting"]
    
    # This should now print [LIMIT] instead of red circle emoji
    rotator.report_error(rotator.keys[0], 429)
    print("Success: KeyRotator did not crash.")

async def test_search_logic():
    print("\nTesting search query normalization (simulated)...")
    from app.services.gemini_search_assistant import GeminiSearchAssistant
    assistant = GeminiSearchAssistant()
    
    # Test normalization of 'minhajul qosidin'
    # Note: This requires a valid API key to perform actual AI normalization
    # If keys are missing or limited, it should fail gracefully
    try:
        res, err = await assistant.process_query("minhajul qosidin")
        if res:
            print(f"Normalized: {res.get('arabic_title')} ({res.get('normalized_title')})")
        else:
            print(f"Normalization skipped or failed: {err}")
    except Exception as e:
        print(f"Normalization CRASHED (this is bad): {e}")

if __name__ == "__main__":
    asyncio.run(test_key_rotator_fixed())
    asyncio.run(test_search_logic())
