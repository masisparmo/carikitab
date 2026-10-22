import httpx
from bs4 import BeautifulSoup
import asyncio
import re

async def debug_redirect_follow():
    url = "https://www.google.com/search"
    query = "site:shamela.org/pdf shahih bukhari"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=20) as client:
        print(f"Step 1: Searching: {query}")
        params = {"q": query}
        r = await client.get(url, params=params)
        print(f"Status 1: {r.status_code}")
        
        soup = BeautifulSoup(r.text, 'html.parser')
        redirect_link = soup.find('a', href=re.compile(r'/search\?q=.*sei='))
        
        if redirect_link:
            href = redirect_link['href']
            print(f"Found redirect link: {href}")
            # Ensure internal link is absolute
            if href.startswith('/'):
                href = "https://www.google.com" + href
            
            print(f"Step 2: Following redirect...")
            r2 = await client.get(href)
            print(f"Status 2: {r2.status_code}")
            
            soup2 = BeautifulSoup(r2.text, 'html.parser')
            links = soup2.find_all('a', href=True)
            shamela_links = [a['href'] for a in links if "shamela.org/pdf" in a['href']]
            print(f"Found {len(shamela_links)} books after redirect.")
            for i, l in enumerate(shamela_links[:5]):
                print(f"Result {i+1}: {l}")
        else:
            print("No redirect link found.")

if __name__ == "__main__":
    asyncio.run(debug_redirect_follow())
