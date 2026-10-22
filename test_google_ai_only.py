import asyncio
import logging
import os
import sys
import urllib.parse
from typing import Optional

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.core.playwright_scraper import PlaywrightScraper

async def google_only_test():
    query = "apa kitab-kitab tafsir quran yang metode tafsirnya adalah dengan menganalisa struktur kata, arti kata, nahfu, shorof ?"
    print(f"--- TESTING GOOGLE AI ONLY FOR: {query} ---")
    
    scraper = PlaywrightScraper(headless=True)
    await scraper.start()
    try:
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&udm=50"
        print(f"Navigating to: {url}")
        await scraper.page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await scraper.page.wait_for_timeout(8000)
        
        result = await scraper.page.evaluate("""
            () => {
                const ai = document.querySelector('.Y3BBE') || document.querySelector('[jscontroller="zcfIf"]');
                if (ai) return { type: 'AI Overview', text: ai.innerText };
                const snip = document.querySelector('.LGOve, .hgKAtc, .VwiC3b');
                if (snip) return { type: 'Snippet', text: snip.innerText };
                return null;
            }
        """)
        
        if result:
            print(f"✅ SUCCESS! Type: {result['type']}")
            print(f"Content: {result['text'][:500]}...")
            with open("google_test_success.txt", "w", encoding="utf-8") as f:
                f.write(result['text'])
        else:
            print("❌ FAILED: No AI overview or snippet found.")
            await scraper.page.screenshot(path="google_failed_capture.png")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    finally:
        await scraper.stop()

if __name__ == "__main__":
    asyncio.run(google_only_test())
