import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://gemini.google.com/app", wait_until="networkidle")
        await asyncio.sleep(5)
        
        # Get the selector of the focused element or all textboxes
        selectors = await page.evaluate("""
            () => {
                const boxes = document.querySelectorAll('div[contenteditable="true"], div[role="textbox"], textarea');
                return Array.from(boxes).map(b => ({
                    tag: b.tagName,
                    id: b.id,
                    className: b.className,
                    ariaLabel: b.getAttribute('aria-label'),
                    placeholder: b.getAttribute('placeholder')
                }));
            }
        """)
        print("Textboxes found:")
        for s in selectors:
            print(s)
            
        await page.screenshot(path="gemini_textbox_debug.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect())
