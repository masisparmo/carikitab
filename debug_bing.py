import httpx
from bs4 import BeautifulSoup
import asyncio
import urllib.parse

async def search_bing(keyword):
    # Bing HTML version (less bot detection)
    url = "https://www.bing.com/search"
    # Use site:domain + literal path string for better coverage
    params = {"q": f'site:shamela.org "shamela.org/pdf" {keyword}'}
    
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.bing.com/"
    }
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=20) as client:
        print(f"Searching Bing: {params['q']}")
        try:
            r = await client.get(url, params=params)
            print(f"Status: {r.status_code}")
            
            soup = BeautifulSoup(r.text, 'html.parser')
            results = []
            
            # Bing results are usually in <h2> <a href="...">
            for h2 in soup.select('li.b_algo h2'):
                a = h2.find('a')
                if not a: continue
                href = a.get('href', '')
                
                if "shamela.org/pdf" in href:
                    results.append({
                        "title": a.get_text(strip=True),
                        "url": href
                    })
            
            print(f"Found {len(results)} books.")
            for i, res in enumerate(results[:5]):
                print(f"{i+1}. {res['title']} -> {res['url']}")
            return results
        except Exception as e:
            print(f"Bing Search error: {e}")
            return []

if __name__ == "__main__":
    asyncio.run(search_bing("shahih bukhari"))
