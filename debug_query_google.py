import httpx
from bs4 import BeautifulSoup
import asyncio
import re

async def debug_query_variation():
    url = "https://www.google.com/search"
    # Testing without 'site:' operator
    query = "shamela.org/pdf shahih bukhari"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=15) as client:
        params = {"q": query, "num": 10}
        r = await client.get(url, params=params)
        print(f"Status: {r.status_code}")
        
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Generic link extraction
        links = soup.find_all('a', href=True)
        results = [a['href'] for a in links if "shamela.org/pdf" in a['href']]
        print(f"Found {len(results)} shamela.org/pdf links.")
        for i, l in enumerate(results[:5]):
            print(f"{i+1}. {l}")

if __name__ == "__main__":
    asyncio.run(debug_query_variation())
