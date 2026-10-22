import logging
import asyncio
from typing import Optional
import urllib.parse
from app.core.playwright_scraper import PlaywrightScraper

logger = logging.getLogger(__name__)

class GoogleAIFallback:
    """
    Universal AI Fallback Scraper.
    Tries multiple AI web interfaces in order to get a response when API is limit.
    Order: 1. Brave Search AI, 2. Gemini Web, 3. Google Search AI
    """
    
    def __init__(self, headless=True):
        # Forced headless=True to hide browser fallback from user!
        self.p_scraper = PlaywrightScraper(headless=True)

    async def get_answer(self, query: str, status_signal=None) -> Optional[str]:
        """
        Main entry point for multi-engine fallback.
        """
        logger.info(f"[UniversalAI] Starting fallback sequence for: {query}")
        
        try:
            await self.p_scraper.start()
            page = self.p_scraper.page
            
            # --- PHASE 1: GEMINI WEB (Lapis 1) ---
            if status_signal: status_signal.emit("🤖 Mencoba Lapis 1: Gemini Web (Recommended)...")
            gemini_res = await self._get_gemini_web_answer(query)
            if gemini_res: return gemini_res

            # --- PHASE 2: BRAVE SEARCH AI (Lapis 2) ---
            if status_signal: status_signal.emit("🤖 Mencoba Lapis 2: Brave AI...")
            brave_res = await self._get_brave_ai_answer(query)
            if brave_res: return brave_res

            # --- PHASE 3: GOOGLE SEARCH AI (Lapis 3) ---
            if status_signal: status_signal.emit("🤖 Mencoba Lapis 3: Google AI...")
            google_res = await self._get_google_search_answer(query)
            if google_res: return google_res
                
        except Exception as e:
            logger.error(f"[UniversalAI] Critical failure in sequence: {e}")
        finally:
            await self.p_scraper.stop()
            
        return None

    async def _get_brave_ai_answer(self, query: str) -> Optional[str]:
        """Scrapes Brave Search AI (The Best Alternative)."""
        page = self.p_scraper.page
        try:
            url = f"https://search.brave.com/ask?q={urllib.parse.quote(query)}"
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)

            # --- Wait for Response generation ---
            try:
                # Brave uses .llm-output within .message.assistant or .answer-content
                await page.wait_for_function(
                    "() => { \
                        const el = document.querySelector('.llm-output') || document.querySelector('.answer-content') || document.querySelector('.markdown'); \
                        return el && el.innerText.length > 50; \
                    }",
                    timeout=25000
                )
                
                # 2. Stabilitas Streaming Cerdas untuk Brave AI (Menunggu ngetik selesai)
                logger.info("[Brave-AI] AI sedang mengetik, menunggu streaming selesai...")
                await page.evaluate("""
                    () => {
                        return new Promise((resolve) => {
                            let lastLen = 0;
                            let sameCount = 0;
                            let elapsed = 0;
                            const interval = setInterval(() => {
                                elapsed += 500;
                                const el = document.querySelector('.llm-output') || document.querySelector('.answer-content') || document.querySelector('.markdown');
                                let currentLen = el ? el.innerText.length : 0;
                                
                                if(currentLen > 100 && currentLen === lastLen) {
                                    sameCount++;
                                    if(sameCount >= 4) { // 2 detik stabil
                                        clearInterval(interval);
                                        resolve(true);
                                    }
                                } else {
                                    sameCount = 0;
                                    lastLen = currentLen;
                                }
                                
                                if(elapsed > 30000) { // Limit waktu ngetik Brave AI
                                    clearInterval(interval);
                                    resolve(false);
                                }
                            }, 500);
                        });
                    }
                """)
            except Exception:
                logger.warning("[Brave-AI] Timeout respon streaming.")
            
            await page.wait_for_timeout(1000)

            # --- Rich Text Extraction (innerHTML preserves paragraphs & lists) ---
            ans = await page.evaluate("""
                () => {
                    const el = document.querySelector('.llm-output') || document.querySelector('.answer-content') || document.querySelector('.markdown');
                    return el ? el.innerHTML : null;
                }
            """)
            
            if ans and len(ans) > 30:
                return f"<div style='line-height: 1.6;'>{self._clean_html(ans)}</div>"
        except Exception as e:
            logger.warning(f"[Brave-AI] Percobaan gagal: {e}")
        return None

    async def _get_gemini_web_answer(self, query: str) -> Optional[str]:
        """Scrapes Gemini Web (Anonymous mode)."""
        page = self.p_scraper.page
        try:
            # V1.5.3: Increased timeout and better load check
            await page.goto("https://gemini.google.com/app", wait_until="domcontentloaded", timeout=35000)
            
            if "accounts.google.com" in page.url:
                logger.warning("[Gemini-Web] Terblokir layar login.")
                return None

            # Blank page check
            if not await page.query_selector('div'):
                logger.warning("[Gemini-Web] Halaman kosong, mencoba reload...")
                await page.reload(wait_until="domcontentloaded")

            # Simulation of Typing
            input_selectors = [
                'div[contenteditable="true"]',
                'div[role="textbox"]',
                '.ql-editor.textarea.new-input-ui',
                '.input-area p'
            ]
            
            input_found = False
            for sel in input_selectors:
                try:
                    el = await page.wait_for_selector(sel, timeout=10000)
                    if el:
                        logger.info(f"[Gemini-Web] Menggunakan selector: {sel}")
                        await page.click(sel)
                        # Clear field first
                        await page.keyboard.press('Control+A')
                        await page.keyboard.press('Backspace')
                        await page.keyboard.type(query, delay=30)
                        await page.wait_for_timeout(1000)
                        
                        # Try to click Send button explicitly
                        try:
                            send_btn = await page.wait_for_selector('button[aria-label*="Send"], button[mattooltip*="Send"], .send-button', timeout=2000)
                            if send_btn:
                                await send_btn.click()
                            else:
                                await page.keyboard.press("Enter")
                        except Exception:
                            await page.keyboard.press("Enter")
                            
                        input_found = True
                        break
                except: continue

            if input_found:
                # Wait for response to have content and finish streaming
                try:
                    # 1. Pastikan jawaban mulai muncul (min 50 karakter)
                    await page.wait_for_function(
                        "(sel) => { \
                            const els = document.querySelectorAll(sel + ', .markdown-content, .message-content'); \
                            if(els.length === 0) return false; \
                            const last = els[els.length - 1]; \
                            return last && last.innerText.length > 50; \
                        }",
                        arg='.model-response-text',
                        timeout=35000
                    )
                    
                    # 2. Stabilitas Streaming Cerdas (Tunggu sampai AI berhenti ngetik)
                    logger.info("[Gemini-Web] AI sedang mengetik, menunggu hingga selesai...")
                    await page.evaluate("""
                        (sel) => {
                            return new Promise((resolve) => {
                                let lastLen = 0;
                                let sameCount = 0;
                                let elapsed = 0;
                                const interval = setInterval(() => {
                                    elapsed += 500;
                                    const els = document.querySelectorAll(sel + ', .markdown-content, .message-content');
                                    let currentLen = 0;
                                    if(els.length > 0) {
                                        currentLen = els[els.length - 1].innerText.length;
                                    }
                                    
                                    if(currentLen > 100 && currentLen === lastLen) {
                                        sameCount++;
                                        if(sameCount >= 5) { // 2.5 detik tanpa ada teks baru = Selesai
                                            clearInterval(interval);
                                            resolve(true);
                                        }
                                    } else {
                                        sameCount = 0;
                                        lastLen = currentLen;
                                    }
                                    
                                    if(elapsed > 45000) { // Batas mentok pengetikan 45 detik
                                        clearInterval(interval);
                                        resolve(false);
                                    }
                                }, 500);
                            });
                        }
                    """, arg='.model-response-text')
                except Exception:
                    logger.warning("[Gemini-Web] Timeout sinkronisasi jawaban AI melampaui batas.")
                
                await page.wait_for_timeout(1000)
                
                # Extract Rich Text (innerHTML) for professional UI
                ans = await page.evaluate("""
                    () => {
                        const selectors = ['.model-response-text', '.markdown-content', 'div[role="article"]'];
                        for (let s of selectors) {
                            const els = document.querySelectorAll(s);
                            if (els.length > 0) {
                                const last = els[els.length - 1];
                                if (last.innerText.length > 100) return last.innerHTML;
                            }
                        }
                        return null; // Don't guess if not found
                    }
                """)
                if ans: return f"<div style='line-height: 1.6;'>{self._clean_html(ans)}</div>"
            else:
                logger.warning("[Gemini-Web] Kolom input tidak ditemukan.")
        except Exception as e:
            logger.warning(f"[Gemini-Web] Gangguan teknis: {e}")
        return None

    async def _get_google_search_answer(self, query: str) -> Optional[str]:
        """Scrapes Google Search AI Mode / Snippet (Final Guard)."""
        page = self.p_scraper.page
        try:
            url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&udm=50"
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            await page.wait_for_timeout(6000)
            
            # If we see CAPTCHA, don't wait 15s, fail immediately
            if await page.query_selector('#captcha-form'):
                logger.warning("[Google-Search] Blocked by CAPTCHA.")
                return None

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
                content = result['text']
                note = "<i>(Analisis Mesin Pencari)</i>" if result['type'] == 'snippet' else ""
                return f"<div>{note}{content}</div>"
        except Exception as e:
            logger.warning(f"[Google-Search] Attempt failed: {e}")
        return None

    def _clean_html(self, html: str) -> str:
        import re
        # Remove weird classes but keep structural tags (p, br, b, i, ul, li)
        text = re.sub(r' class="[^"]*"', '', html)
        text = re.sub(r' id="[^"]*"', '', html)
        text = re.sub(r' style="[^"]*"', '', text)
        text = re.sub(r'\[\d+\]', '', text) # Remove citations
        # If no explicit rich tags are found but it has newlines (fallback)
        if '<p>' not in text.lower() and '<br' not in text.lower():
            text = text.replace('\n', '<br>')
            
        return text
