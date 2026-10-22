import asyncio
import logging
import os
import sys
import urllib.parse
from typing import Optional

# Add app directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.playwright_scraper import PlaywrightScraper

# Configure logging to file with utf-8
log_file = "test_ai_v140_log.txt"
file_handler = logging.FileHandler(log_file, encoding='utf-8')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', handlers=[file_handler])
logger = logging.getLogger("Version140Test")

class GoogleAIFallback_V140:
    def __init__(self, headless=True):
        self.p_scraper = PlaywrightScraper(headless=headless)

    async def get_answer(self, query: str, status_signal=None) -> Optional[str]:
        logger.info(f"[UniversalAI-V140] Starting fallback sequence for: {query}")
        try:
            await self.p_scraper.start()
            
            # --- PHASE 1: DUCKDUCKGO AI (Lapis 1) ---
            if status_signal: status_signal.emit("🤖 Mencoba Lapis 1: Duck.ai (V1.4.0 fast mode)...")
            ddg_res = await self._get_ddg_answer(query)
            if ddg_res: return ddg_res

            # --- PHASE 2: GEMINI WEB (Lapis 2) ---
            if status_signal: status_signal.emit("🤖 Mencoba Lapis 2: Gemini Web (V1.4.0 optimized)...")
            gemini_res = await self._get_gemini_web_answer(query)
            if gemini_res: return gemini_res

            # --- PHASE 3: GOOGLE SEARCH AI (Lapis 3) ---
            if status_signal: status_signal.emit("🤖 Mencoba Lapis 3: Google AI (V1.4.0)...")
            google_res = await self._get_google_search_answer(query)
            if google_res: return google_res
                
        except Exception as e:
            logger.error(f"[UniversalAI-V140] Critical failure: {e}")
        finally:
            await self.p_scraper.stop()
        return None

    async def _get_ddg_answer(self, query: str) -> Optional[str]:
        page = self.p_scraper.page
        try:
            url = f"https://duckduckgo.com/?q={urllib.parse.quote(query)}&ia=chat"
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            await page.wait_for_timeout(5000)
            
            # Use innerText to avoid HTML issues for now
            ans = await page.evaluate("""
                () => {
                    const msg = document.querySelector('.whitespace-normal.space-y-4') || 
                                document.querySelector('.result__snippet');
                    return msg ? msg.innerText : null;
                }
            """)
            if ans and len(ans) > 50:
                logger.info(f"[DDG] Success! Length: {len(ans)}")
                return f"<div class='ddg-response'>{ans}</div>"
        except Exception as e:
            logger.warning(f"[DDG] Attempt failed: {e}")
        return None

    async def _get_gemini_web_answer(self, query: str) -> Optional[str]:
        page = self.p_scraper.page
        try:
            await page.goto("https://gemini.google.com/app", wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_timeout(3000)
            
            selector = '.ql-editor.textarea.new-input-ui'
            if await page.query_selector(selector):
                await page.fill(selector, query)
                await page.keyboard.press("Enter")
                await page.wait_for_timeout(10000)
                
                ans = await page.evaluate("""
                    () => {
                        const msg = document.querySelector('.model-response-text');
                        return msg ? msg.innerText : null;
                    }
                """)
                if ans: 
                    logger.info(f"[Gemini-Web] Success! Length: {len(ans)}")
                    return f"<div class='gemini-web-response'>{ans}</div>"
        except Exception as e:
            logger.warning(f"[Gemini-Web] Attempt failed: {e}")
        return None

    async def _get_google_search_answer(self, query: str) -> Optional[str]:
        page = self.p_scraper.page
        try:
            url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&udm=50"
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            await page.wait_for_timeout(5000)
            
            result = await page.evaluate("""
                () => {
                    const ai = document.querySelector('.Y3BBE') || document.querySelector('[jscontroller="zcfIf"]');
                    if (ai) return { type: 'ai', text: ai.innerText };
                    const snip = document.querySelector('.LGOve, .hgKAtc, .VwiC3b');
                    if (snip) return { type: 'snippet', text: snip.innerText };
                    return null;
                }
            """)
            if result:
                logger.info(f"[Google-Search] Success ({result['type']})")
                return f"<div>{result['text']}</div>"
        except Exception as e:
            logger.warning(f"[Google-Search] Attempt failed: {e}")
        return None

async def run_v140_test():
    query = "apa kitab-kitab tafsir quran yang metode tafsirnya adalah dengan menganalisa struktur kata, arti kata, nahfu, shorof ?"
    
    from app.services.google_ai_fallback import GoogleAIFallback
    fallback = GoogleAIFallback(headless=False)
    
    class MockSignal:
        def emit(self, text):
            logger.info(f"[STATUS] {text}")

    start_time = asyncio.get_event_loop().time()
    try:
        ans = await asyncio.wait_for(fallback.get_answer(query, status_signal=MockSignal()), timeout=90)
        end_time = asyncio.get_event_loop().time()
        
        with open("test_v140_result.txt", "w", encoding="utf-8") as f:
            if ans:
                f.write(f"--- SUCCESS (V1.4.0) ---\n")
                f.write(f"Time taken: {end_time - start_time:.2f}s\n\n")
                f.write(ans)
            else:
                f.write(f"--- FAILED ---\n")
                f.write(f"Time taken: {end_time - start_time:.2f}s\n")
    except Exception as e:
        with open("test_v140_result.txt", "w", encoding="utf-8") as f:
            f.write(f"--- ERROR ---\n{str(e)}")

if __name__ == "__main__":
    asyncio.run(run_v140_test())
