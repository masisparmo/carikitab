import asyncio
import logging
import os
import sys
import datetime

# Add project root to sys.path
sys.path.append(os.getcwd())

from app.services.google_ai_fallback import GoogleAIFallback

# Setup logging to console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def debug_realtime():
    print("--- STARTING REAL-TIME FALLBACK DEBUG (v1.5.7) ---")
    query = "siapa penulis kitab matan jurumiyah ?"
    
    fallback = GoogleAIFallback(headless=True)
    
    async def capture(name):
        timestamp = datetime.datetime.now().strftime("%H%M%S")
        img_path = f"debug_fallback_{name}_{timestamp}.png"
        html_path = f"debug_fallback_{name}_{timestamp}.html"
        await fallback.p_scraper.page.screenshot(path=img_path)
        html = await fallback.p_scraper.page.content()
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Captured: {img_path} and {html_path}")

    # Patch engine methods
    orig_gemini = fallback._get_gemini_web_answer
    async def patched_gemini(q):
        print(f"Testing Gemini Web Lapis 2...")
        res = await orig_gemini(q)
        await capture("gemini_final")
        return res
    fallback._get_gemini_web_answer = patched_gemini

    # Run
    start_time = asyncio.get_event_loop().time()
    try:
        ans = await fallback.get_answer(query)
        end_time = asyncio.get_event_loop().time()
        
        print("\n" + "="*40)
        if ans:
            print(f"SUCCESS in {end_time - start_time:.2f}s!")
            print(f"Result Preview: {ans[:300]}...")
        else:
            print(f"FAILED to get answer from all engines in {end_time - start_time:.2f}s.")
        print("="*40)
        
    except Exception as e:
        print(f"\nERROR during debug: {e}")

if __name__ == "__main__":
    asyncio.run(debug_realtime())
