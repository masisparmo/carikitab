import asyncio
import logging
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from app.services.google_ai_fallback import GoogleAIFallback

logging.basicConfig(level=logging.INFO)

async def test_fallback():
    query = "apa kitab-kitab tafsir quran yang metode tafsirnya adalah dengan menganalisa struktur kata, arti kata, nahfu, shorof ?"
    print(f"\n[TEST] Menguji Fallback AI dengan Pertanyaan: {query}\n")
    
    fallback = GoogleAIFallback()
    answer = await fallback.get_answer(query)
    
    if answer:
        print("\n" + "="*50)
        print("HASIL EKSTRAKSI BERHASIL:")
        print("="*50)
        print(answer)
        print("="*50 + "\n")
    else:
        print("\n[!] GAGAL: Tidak mendapatkan jawaban dari Google AI/Snippet.\n")

if __name__ == "__main__":
    asyncio.run(test_fallback())
