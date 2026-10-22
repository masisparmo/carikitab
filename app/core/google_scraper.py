import logging
import httpx
import re
import urllib.parse
import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict
from app.services.gemini_search_assistant import GeminiSearchAssistant
from app.core.transliteration import transliterate_to_arabic
from app.core.playwright_scraper import PlaywrightScraper

logger = logging.getLogger(__name__)

class GoogleShamelaScraper:
    """
    Bridge that uses Gemini Search capabilities to find books at shamela.org/pdf.
    Includes a robust DuckDuckGo HTML fallback if Gemini is rate-limited.
    """
    
    def __init__(self, assistant=None):
        self.assistant = assistant or GeminiSearchAssistant()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

    async def _search_all_engines(self, query: str) -> List[Dict]:
        """
        Tries Google, then Bing, then DDG Lite.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://www.google.com/"
        }
        
        # Result accumulator
        winners = []
        
        # 1. Try Google (Mobile Mock)
        try:
            # User suggested: site:shamela.org/pdf + keyword in arabic
            url = "https://www.google.com/search"
            params = {"q": f'site:shamela.org {query}', "hl": "ar"}
            async with httpx.AsyncClient(headers=headers, timeout=10) as c:
                r = await c.get(url, params=params)
                if r.status_code == 200:
                    s = BeautifulSoup(r.text, 'html.parser')
                    for a in s.select('a[href*="shamela.org"]'):
                        href = a.get('href', '')
                        if "url?q=" in href: href = urllib.parse.parse_qs(urllib.parse.urlparse(href).query).get('q', [href])[0]
                        if "shamela.org/pdf" in href or "shamela.org/book" in href or "shamela.ws/book" in href:
                            winners.append({"title": a.get_text(strip=True) or "Kitab", "url": href, "source": "google"})
                if winners: return winners
        except: pass

        # 2. Try Bing
        try:
            url = "https://www.bing.com/search"
            params = {"q": f'site:shamela.org {query}'}
            async with httpx.AsyncClient(headers=headers, timeout=10) as c:
                r = await c.get(url, params=params)
                if r.status_code == 200:
                    s = BeautifulSoup(r.text, 'html.parser')
                    for h2 in s.select('li.b_algo h2'):
                        a = h2.find('a')
                        if a:
                            href = a.get('href', '')
                            if "shamela.org/pdf" in href or "shamela.org/book" in href or "shamela.ws/book" in href:
                                winners.append({"title": a.get_text(strip=True), "url": href, "source": "bing"})
                if winners: return winners
        except: pass

        # 3. Try DDG Lite (Ultima Fallback)
        try:
            url = "https://duckduckgo.com/lite/"
            data = {"q": f'site:shamela.org {query}'}
            async with httpx.AsyncClient(headers=headers, timeout=10) as c:
                r = await c.post(url, data=data)
                if r.status_code == 200:
                    s = BeautifulSoup(r.text, 'html.parser')
                    for a in s.select('a.result-link'):
                        href = a.get('href', '')
                        if "shamela.org/pdf" in href or "shamela.org/book" in href or "shamela.ws/book" in href:
                            winners.append({"title": a.get_text(strip=True), "url": href, "source": "ddg"})
        except: pass

        return winners

    async def search(self, query: str, page_num: int = 1) -> List[Dict]:
        """
        Unified search for shamela.org/pdf using multiple engines.
        Prioritizes Playwright for exact mimicry.
        """
        logger.info(f"[SearchBridge] Brute-forcing: {query}")
        
        final_results = []
        
        # 0. Prep query
        arabic_query = query
        try:
            norm, _ = await self.assistant.process_query(query)
            if norm and norm.get('arabic_title'):
                arabic_query = norm.get('arabic_title')
        except: pass

        # 1. Try Playwright Scraper
        try:
            p_scraper = PlaywrightScraper()
            p_results = await p_scraper.search_shamela(query, page_num=page_num)
            logger.info(f"[SearchBridge] Playwright returned {len(p_results)} results for page {page_num}.")
            if p_results:
                final_results.extend(p_results)
        except Exception as e:
            logger.error(f"[Playwright] Scraper failed internally: {e}")

        # 2. Search Engines Fallback (only on first page for now to save time)
        if not final_results and page_num == 1:
            for q in [arabic_query, query]:
                if not final_results:
                    final_results.extend(await self._search_all_engines(q))
                    if final_results: break

        # Filter hallucinations (No 10001, must be long)
        def is_valid(url):
            book_id = url.rstrip('/').split('/')[-1]
            return len(book_id) >= 2 and book_id != "10001" and re.match(r'^[a-fA-F0-9_]+$', book_id)
            
        # 3. Final cleanup and key harmonization
        valid_filtered = []
        for r in final_results:
            u = r.get('url') or r.get('detail_url', '')
            t = r.get('title') or r.get('judul_arab', '')
            
            if is_valid(u):
                # Ensure BOTH keys exist for compatibility with other modules
                r['url'] = u
                r['detail_url'] = u
                r['title'] = t
                r['judul_arab'] = t
                
                # Metadata persistence
                if 'page_count' not in r: r['page_count'] = ""
                if 'file_size' not in r: r['file_size'] = ""
                
                valid_filtered.append(r)
        
        return valid_filtered

    async def close(self):
        pass
