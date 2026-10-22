import asyncio
import logging
import os
import sys
import urllib.parse
from typing import Optional

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.core.playwright_scraper import PlaywrightScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EngineTest")

async def test_engine(name, func, query):
    print(f"\n--- TESTING ENGINE: {name} ---")
    scraper = PlaywrightScraper(headless=True)
    await scraper.start()
    try:
        ans = await asyncio.wait_for(func(scraper.page, query), timeout=45)
        if ans:
            print(f"✅ {name} SUCCESS!")
            print(f"Preview: {ans[:200]}...")
        else:
            print(f"❌ {name} FAILED (No response)")
    except Exception as e:
        print(f"❌ {name} ERROR: {e}")
        # Save screenshot
        await scraper.page.screenshot(path=f"test_{name.lower().replace(' ', '_')}_fail.png")
    finally:
        await scraper.stop()

async def ddg_logic(page, query):
    url = f"https://duckduckgo.com/?q={urllib.parse.quote(query)}&ia=chat"
    await page.goto(url, wait_until="domcontentloaded", timeout=20000)
    await page.wait_for_timeout(7000)
    return await page.evaluate("() => document.querySelector('.whitespace-normal.space-y-4')?.innerText || null")

async def gemini_logic(page, query):
    await page.goto("https://gemini.google.com/app", wait_until="domcontentloaded", timeout=20000)
    await page.wait_for_timeout(5000)
    # Check if we are on a login page
    if "accounts.google.com" in page.url:
        return "BLOCKED: Login required"
    return "STILL WORKING ON SELECTORS"

async def google_logic(page, query):
    url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&udm=50"
    await page.goto(url, wait_until="domcontentloaded", timeout=20000)
    await page.wait_for_timeout(7000)
    return await page.evaluate("""
        () => {
            const ai = document.querySelector('.Y3BBE') || document.querySelector('[jscontroller="zcfIf"]');
            if (ai) return ai.innerText;
            const snip = document.querySelector('.LGOve, .hgKAtc, .VwiC3b');
            return snip ? snip.innerText : null;
        }
    """)

async def run():
    query = "apa kitab-kitab tafsir quran yang metode tafsirnya adalah dengan menganalisa struktur kata, arti kata, nahfu, shorof ?"
    await test_engine("DuckDuckGo AI", ddg_logic, query)
    await test_engine("Gemini Web", gemini_logic, query)
    await test_engine("Google AI", google_logic, query)

if __name__ == "__main__":
    asyncio.run(run())
