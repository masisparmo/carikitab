import httpx
from bs4 import BeautifulSoup
import re
import asyncio

async def debug_search():
    url = "https://www.google.com/search"
    # Added gbv=1 to get non-JS version
    query = "site:shamela.org/pdf shahih bukhari"
    params = {"q": query, "num": 10, "gbv": "1"}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,ar;q=0.8"
    }
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        r = await client.get(url, params=params)
        print(f"Status: {r.status_code}")
        
        with open("google_debug_legacy.html", "w", encoding="utf-8") as f:
            f.write(r.text)
            
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Test legacy selectors (usually div.g or div.kCrYT)
        items = soup.select('div.g')
        print(f"Selector 'div.g' count: {len(items)}")
        
        items_v3 = soup.select('div.kCrYT')
        print(f"Selector 'div.kCrYT' (legacy) count: {len(items_v3)}")
        
        all_links = soup.find_all('a', href=True)
        shamela_links = [l['href'] for l in all_links if 'shamela.org' in l['href']]
        print(f"Shamela links found: {len(shamela_links)}")
        for l in shamela_links[:5]:
            print(f"  - {l}")

if __name__ == "__main__":
    asyncio.run(debug_search())
