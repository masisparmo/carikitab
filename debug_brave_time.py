import asyncio
import sys
sys.path.append('.')

from app.services.google_ai_fallback import GoogleAIFallback

async def test_brave():
    q = "Sajikan jawaban dalam Bahasa Indonesia. WAJIB sertakan tulisan Arab aslinya di dalam kurung setelah setiap Anda menyebutkan judul kitab atau nama ulama (Contoh: Tafsir Al-Jalalain (تفسير الجلالين)). Pertanyaan: 🔍 <b>Menganalisis Kitab:</b> Al-Mawdu'at (Hadis-hadis Palsu) Karya Ibn al-Jawzi<br>Silakan tunggu, saya sedang membedah 10 halaman awal untuk memberikan resume mendalam..."
    
    fallback = GoogleAIFallback(headless=True)
    await fallback.p_scraper.start()
    
    print("Testing Brave AI...")
    ans = await fallback._get_brave_ai_answer(q)
    print("====== BRAVE RESULT ======")
    print(ans)
    print("==========================")
    
    await fallback.p_scraper.close()

if __name__ == "__main__":
    asyncio.run(test_brave())
