import httpx
from bs4 import BeautifulSoup
import asyncio
from typing import List, Dict, Optional
import urllib.parse
from app.core.transliteration import transliterate_to_arabic
from app.core.playwright_scraper import PlaywrightScraper

class ShamelaScraper:
    BASE_URL = "https://shamela.ws"
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://shamela.ws/search"
        }
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True, headers=self.headers)

    async def search_books(self, keyword_indo: str, search_by: str = "Tittle", page: int = 1) -> List[Dict]:
        """
        Search books on shamela.ws using their AJAX API.
        Normally, keyword_indo will be transliterated to Arabic.
        """
        keyword_arab = transliterate_to_arabic(keyword_indo)
        url = f"{self.BASE_URL}/ajax/search"
        data = {
            "term": keyword_arab,
            "page": str(page),
            "aqsam": "-1",
            "authors": "-1",
            "books": "-1",
            "decades": "-1"
        }
        
        try:
            # We use POST for their ajax search API
            response = await self.client.post(url, data=data)
            response.raise_for_status()
        except Exception as e:
            print(f"Error fetching search results: {e}")
            return []
            
        soup = BeautifulSoup(response.text, 'lxml')
        results = []
        
        # In the parsed result, there are multiple a tags
        # Format is roughly: 
        # <a href="https://shamela.ws/book/3901/4257" class="...">
        # Title [Author]
        # </a>
        
        links = soup.select("a.list-group-item")
        if not links:
            # Maybe the structure is different, let's just grab any book link
            links = [a for a in soup.select("a[href]") if "/book/" in a.get('href', '') and not a.get("href", "").endswith("/download")]
            
        seen_books = set()
        
        for a_tag in links:
            href = a_tag.get("href", "")
            # We only want the main book ID, e.g. /book/3901
            # But the search usually returns /book/3901/4257 (page level)
            # Let's clean the href to just /book/ID
            parts = href.split('/')
            book_id = None
            if "book" in parts:
                idx = parts.index("book")
                if len(parts) > idx + 1:
                    book_id = parts[idx+1]
            
            if not book_id:
                continue
                
            book_url = f"{self.BASE_URL}/book/{book_id}"
            if book_url in seen_books:
                continue
                
            seen_books.add(book_url)
            
            text_content = a_tag.get_text(strip=True)
            # Typically "Title [Author]"
            title_arab = text_content
            author_arab = "Unknown"
            
            if "[" in text_content and "]" in text_content:
                title_arab = text_content[:text_content.rfind("[")].strip()
                author_arab = text_content[text_content.rfind("[")+1:text_content.rfind("]")].strip()
            
            if not title_arab:
                continue
                
            results.append({
                'judul_indonesia': "", 
                'judul_arab': title_arab,
                'penulis_indonesia': "", 
                'penulis_arab': author_arab,
                'detail_url': book_url
            })
            
        return results

    async def get_pdf_link(self, detail_url: str) -> Optional[str]:
        """
        Resolves the direct download link. 
        Supports both shamela.ws (legacy) and shamela.org/pdf (new).
        """
        # 1. Handle shamela.org/pdf (The new PDF site)
        if "shamela.org/pdf/" in detail_url:
            try:
                p_scraper = PlaywrightScraper()
                return await p_scraper.resolve_pdf_link(detail_url)
            except Exception as e:
                print(f"Playwright resolution failed, falling back: {e}")
                book_id = detail_url.rstrip('/').split('/')[-1]
                return f"https://shamela.org/gen/{book_id}_gen.pdf"

        # 2. Handle shamela.ws (Legacy site)
        try:
            response = await self.client.get(detail_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                # Prioritize PDF links over BOK
                for a in soup.select("a[href]"):
                    href = a.get('href', '').lower()
                    if '.pdf' in href:
                        return f"{self.BASE_URL}{href}" if href.startswith('/') else a.get('href')
                
                # Check for any "Download" text if PDF extension isn't found
                for a in soup.select("a[href]"):
                    if 'pdf' in a.text.lower() or 'تحميل' in a.text.lower():
                        href = a.get('href')
                        return f"{self.BASE_URL}{href}" if href.startswith('/') else href
                        
        except Exception as e:
            print(f"Error fetching detail page pdf: {e}")
            
        # Fallback for shamela.ws
        if "shamela.ws" in detail_url:
            book_id = detail_url.rstrip('/').split('/')[-1]
            return f"{self.BASE_URL}/rep.php/book/download/{book_id}"
        
        return detail_url # Return original if all else fails

    async def close(self):
        await self.client.aclose()

# Test block
if __name__ == "__main__":
    async def test():
        scraper = ShamelaScraper()
        results = await scraper.search_books("bukhari")
        for r in results[:3]:
            print("Found:", r['judul_arab'], "by", r['penulis_arab'])
            pdf = await scraper.get_pdf_link(r['detail_url'])
            print("Download Link:", pdf)
        await scraper.close()
    
    asyncio.run(test())
