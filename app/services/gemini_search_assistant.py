import json
import httpx
import logging
import re
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

from app.services.gemini_key_rotator import GeminiKeyRotator
from app.services.llm_cache import llm_cache
from app.services.google_ai_fallback import GoogleAIFallback
from app.core.transliteration import transliterate_to_latin

# Singleton rotator to share state and cooldowns
global_rotator = GeminiKeyRotator()

class GeminiSearchAssistant:
    """
    Search Bridge & Translation Engine powered by Gemini 2.5 Flash.
    Strictly follows shamela.org/pdf patterns and prevents hallucination.
    """
    def __init__(self):
        self.key_rotator = global_rotator
        self.cache = llm_cache
        self.model = "gemini-2.0-flash"  # 2.0-flash has much higher rate limits for REST API search

    async def find_books_at_shamela(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Primary search method. Strictly filters results to ensure only real IDs are returned.
        """
        if not keyword: return []
        
        cache_key = f"search_v2_{keyword}"
        cached = self.cache.get_cache(cache_key)
        if cached: return cached

        prompt = f"""Search 'shamela.org/pdf' for: "{keyword}".
Return ONLY a JSON array of objects.
Keys: "judul_arab", "penulis_arab", "judul_indonesia", "penulis_indonesia", "detail_url" (must be https://shamela.org/pdf/...), "page_count", "file_size", "source": "gemini".

CRITICAL RULES:
- DO NOT guess or hallucinate book IDs.
- Real IDs are long alphanumeric strings (SHA-like).
- NEVER return IDs like '10001', '10002', etc. These are FAKE.
- If you can extract page count or file size from search context, do so, otherwise keep empty "".
- 'judul_indonesia' HARUS berisi transliterasi LATIN yang umum (contoh: 'Ihya Ulumiddin').
- 'penulis_indonesia' HARUS berisi transliterasi LATIN yang umum (contoh: 'Al-Ghazali').
- Jika Anda tidak menemukan real URLs, return an empty array [].
- JSON ONLY. Max 10 results."""

        results = await self._gemini_api_call(prompt, is_search=True)
        
        # VALIDATION: Strictly filter IDs.
        # Real IDs are long alphanumeric strings with underscores (e.g., 633ce60c8cbe7_...)
        def is_valid_url(url):
            if not url or not url.startswith("https://shamela.org/pdf/"): return False
            book_id = url.rstrip('/').split('/')[-1]
            return len(book_id) > 10 and re.match(r'^[a-f0-9_]+$', book_id.lower())

        validated = [r for r in results if is_valid_url(r.get('detail_url', ''))]
        
        if validated:
            self.cache.set_cache(cache_key, validated)
        return validated

    async def batch_translate_results(self, books: List[Dict]) -> List[Dict]:
        """
        Translates raw Arabic results to Indonesian with context awareness for Islamic literature.
        Now uses parallel execution for fallback to ensure speed.
        """
        if not books: return []
        
        # Prepare list for LLM context
        items = ""
        for i, b in enumerate(books[:15]):
            judul = b.get('judul_arab', b.get('title', ''))
            penulis = b.get('penulis_arab', '')
            items += f"{i+1}. Judul: {judul} | Penulis: {penulis}\n"
            
        prompt = f"""Anda adalah ahli transliterasi penulisan bahasa Arab ke huruf Latin.
Tugas Anda: UBAH seluruh teks judul dan nama penulis berbahasa Arab menjadi ejaan Latin (Transliterasi) sesuai cara bacanya.
DILARANG KERAS MENERJEMAHKAN MAKNA / ARTI KE DALAM BAHASA INDONESIA! 

Contoh Benar:
- إحياء علوم الدين -> Ihya Ulumuddin
- أبو حامد الغزالي -> Abu Hamid Al-Ghazali
- صحيح البخاري -> Shahih Al-Bukhari

Contoh Salah (KARENA DITERJEMAHKAN KE INDONESIA):
- إحياء علوم الدين -> Kebangkitan Ilmu Agama (SALAH!)
- منهاج القاصدين -> Jalan Orang yang Bertujuan (SALAH!)

DAFTAR JUDUL KITAB UNTUK DITRANSLITERASI:
{items}

ATURAN KHUSUS:
- 'judul_indonesia' HARUS berisi teks Transliterasi Latin dari judul asli.
- 'penulis_indonesia' HARUS berisi teks Transliterasi Latin dari penulis asli. Jika tidak ada penulis, isi string kosong.
- Pastikan format JSON valid.

KEMBALIKAN HANYA JSON array (tanpa markdown blok):
[{{"judul_indonesia": "...", "penulis_indonesia": "..."}}]"""

        try:
            translations = await self._gemini_api_call(prompt, is_search=False)
            
            if isinstance(translations, list) and len(translations) > 0:
                for i, trans in enumerate(translations):
                    if i < len(books):
                        t_ind = trans.get('judul_indonesia', '')
                        if t_ind and len(t_ind) > 3:
                            books[i]['judul_indonesia'] = t_ind
                            books[i]['penulis_indonesia'] = trans.get('penulis_indonesia', books[i].get('penulis_indonesia', ''))
                
                if all(b.get('judul_indonesia') for b in books):
                    return books
        except Exception as e:
            logger.error(f"[Gemini] API Translation failed: {e}")

        # --- LAPIS 2: WEB BROWSER AI FALLBACK (PLAYWRIGHT) ---
        logger.info("[Gemini] API Limit/Error. Mencoba Lapis 2: Web Browser AI (Playwright)...")
        try:
            browser_fallback = GoogleAIFallback(headless=True)
            # Karena batching 10 hasil dari main.py, prompt ini akan meminta JSON array kembali.
            web_response = await browser_fallback.get_answer(prompt)
            if web_response:
                # Cari JSON block di dalam respon teks bebas
                json_match = re.search(r'\[\s*\{.*\}\s*\]', web_response, re.DOTALL)
                if json_match:
                    try:
                        translations = json.loads(json_match.group(0))
                        if isinstance(translations, list):
                            for i, trans in enumerate(translations):
                                if i < len(books):
                                    books[i]['judul_indonesia'] = trans.get('judul_indonesia', '')
                                    books[i]['penulis_indonesia'] = trans.get('penulis_indonesia', '')
                            # Jika setidaknya judul tertransliterasi, anggap sukses Lapis 2
                            if all(b.get('judul_indonesia') for b in books):
                                return books
                    except:
                        logger.warning("[Gemini] Gagal mem-parsing JSON dari Browser Fallback.")
        except Exception as e:
            logger.error(f"[Gemini] Browser Fallback failed: {e}")

        # --- LAPIS 3: LOCAL OFFLINE TRANSLITERASI (FINAL SAFETY) ---
        logger.info("[Gemini] Lapis 1 & 2 Gagal. Mengaktifkan Lapis 3: Transliterasi Offline Lokal.")
        for b in books:
            # Pastikan teks Arab tidak dibiarkan apa adanya
            if b.get('judul_arab'):
                b['judul_indonesia'] = transliterate_to_latin(b['judul_arab'])
            if b.get('penulis_arab'):
                b['penulis_indonesia'] = transliterate_to_latin(b['penulis_arab'])
                
            # Pastikan fallback default string jika pemetaan kosong
            b['judul_indonesia'] = b.get('judul_indonesia') or b.get('judul_arab', 'Kitab')
            b['penulis_indonesia'] = b.get('penulis_indonesia') or b.get('penulis_arab', '')
            
        return books

    async def process_query(self, keyword: str) -> tuple[Optional[Dict], str]:
        """
        Query normalization (Arabic title extraction).
        Uses a 4-Layer Fallback strategy to bypass API limit.
        """
        # Quick check for non-latin
        if not re.search('[a-zA-Z]', keyword) and len(keyword) > 3:
            return {"arabic_title": keyword, "normalized_title": keyword}, ""
            
        # Lapis 1: Gemini API
        prompt = f"Detect language and provide strictly ONLY the Arabic title for keyword: '{keyword}'. Return JSON: {{\"arabic_title\": \"<arabic text>\", \"normalized_title\": \"<input text>\"}}"
        res = await self._gemini_api_call(prompt, is_search=False)
        
        # Validasi Lapis 1
        if isinstance(res, dict) and res.get("arabic_title") and re.search('[\u0600-\u06FF]', res.get("arabic_title")):
            return res, ""
            
        logger.warning("[Fallback] Lapis 1 (Gemini API) gagal mengubah query. Lanjut Lapis 2 (Gemini Web via Playwright)...")
        
        # Lapis 2 & Lapis 3 require Playwright
        from app.core.playwright_scraper import PlaywrightScraper
        p_scraper = PlaywrightScraper(headless=True)
        try:
            await p_scraper.start()
            page = p_scraper.page
            
            # Use English prompt to avoid "Tentu, ini bahasa arabnya..." wrapper text
            web_prompt = f"Translate the book name to Arabic. Just reply with the arabic letters and absolutely no other words: '{keyword}'"
            
            # Lapis 2: Gemini Web
            try:
                await page.goto("https://gemini.google.com/app", wait_until="domcontentloaded", timeout=35000)
                if not "accounts.google.com" in page.url:
                    input_selectors = ['div[contenteditable="true"]', 'div[role="textbox"]', '.ql-editor.textarea.new-input-ui', '.input-area p']
                    input_found = False
                    for sel in input_selectors:
                        try:
                            el = await page.wait_for_selector(sel, timeout=10000)
                            if el:
                                await page.click(sel)
                                await page.keyboard.press('Control+A')
                                await page.keyboard.press('Backspace')
                                await page.keyboard.type(web_prompt, delay=20)
                                await page.wait_for_timeout(500)
                                
                                try:
                                    send_btn = await page.wait_for_selector('button[aria-label*="Send"], button[mattooltip*="Send"], .send-button', timeout=2000)
                                    if send_btn: await send_btn.click()
                                    else: await page.keyboard.press("Enter")
                                except:
                                    await page.keyboard.press("Enter")
                                
                                input_found = True
                                break
                        except: pass
                    
                    if input_found:
                        try:
                            await page.wait_for_function(
                                "(sel) => { \
                                    const els = document.querySelectorAll(sel + ', .markdown-content, .message-content'); \
                                    if(els.length === 0) return false; \
                                    const last = els[els.length - 1]; \
                                    return last && last.innerText.length > 2; \
                                }",
                                arg='.model-response-text',
                                timeout=20000
                            )
                            # Stabilize for 2 seconds
                            await page.wait_for_timeout(2000)
                            ans = await page.evaluate("""
                                () => {
                                    const selectors = ['.model-response-text', '.markdown-content', 'div[role="article"]'];
                                    for (let s of selectors) {
                                        const els = document.querySelectorAll(s);
                                        if (els.length > 0) return els[els.length - 1].innerText.trim();
                                    }
                                    return '';
                                }
                            """)
                            if ans and re.search('[\u0600-\u06FF]', ans):
                                ans = ans.replace('"', '').replace("'", "").strip()
                                # Clean if AI still replies verbosely
                                if ":" in ans: ans = ans.split(":")[-1].strip()
                                logger.info(f"[Fallback] Lapis 2 (Gemini Web) berhasil: {ans}")
                                return {"arabic_title": ans, "normalized_title": keyword}, ""
                        except Exception as e:
                            logger.warning(f"[Fallback] Gemini Web respons timeout: {e}")
            except Exception as e:
                logger.warning(f"[Fallback] Lapis 2 Error: {e}")

            logger.warning("[Fallback] Lapis 2 gagal. Lanjut Lapis 3 (iAsk.ai)...")
            
            # Lapis 3: iAsk.ai/chat
            try:
                await page.goto("https://iask.ai/chat", wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(2000)
                
                # Check for alternative input text areas
                input_area = await page.wait_for_selector('textarea[placeholder*="Ask"], input[placeholder*="Ask"], textarea, .ProseMirror', timeout=10000)
                if input_area:
                    await input_area.click()
                    await page.keyboard.type(web_prompt, delay=30)
                    await page.wait_for_timeout(500)
                    
                    # Coba klik send button iAsk (ikon paper plane) atau Enter
                    try:
                        send_btn = await page.wait_for_selector('button[type="submit"]', timeout=3000)
                        if send_btn: await send_btn.click()
                        else: await page.keyboard.press('Enter')
                    except:
                        await page.keyboard.press('Enter')
                    
                    # Wait for results
                    await page.wait_for_selector('.prose, .message-content, article', timeout=25000)
                    await page.wait_for_timeout(3000) # Output generation duration
                    
                    ans = await page.evaluate("""
                        () => {
                            const answers = document.querySelectorAll('.prose, .message-content, article');
                            if (answers.length > 0) {
                                return answers[answers.length - 1].innerText.trim();
                            }
                            return '';
                        }
                    """)
                    if ans and re.search('[\u0600-\u06FF]', ans):
                        ans = ans.replace('"', '').replace("'", "").strip()
                        if ":" in ans: ans = ans.split(":")[-1].strip()
                        logger.info(f"[Fallback] Lapis 3 (iAsk.ai) berhasil: {ans}")
                        return {"arabic_title": ans, "normalized_title": keyword}, ""
            except Exception as e:
                logger.warning(f"[Fallback] Lapis 3 Error: {e}")

        except Exception as e:
            logger.error(f"[Fallback] Scraper Playwright gagal dijalankan: {e}")
        finally:
            await p_scraper.stop()
            
        logger.warning("[Fallback] Lapis 3 gagal. Lanjut Lapis 4 (Google Translate via HTTP)...")
        
        # Lapis 4: Google Translate via HTTP
        import urllib.parse
        from bs4 import BeautifulSoup
        try:
            url = f"https://translate.google.com/m?sl=id&tl=ar&q={urllib.parse.quote(keyword)}"
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"})
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, 'html.parser')
                    result_div = soup.find('div', class_='result-container')
                    if result_div:
                        arabic_text = result_div.get_text(strip=True)
                        if re.search('[\u0600-\u06FF]', arabic_text) and len(arabic_text) > 1:
                            logger.info(f"[Fallback] Lapis 4 (Google Translate) berhasil: {arabic_text}")
                            return {"arabic_title": arabic_text, "normalized_title": keyword}, ""
        except Exception as e:
            logger.warning(f"[Fallback] Lapis 4 Error: {e}")
            
        logger.error(f"[Fallback] Seluruh lapis transliterasi gagal untuk: '{keyword}'")
        return None, "Error: Semua Lapis Fallback (API, LLM Web, GT) gagal."

    async def _gemini_api_call(self, prompt: str, is_search: bool = False) -> Any:
        """
        Centralized Gemini API caller with rotation and robust JSON repair.
        Optimized to fail fast on 429 if no keys left.
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            for attempt in range(3): # Retries for intermittent network
                api_key = self.key_rotator.get_key()
                if not api_key: 
                    # If we tried and no keys are available (all on cooldown)
                    return [] if is_search else {}
                
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={api_key}"
                try:
                    payload = {
                        "contents": [{"parts": [{"text": prompt}]}], 
                        "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"}
                    }
                    response = await client.post(url, json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        text = data['candidates'][0]['content']['parts'][0]['text']
                        text = text.replace("```json", "").replace("```", "").strip()
                        
                        # JSON Repair logic
                        if is_search and not text.endswith(']'):
                            lb = text.rfind('}')
                            if lb != -1: text = text[:lb+1] + ']'
                        
                        return json.loads(text)
                    elif response.status_code == 429:
                        # Rate limit: report and immediately try next key in the loop
                        self.key_rotator.report_error(api_key, 429)
                        continue 
                    elif response.status_code == 503:
                        # Service overloaded: small wait then next key
                        self.key_rotator.report_error(api_key, 503)
                        await asyncio.sleep(1)
                        continue
                    else:
                        self.key_rotator.report_error(api_key, response.status_code)
                except Exception as e:
                    logger.error(f"[Gemini] API error: {e}")
                    self.key_rotator.report_error(api_key, 500)
                    
        return [] if is_search else {}

    def _transliterate_only(self, text: str) -> str:
        # Fallback transliteration for search engine
        return re.sub(r'[^\x00-\x7F]+', ' ', text).strip() or "Kitab"
