import asyncio
from playwright.async_api import async_playwright

async def debug_brave_upload():
    url = "https://search.brave.com/ask"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = await context.new_page()
        print(f"Loading {url}...")
        await page.goto(url, wait_until="domcontentloaded")
        
        await asyncio.sleep(5)
        
        # Cari input type file terpembunyi
        file_inputs = await page.query_selector_all('input[type="file"]')
        print(f"Ditemukan {len(file_inputs)} input file.")
        
        for idx, inp in enumerate(file_inputs):
            mul = await inp.get_attribute('multiple')
            acc = await inp.get_attribute('accept')
            print(f"Input {idx+1} - Multiple: {mul}, Accept: {acc}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_brave_upload())
