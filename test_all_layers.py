import asyncio
import logging
import os
import sys
import re

# Add app directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.google_ai_fallback import GoogleAIFallback

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("LayerTest")

def format_arabic_links(ans):
    """Simulates the Regex Formatter from app/main.py"""
    if not ans: return None
    pattern = r'([A-Za-z0-9\s\'-]+?)\s*\(([\u0600-\u06FF\s]+)\)'
    formatted = re.sub(
        pattern,
        r'<a href="search:\2">\1</a> (<a href="search:\2">\2</a>)',
        ans
    )
    return formatted

async def test_layer(name, fallback_method, query, fallback_instance, screenshot_name):
    logger.info(f"\n{'='*40}\nMENGUJI LAPIS: {name}\n{'='*40}")
    try:
        # Prompt injection just like in app/main.py
        system_instruction = "Sajikan jawaban dalam Bahasa Indonesia. WAJIB sertakan tulisan Arab aslinya di dalam kurung setelah setiap Anda menyebutkan judul kitab atau nama ulama (Contoh: Tafsir Al-Jalalain (تفسير الجلالين)). Pertanyaan: "
        fallback_prompt = system_instruction + query
        
        logger.info("Menjalankan scraper...")
        # Await the specific method
        ans = await fallback_method(fallback_prompt)
        
        logger.info("Mengambil screenshot browser internal...")
        await fallback_instance.p_scraper.page.screenshot(path=screenshot_name, full_page=True)
        
        if ans:
            logger.info("Jawaban mentah berhasil didapatkan. Memproses regex...")
            formatted_ans = format_arabic_links(ans)
            
            # Save raw and formatted to HTML for inspection
            html_content = f"""
            <html><head><meta charset="utf-8"></head><body style="font-family: Arial; line-height: 1.6; padding: 20px;">
            <h2>Hasil {name}</h2>
            <hr>
            {formatted_ans}
            </body></html>
            """
            with open(f"result_{name.replace(' ', '_').lower()}.html", "w", encoding="utf-8") as f:
                f.write(html_content)
                
            logger.info(f"VERDICT: SUKSES. Panjang HTML = {len(formatted_ans)} chars. Lihat {screenshot_name}")
            return True, formatted_ans
        else:
            logger.error(f"VERDICT: GAGAL ATAU TIMEOUT. Lihat {screenshot_name}")
            return False, "Tidak ada jawaban yang diekstrak."
            
    except Exception as e:
        logger.error(f"CRITICAL ERROR pada {name}: {e}")
        return False, str(e)

async def run_all_tests():
    query = "sebutkan 7 kitab karya ibnu katsir"
    fallback = GoogleAIFallback(headless=True) # Pakai headless agar cepat, screenshot tetap jalan
    
    await fallback.p_scraper.start()
    
    try:
        # Lapis 1: Brave Search AI
        await test_layer("Lapis 1 Brave AI", fallback._get_brave_ai_answer, query, fallback, "screenshot_lapis1_brave.png")
        
        # Reset context to be safe
        await fallback.p_scraper.stop()
        await fallback.p_scraper.start()
        
        # Lapis 2: Gemini Web
        await test_layer("Lapis 2 Gemini Web", fallback._get_gemini_web_answer, query, fallback, "screenshot_lapis2_gemini.png")
        
        await fallback.p_scraper.stop()
        await fallback.p_scraper.start()
        
        # Lapis 3: Google Search AI
        await test_layer("Lapis 3 Google Search AI", fallback._get_google_search_answer, query, fallback, "screenshot_lapis3_google.png")
        
    finally:
        await fallback.p_scraper.stop()
        logger.info("======== SEMUA PENGUJIAN SELESAI ========")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
