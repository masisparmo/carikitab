import asyncio
import sys
import os

# Add project root to sys.path
sys.path.append(os.getcwd())

from app.core.playwright_scraper import PlaywrightScraper

async def test():
    scraper = PlaywrightScraper()
    url = "https://shamela.org/pdf/633ce60c8cbe7_39e211e21a49f4d009bd322cfcf47794"
    print(f"Testing fast resolution for: {url}")
    
    import time
    start = time.time()
    pdf_url = await scraper.resolve_pdf_link(url)
    end = time.time()
    
    print(f"Result: {pdf_url}")
    print(f"Time Taken: {end - start:.2f} seconds")
    
    if pdf_url and "shamela.org" in pdf_url and ".pdf" in pdf_url:
        print("VERIFICATION SUCCESSFUL: Link resolved quickly!")
    else:
        print("VERIFICATION FAILED: Link not resolved correctly.")

if __name__ == "__main__":
    asyncio.run(test())
