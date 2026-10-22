import asyncio
from playwright.async_api import async_playwright
import logging

logging.basicConfig(level=logging.INFO)

async def test_ddg():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
        page = await context.new_page()
        try:
            logging.info("Going to duck.ai")
            try:
                await page.goto("https://duck.ai", wait_until="commit", timeout=15000)
                logging.info("Goto finished naturally.")
            except Exception as e:
                logging.warning(f"Goto timeout/error ignored: {e}")
            
            logging.info("Waiting for welcome button...")
            get_started = await page.wait_for_selector('[data-testid="chat-welcome-button"]', timeout=10000)
            if get_started:
                logging.info("Found Welcome button! Clicking...")
                await get_started.click()
                i_agree = await page.wait_for_selector('[data-testid="chat-terms-accept"]', timeout=3000)
                if i_agree: 
                    logging.info("Found Agree button! Clicking...")
                    await i_agree.click()
            
            logging.info("Waiting for textarea...")
            input_area = await page.wait_for_selector('textarea', timeout=10000)
            if input_area:
                logging.info("Success! Textarea found. Filling input.")
                await input_area.fill("tes tes 123")
                await page.keyboard.press("Enter")
            else:
                logging.warning("Textarea not found.")

        except Exception as e:
            logging.error(f"Error: {e}")
        finally:
            await asyncio.sleep(3)
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_ddg())
