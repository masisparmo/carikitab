import asyncio
from playwright.async_api import async_playwright

async def test_chatgpt():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        query = "siapa penulis kitab fathul bari ?"
        print(f"Navigating to ChatGPT...")
        try:
            await page.goto("https://chatgpt.com/", wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(5)
            
            # Check for input field
            # Common selectors for ChatGPT input: #prompt-textarea, [data-testid="text-input"]
            selector = '#prompt-textarea'
            if await page.query_selector(selector):
                print("Input field found. Typing...")
                await page.fill(selector, query)
                await page.keyboard.press("Enter")
                
                print("Waiting for response (15s)...")
                await asyncio.sleep(15)
                
                ans = await page.evaluate("""
                    () => {
                        const msgs = document.querySelectorAll('.markdown');
                        return msgs.length > 0 ? msgs[msgs.length - 1].innerText : null;
                    }
                """)
                if ans:
                    print(f"SUCCESS: {ans[:200]}...")
                else:
                    print("Response NOT found in .markdown")
            else:
                print("Input field NOT found.")
                
            await page.screenshot(path="test_chatgpt_anon.png")
            
        except Exception as e:
            print(f"FAILED: {e}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_chatgpt())
