import httpx
from bs4 import BeautifulSoup
import asyncio

async def test_org():
    url = "https://shamela.org/src/api/pdfs.php?page=1"

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(url)
            print("Status", resp.status_code)
            print(resp.text[:500])
        except Exception as e:
            print("Error", e)

if __name__ == "__main__":
    asyncio.run(test_org())
