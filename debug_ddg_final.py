import httpx
from bs4 import BeautifulSoup
import asyncio
import urllib.parse

async def search_ddg(keyword):
    # DDG HTML version (no JS required)
    url = "https://html.duckduckgo.com/html/"
    params = {"q": f"site:shamela.org/pdf {keyword}"}
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://duckduckgo.com/"
    }
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=20) as client:
        print(f"Searching DDG: {params['q']}")
        try:
            r = await client.get(url, params=params)
            print(f"Status: {r.status_code}")
            
            soup = BeautifulSoup(r.text, 'html.parser')
            
            results = []
            # DDG HTML results are usually in links with class 'result__a'
            for a in soup.select('a.result__a'):
                href = a.get('href', '')
                # DDG sometimes wraps links in /l/?kh=-1&uddg=URL
                if '/l/?' in href:
                    parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                    if 'uddg' in parsed:
                        href = parsed['uddg'][0]

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
            print(f"DDG Search error: {e}")
            return []

if __name__ == "__main__":
    asyncio.run(search_ddg("shahih bukhari"))
