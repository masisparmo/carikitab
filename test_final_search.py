import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from app.services.gemini_search_assistant import GeminiSearchAssistant
from app.core.google_scraper import GoogleShamelaScraper

async def test_integration():
    print("Initializing components...")
    assistant = GeminiSearchAssistant()
    scraper = GoogleShamelaScraper(assistant=assistant)
    
    keyword = "shahih bukhari"
    print(f"Testing Smart Search for: '{keyword}'")
    
    results = await scraper.search(keyword)
    
    print(f"Results found: {len(results)}")
    for i, res in enumerate(results[:5]):
        print(f"{i+1}. {res['judul_arab']} ({res['judul_indonesia']})")
        print(f"   URL: {res['detail_url']}")
        print("-" * 30)

if __name__ == "__main__":
    asyncio.run(test_integration())
