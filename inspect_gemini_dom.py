import asyncio
from playwright.async_api import async_playwright

async def inspect_gemini():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        query = "siapa pencipta kitab matan jurumiyah ?"
        print(f"Navigating to Gemini...")
        await page.goto("https://gemini.google.com/app", wait_until="domcontentloaded")
        await asyncio.sleep(5)
        
        if "accounts.google.com" in page.url:
            print("Blocked by login.")
            await browser.close()
            return

        selector = '.ql-editor.textarea.new-input-ui'
        print(f"Checking for input selector: {selector}")
        if await page.query_selector(selector):
            print("Input field found. Typing query...")
            await page.fill(selector, query)
            await page.keyboard.press("Enter")
            
            print("Waiting for response (15s)...")
            await asyncio.sleep(15)
            
            # Dump all class names and text of potential response elements
            print("Dumping potential response elements...")
            elements = await page.evaluate("""
                () => {
                    const results = [];
                    // Look for elements containing long text that aren't the query
                    const allDivs = document.querySelectorAll('div, p, span');
                    for (const el of allDivs) {
                        if (el.innerText && el.innerText.length > 50) {
                            results.push({
                                tag: el.tagName,
                                classes: el.className,
                                text: el.innerText.substring(0, 100)
                            });
                        }
                    }
                    return results;
                }
            """)
            
            for res in elements:
                if "pencipta" in res['text'].lower() or "shanhaji" in res['text'].lower():
                    print(f"MATCH FOUND: {res}")
            
            await page.screenshot(path="inspect_gemini_dom.png")
            print("Saved screenshot: inspect_gemini_dom.png")
        else:
            print("Input field NOT found.")
            # Let's see what's there
            await page.screenshot(path="inspect_gemini_fail.png")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_gemini())
