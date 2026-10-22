import httpx
from bs4 import BeautifulSoup
import asyncio
import urllib.parse
import re

async def search_google_human(keyword):
    # Mimic a real desktop/mobile browser to get the real results
    url = "https://www.google.com/search"
    params = {
        "q": f"site:shamela.org/pdf {keyword}",
        "hl": "id",
        "num": "10"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.google.com/",
        "Sec-Ch-Ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
    }
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=15) as client:
        print(f"Searching Google: {params['q']}")
        try:
            r = await client.get(url, params=params)
            print(f"Status: {r.status_code}")
            
            # Save for inspection
            with open("google_debug.html", "w", encoding="utf-8") as f:
                f.write(r.text)
            
            soup = BeautifulSoup(r.text, 'html.parser')
            results = []
            
            # Google's current main link selector is often div.g a or div.MjjYud a
            for a in soup.select('a[href*="shamela.org/pdf"]'):
                href = a.get('href', '')
                if '/url?q=' in href:
                    href = urllib.parse.parse_qs(urllib.parse.urlparse(href).query).get('q', [href])[0]
                
                # Title is usually in h3 or nearby text
                h3 = a.find('h3')
                title = h3.get_text() if h3 else a.get_text(strip=True)
                
                # Filter out garbage
                if "shamela.org/pdf" in href:
                    results.append({"title": title, "url": href})
            
            print(f"Found {len(results)} books.")
            for i, res in enumerate(results[:5]):
                print(f"{i+1}. {res['title']} -> {res['url']}")
            return results
        except Exception as e:
            print(f"Google Search error: {e}")
            return []

if __name__ == "__main__":
    asyncio.run(search_google_human("shahih bukhari"))
