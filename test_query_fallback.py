import asyncio
import logging
import os
from app.services.gemini_search_assistant import GeminiSearchAssistant
from app.core.utils import get_data_dir

# Enable logging to see the fallback steps
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

async def test_fallback():
    # Buat API key sengaja salah agar API layer gagal (memancing fallback)
    os.environ["GEMINI_API_KEYS"] = "AIzaSy_FAKE_KEY_FOR_TESTING"
    
    # Reset internal key rotator
    from app.services.gemini_search_assistant import global_rotator
    global_rotator.reload_keys()

    assistant = GeminiSearchAssistant()
    print("Mencoba process_query untuk kata: 'minhajul qosidin'")
    
    result, err = await assistant.process_query("minhajul qosidin")
    print(f"\nHasil: {result}")
    print(f"Error: {err}")

if __name__ == "__main__":
    asyncio.run(test_fallback())
