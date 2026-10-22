import logging
import asyncio
import re
from typing import List, Dict
from playwright.async_api import async_playwright
import playwright_stealth

logger = logging.getLogger(__name__)

class GoogleGlobalScraper:
    """
    Scraper for the Custom Google CSE (Archive.org, Drive, etc.)
    CX: 02e132f881e8f475c
    """
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
        self.cse_url = "https://cse.google.com/cse?cx=02e132f881e8f475c"

    async def _init_browser(self):
        if not self.browser:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
            self.context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            )
            self.page = await self.context.new_page()
            
            # Apply stealth robustly
            try:
                f = playwright_stealth.stealth
                if not callable(f) and hasattr(f, 'stealth'): f = f.stealth
                if callable(f):
                    if asyncio.iscoroutinefunction(f): await f(self.page)
                    else: f(self.page)
            except Exception as e:
                logger.warning(f"[GlobalScraper] Stealth failure: {e}")

    async def search(self, keyword: str, page_num: int = 1) -> List[Dict]:
        await self._init_browser()
        
        try:
            logger.info(f"[GlobalScraper] Searching for: {keyword} (Page {page_num})")
            await self.page.goto(self.cse_url, wait_until="networkidle", timeout=60000)
            
            # 1. Type keyword
            await self.page.wait_for_selector("input.gsc-input", timeout=20000)
            await self.page.fill("input.gsc-input", keyword)
            await self.page.press("input.gsc-input", "Enter")
            
            # 2. Wait for results
            await self.page.wait_for_selector("div.gsc-webResult", timeout=20000)
            
            # 3. Handle Pagination if page_num > 1
            if page_num > 1:
                logger.info(f"[GlobalScraper] Navigating to page {page_num}...")
                page_selector = f'div.gsc-cursor-page:has-text("{page_num}")'
                pagination_exists = await self.page.query_selector(page_selector)
                
                if pagination_exists:
                    await pagination_exists.click()
                    # Wait for results to refresh
                    await asyncio.sleep(2)
                    await self.page.wait_for_selector("div.gsc-webResult", timeout=20000)
                else:
                    logger.warning(f"[GlobalScraper] Page {page_num} not found in pagination.")
                    return []

            # 4. Scrape results
            results = []
            elements = await self.page.query_selector_all("div.gsc-webResult")
            
            for el in elements:
                title_el = await el.query_selector("a.gs-title")
                snippet_el = await el.query_selector("div.gs-snippet")
                
                if title_el:
                    title = await title_el.inner_text()
                    href = await title_el.get_attribute("href")
                    snippet = await snippet_el.inner_text() if snippet_el else ""
                    
                    if href:
                        # Shared metadata extraction
                        page_count = ""
                        file_size_raw = ""
                        
                        # Extract "Author: ..."
                        penulis_arab = ""
                        a_match = re.search(r'Author:\s*([^.]+?)(?=\s*Pages:|\s*Size:|$)', snippet)
                        if a_match:
                            penulis_arab = a_match.group(1).strip()
                        elif "Author:" in snippet:
                            parts = snippet.split("Author:")
                            if len(parts) > 1:
                                penulis_arab = parts[1].split(".")[0].split("Pages:")[0].strip()

                        p_match = re.search(r'Pages:\s*(\d+)', snippet)
                        if p_match: page_count = p_match.group(1)
                            
                        s_match = re.search(r'Size:\s*(\d+)\s*bytes', snippet)
                        if s_match:
                            size_bytes = int(s_match.group(1))
                            file_size_raw = f"{size_bytes / (1024*1024):.1f} MB"
                            
                        results.append({
                            "judul_arab": title,
                            "penulis_arab": penulis_arab,
                            "detail_url": href,
                            "url": href,
                            "snippet": snippet,
                            "page_count": page_count,
                            "file_size": file_size_raw,
                            "source": "global-cse"
                        })
            
            return results
        except Exception as e:
            logger.error(f"[GlobalScraper] Error: {e}")
            return []

    async def close(self):
        if self.browser:
            await self.browser.close()
