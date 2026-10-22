import asyncio
import logging
import os
from playwright.async_api import async_playwright
import playwright_stealth
import re
from typing import List, Dict, Any, Optional
from app.core.transliteration import transliterate_to_arabic

logger = logging.getLogger(__name__)

def get_playwright_browsers_path():
    """Get a writable directory for playwright browsers in AppData"""
    if os.name == 'nt':
        base = os.environ.get('APPDATA') or os.path.expanduser('~\\AppData\\Roaming')
        path = os.path.join(base, "Cari Kitab", "playwright-browsers")
    else:
        base = os.path.expanduser('~')
        path = os.path.join(base, ".cari_kitab", "playwright-browsers")
    
    os.makedirs(path, exist_ok=True)
    return path

class PlaywrightScraper:
    def __init__(self, headless=True):
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
        
        # Ensure browsers path is set before starting
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = get_playwright_browsers_path()

    async def start(self):
        if not self.playwright:
            logger.info(f"[Playwright] Starting with browsers at: {os.environ.get('PLAYWRIGHT_BROWSERS_PATH')}")
            self.playwright = await async_playwright().start()
            try:
                self.browser = await self.playwright.chromium.launch(headless=self.headless)
            except Exception as e:
                logger.error(f"[Playwright] Launch failed: {e}")
                # If launch fails, maybe browsers are not installed
                raise RuntimeError("Browser not found. Please click 'Repair Search' in Settings.")
            
            self.context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            )
            self.page = await self.context.new_page()
            
            # Apply stealth robustly
            try:
                if hasattr(playwright_stealth, 'stealth'):
                    f = playwright_stealth.stealth
                    if not callable(f) and hasattr(f, 'stealth'):
                        f = f.stealth
                    if callable(f):
                        if asyncio.iscoroutinefunction(f):
                            await f(self.page)
                        else:
                            f(self.page)
            except Exception as e:
                logger.warning(f"[Playwright] Stealth failure (non-critical): {e}")

    async def stop(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None

    async def search_shamela(self, query: str, page_num: int = 1) -> List[Dict[str, Any]]:
        """
        Searches shamela.org and handles Google CSE popup results with optional pagination.
        """
        if not query: return []
        
        try:
            if not self.browser:
                await self.start()
            
            # 1. Convert to Arabic if needed
            from app.core.transliteration import transliterate_to_arabic, is_arabic
            arabic_query = transliterate_to_arabic(query)
            
            # 1b. Fallback: Google Translate jika kamus lokal tidak lengkap (masih ada huruf Latin)
            import re as _re
            has_latin = bool(_re.search(r'[a-zA-Z]', arabic_query))
            if has_latin:
                logger.info(f"[Playwright] Kamus lokal tidak lengkap: '{arabic_query}'. Mencoba Google Translate...")
                try:
                    import urllib.parse as _up
                    from bs4 import BeautifulSoup as _BS
                    gt_url = f"https://translate.google.com/m?sl=id&tl=ar&q={_up.quote(query)}"
                    import httpx as _hx
                    async with _hx.AsyncClient(timeout=8) as _c:
                        _r = await _c.get(gt_url, headers={"User-Agent": "Mozilla/5.0"})
                        if _r.status_code == 200:
                            _s = _BS(_r.text, 'html.parser')
                            _res = _s.find('div', class_='result-container')
                            if _res:
                                gt_result = _res.get_text(strip=True)
                                if is_arabic(gt_result) and len(gt_result) > 1:
                                    logger.info(f"[Playwright] Google Translate berhasil: '{gt_result}'")
                                    arabic_query = gt_result
                except Exception as _e:
                    logger.warning(f"[Playwright] Google Translate fallback gagal: {_e}")
            
            # 2. Redirect to direct Google CSE URL for instant results
            import urllib.parse
            encoded_query = urllib.parse.quote(arabic_query)
            # This is the direct Google-hosted CSE page for the Shamela CX (using &q= for auto-trigger)
            direct_url = f"https://cse.google.com/cse?cx=01a21494071be20f9&q={encoded_query}"
            
            logger.info(f"[Playwright] Navigating directly to CSE: {direct_url}")
            # Use 'domcontentloaded' as we only need the results to start appearing
            await self.page.goto(direct_url, wait_until="domcontentloaded", timeout=60000)
            
            # 3. Handle Pagination if page_num > 1
            if page_num > 1:
                logger.info(f"[Playwright] Navigating to page {page_num} in CSE...")
                try:
                    # Wait for results first
                    await self.page.wait_for_selector("a.gs-title", timeout=15000)
                    cursor_selector = f".gsc-cursor-page:has-text('{page_num}')"
                    cursor_btn = await self.page.wait_for_selector(cursor_selector, timeout=10000)
                    if cursor_btn:
                        await cursor_btn.click()
                        await self.page.wait_for_selector(f".gsc-cursor-current-page:has-text('{page_num}')", timeout=10000)
                except Exception as e:
                    logger.warning(f"[Playwright] Pagination failed: {e}")
                    # If pagination fails, we might still be on page 1, keep going or return []?
                    # Let's keep going with what's on screen.
            
            # 5. Wait for the popup results (general check)
            logger.info("[Playwright] Final wait for results...")
            try:
                await self.page.wait_for_selector("a.gs-title", timeout=20000)
            except Exception as e:
                # DEBUG: Save screenshot to see what happened
                from pathlib import Path
                debug_path = Path("debug_search_fail.png")
                await self.page.screenshot(path=str(debug_path))
                logger.warning(f"[Playwright] Result title not found. Screenshot saved to {debug_path.absolute()}")
                
                if await self.page.query_selector("div.gs-no-results-result"):
                    logger.info("[Playwright] No results found on Shamela.")
                    return []
                return []
            
            # 4. Scrape results
            results = []
            elements = await self.page.query_selector_all("div.gsc-webResult")
            
            for el in elements[:20]: # Increased to top 20 as requested
                title_el = await el.query_selector("a.gs-title")
                snippet_el = await el.query_selector("div.gs-snippet")
                
                if title_el:
                    title = await title_el.inner_text()
                    href = await title_el.get_attribute("href")
                    # Clean snippet
                    snippet = await snippet_el.inner_text() if snippet_el else ""
                    
                    if href and ("shamela.org/pdf/" in href or "shamela.ws/book/" in href or "shamela.org/book/" in href):
                        page_count = ""
                        file_size_raw = ""
                        
                        # Extract "Author: محمد آدم الإثيوبي"
                        penulis_arab = ""
                        a_match = re.search(r'Author:\s*([^.]+?)(?=\s*Pages:|\s*Size:|$)', snippet)
                        if a_match:
                            penulis_arab = a_match.group(1).strip()
                        elif "Author:" in snippet:
                            # Fallback if Pages/Size not present
                            parts = snippet.split("Author:")
                            if len(parts) > 1:
                                penulis_arab = parts[1].split(".")[0].split("Pages:")[0].strip()

                        # Extract "Pages: 236"
                        p_match = re.search(r'Pages:\s*(\d+)', snippet)
                        if p_match:
                            page_count = p_match.group(1)
                            
                        # Extract "Size: 1506921 bytes"
                        s_match = re.search(r'Size:\s*(\d+)\s*bytes', snippet)
                        if s_match:
                            size_bytes = int(s_match.group(1))
                            file_size_raw = f"{size_bytes / (1024*1024):.1f} MB"
                            
                        results.append({
                            "judul_arab": title,
                            "penulis_arab": penulis_arab,
                            "detail_url": href,
                            "snippet": snippet,
                            "page_count": page_count,
                            "file_size": file_size_raw
                        })
            
            logger.info(f"[Playwright] Scraped {len(results)} results.")
            return results
            
        except Exception as e:
            logger.error(f"[Playwright] Search major failure: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
        finally:
            await self.stop()

    async def resolve_pdf_link(self, detail_url: str):
        """
        Visits the shamela.org/pdf/{id} page and extracts the PDF download link.
        Now uses a HYBRID approach: Fast extraction first, fallback to Playwright only if needed.
        """
        # 1. FAST PATH: Attempt extraction using httpx (no browser)
        fast_url = await self.resolve_pdf_link_fast(detail_url)
        if fast_url:
            logger.info(f"[Scraper] Fast resolution success: {fast_url}")
            return fast_url

        # 2. FALLBACK: Playwright (Optimized to not wait for full render)
        await self.start()
        logger.info(f"[Playwright] Falling back to browser for: {detail_url}")
        
        try:
            # Use 'commit' or 'domcontentloaded' to avoid waiting for the heavy PDF render/download
            await self.page.goto(detail_url, wait_until="domcontentloaded", timeout=30000)
            
            # Try to extract from JS variable 'pdfUrl'
            try:
                pdf_url = await self.page.evaluate("() => typeof pdfUrl !== 'undefined' ? pdfUrl : null")
                if pdf_url:
                    if not pdf_url.startswith("http"):
                        pdf_url = "https://shamela.org" + (pdf_url if pdf_url.startswith("/") else f"/{pdf_url}")
                    return pdf_url
            except: pass

            # If still not found, wait a bit for the button and click
            pdf_button = await self.page.wait_for_selector('button:has-text("PDF")', timeout=10000)
            if pdf_button:
                async with self.page.expect_request(lambda request: ".pdf" in request.url.lower(), timeout=15000) as request_info:
                    await pdf_button.click()
                return request_info.value.url
            
        except Exception as e:
            logger.error(f"[Playwright] Link resolution fallback failure: {e}")
            # Final Hardcoded Fallback
            token = detail_url.rstrip('/').split('/')[-1]
            return f"https://shamela.org/gen/{token}_gen.pdf"
        finally:
            await self.stop()

    async def resolve_pdf_link_fast(self, detail_url: str) -> Optional[str]:
        """
        Attempts to extract the PDF link directly from the HTML source using httpx.
        Very fast, no browser overhead.
        """
        import httpx
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
            async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
                resp = await client.get(detail_url, headers=headers)
                if resp.status_code == 200:
                    html = resp.text
                    # Look for: var pdfUrl = '...'; or similar patterns
                    import re
                    # Pattern 1: JS variable
                    match = re.search(r'pdfUrl\s*=\s*[\'"]([^\'"]+)[\'"]', html)
                    if match:
                        url = match.group(1)
                        if not url.startswith("http"):
                            url = "https://shamela.org" + (url if url.startswith("/") else f"/{url}")
                        return url
                    
                    # Pattern 2: Download button href
                    # <a ... href="/gen/xxx_gen.pdf" ...>
                    match = re.search(r'href=[\'"]([^\'"]+\.pdf)[\'"]', html)
                    if match:
                        url = match.group(1)
                        if not url.startswith("http"):
                            url = "https://shamela.org" + (url if url.startswith("/") else f"/{url}")
                        return url
        except Exception as e:
            logger.warning(f"[Scraper] Fast extraction failed for {detail_url}: {e}")
        return None

if __name__ == "__main__":
    async def test():
        scraper = PlaywrightScraper(headless=False)
        res = await scraper.search_shamela("shahih muslim")
        for r in res:
            try:
                print(f"Found: {r['judul_arab']} -> {r['detail_url']}")
            except UnicodeEncodeError:
                print(f"Found: [Arabic Title] -> {r['detail_url']}")
            
    asyncio.run(test())
