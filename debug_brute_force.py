import httpx
from bs4 import BeautifulSoup
import asyncio
import re

async def debug_brute_force_google():
    url = "https://www.google.com/search"
    query = "site:shamela.org/pdf shahih bukhari"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=20) as client:
        # Step 1: Initial request
        params = {"q": query}
        r = await client.get(url, params=params)
        
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Step 2: Handle redirect link if present
        redirect_link = soup.find('a', href=re.compile(r'/search\?q=.*sei='))
        if redirect_link:
            href = redirect_link['href']
            if href.startswith('/'): href = "https://www.google.com" + href
            r = await client.get(href)
            soup = BeautifulSoup(r.text, 'html.parser')

        # Step 3: BRUTE FORCE - Scan ALL anchors
        all_links = soup.find_all('a', href=True)
        results = []
        for a in all_links:
            href = a['href']
            # Unmask /url?q=...
            if "/url?q=" in href:
                match = re.search(r'q=(https?://[^&]+)', href)
                if match: href = match.group(1)

            if "shamela.org/pdf" in href:
                # Find title: first non-empty text in <a> or closest <h3>/<span>
                title = a.get_text(strip=True)
                if not title or len(title) < 3:
                    # Look at parent containers for text
                    parent = a.find_parent(['div', 'span'])
                    if parent: title = parent.get_text(strip=True).split('http')[0][:100]
                
                if href not in [res['url'] for res in results]:
                    results.append({"title": title, "url": href})

        print(f"Brute Force found {len(results)} shamela.org/pdf links.")
        for i, res in enumerate(results[:5]):
            print(f"{i+1}. {res['title']} -> {res['url']}")

if __name__ == "__main__":
    asyncio.run(debug_brute_force_google())
