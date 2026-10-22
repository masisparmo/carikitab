import asyncio
from playwright.async_api import async_playwright
import urllib.parse

async def debug_cse():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        query = "تفسير ابن كثير"
        encoded_query = urllib.parse.quote(query)
        url = f"https://cse.google.com/cse?cx=01a21494071be20f9&q={encoded_query}"
        
        print(f"Opening: {url}")
        await page.goto(url, wait_until="domcontentloaded")
        
        # Wait for results
        print("Waiting for results...")
        try:
            await page.wait_for_selector("a.gs-title", timeout=15000)
            print("✅ Results found!")
            titles = await page.query_selector_all("a.gs-title")
            for t in titles[:3]:
                print(f" - {await t.inner_text()}")
        except Exception as e:
            print(f"❌ No results found or timeout: {e}")
            await page.screenshot(path="debug_cse_empty.png")
            print("Screenshot saved to debug_cse_empty.png")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_cse())
