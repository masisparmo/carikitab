import asyncio
from playwright.async_api import async_playwright

async def find_input():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        print(f"Navigating to Gemini...")
        await page.goto("https://gemini.google.com/app", wait_until="domcontentloaded")
        await asyncio.sleep(5)
        
        # Log all elements that look like input/textareas
        elements = await page.evaluate("""
            () => {
                const results = [];
                const all = document.querySelectorAll('div, textarea, input');
                for (const el of all) {
                    if (el.innerText && el.innerText.includes('Ask Gemini')) {
                        results.push({
                            tag: el.tagName,
                            classes: el.className,
                            id: el.id,
                            placeholder: el.placeholder,
                            innerText: el.innerText
                        });
                    }
                }
                return results;
            }
        """)
        print("Potential input elements:")
        for e in elements:
            print(e)
            
        await page.screenshot(path="find_gemini_input.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(find_input())
