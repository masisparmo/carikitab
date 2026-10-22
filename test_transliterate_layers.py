import asyncio
import logging
import sys
import os

# Setup path
sys.path.append(os.getcwd())

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestTransliterate")

from app.core.transliteration import transliterate_to_latin
from app.services.gemini_search_assistant import GeminiSearchAssistant

async def test_offline_transliteration():
    print("\n=== TEST 1: OFFLINE TRANSLITERATION (LAPIS 3) ===")
    test_cases = [
        "إحياء علوم الدين",
        "أبو حامد الغzالي", # Mixed or typo-ish
        "صحيح البخاري",
        "التفسير من مجموع الفتاوى لشيخ الإسلام ابن تيمية",
        "منهاج القاصدين"
    ]
    
    for tc in test_cases:
        result = transliterate_to_latin(tc)
        print(f"Arab: {tc}")
        print(f"Latin (Offline): {result}")
        print("-" * 30)

async def test_full_assistant_fallback():
    print("\n=== TEST 2: FULL ASSISTANT FALLBACK (LAPIS 1/2/3) ===")
    assistant = GeminiSearchAssistant()
    
    books = [
        {"judul_arab": "كتاب التوحيد", "penulis_arab": "محمد بن عبد الوهاب"},
        {"judul_arab": "رياض الصالحين", "penulis_arab": "الإمام النووي"}
    ]
    
    # This will likely hit Lapis 1 (API) if keys are fresh, 
    # or Lapis 2 (Browser) if 429, 
    # or Lapis 3 (Local) if browser fails.
    results = await assistant.batch_translate_results(books)
    
    for i, b in enumerate(results):
        print(f"Book {i+1}:")
        print(f"  Arab: {b['judul_arab']}")
        print(f"  Latin: {b.get('judul_indonesia')}")
        print(f"  Author Latin: {b.get('penulis_indonesia')}")

if __name__ == "__main__":
    asyncio.run(test_offline_transliteration())
    # Note: test_full_assistant_fallback() will open Playwright browser if API is 429.
    # asyncio.run(test_full_assistant_fallback())
