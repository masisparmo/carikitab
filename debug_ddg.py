import httpx
from bs4 import BeautifulSoup
import re
import asyncio

async def debug_ddg():
    # DDG HTML version (no JS required)
    url = "https://html.duckduckgo.com/html/"
    query = "site:shamela.org/pdf shahih bukhari"
    params = {"q": query}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    }
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        r = await client.get(url, params=params)
        print(f"Status: {r.status_code}")
        
        with open("ddg_debug.html", "w", encoding="utf-8") as f:
            f.write(r.text)
            
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # DDG HTML uses specific classes like 'result__a'
        items = soup.select('a.result__a')
        print(f"DDG Links found: {len(items)}")
        for i, item in enumerate(items[:5]):
            print(f"Result {i}: {item.get_text()} | Link: {item['href']}")

if __name__ == "__main__":
    asyncio.run(debug_ddg())
