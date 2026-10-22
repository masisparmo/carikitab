import asyncio
import sys
import os
import time
import logging

# Add project root to sys.path
sys.path.append(os.getcwd())

from app.services.gemini_search_assistant import GeminiSearchAssistant
from app.core.playwright_scraper import PlaywrightScraper
from app.main import SearchWorker

# Configure logging to console for the test
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TestV133")

async def test_full_workflow(keyword):
    print(f"\n🚀 MEMULAI SIMULASI FULL WORKFLOW v1.3.3")
    print(f"🔍 Kata Kunci: '{keyword}'\n" + "="*50)
    
    assistant = GeminiSearchAssistant()
    start_total = time.time()
    
    # 1. Normalisasi Kueri (Gemini)
    print("Step 1: Normalisasi & Deteksi Bahasa (Gemini)...")
    s1 = time.time()
    norm, err = await assistant.process_query(keyword)
    arabic_query = norm.get('arabic_title', keyword) if norm else keyword
    print(f"✅ Hasil: '{arabic_query}' ({time.time() - s1:.2f}s)")
    
    # 2. Pencarian (Direct CSE Playwright)
    print("\nStep 2: Pencarian Instan (Direct Google CSE)...")
    s2 = time.time()
    p_scraper = PlaywrightScraper()
    results = await p_scraper.search_shamela(arabic_query, page_num=1)
    print(f"✅ Hasil: Ditemukan {len(results)} kitab ({time.time() - s2:.2f}s)")
    
    if not results:
        print("❌ Tidak ada hasil, simulasi berhenti.")
        return

    # 3. Terjemahan Hasil & Metadata (Parallel)
    print("\nStep 3: Terjemahan Paralel & Metadata Enrichment (Top 5)...")
    s3 = time.time()
    # Simulate SearchWorker metadata enrichment (top 8 but we test top 5 for speed)
    async def fetch_meta(res):
        import httpx
        import re
        url = res.get('detail_url')
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    html = resp.text
                    p_match = re.search(r'Pages:\s*(\d+)', html)
                    res['page_count'] = p_match.group(1) if p_match else "?"
        except: pass
        return res

    # Parallel Translation
    task_translate = assistant.batch_translate_results(results[:5])
    # Parallel Metadata
    task_meta = asyncio.gather(*[fetch_meta(r) for r in results[:5]])
    
    enriched_results, _ = await asyncio.gather(task_translate, task_meta)
    print(f"✅ Hasil: {len(enriched_results)} kitab diperkaya ({time.time() - s3:.2f}s)")
    
    # Showcase results
    for i, r in enumerate(enriched_results[:3]):
        print(f"   [{i+1}] {r.get('judul_arab')} -> {r.get('judul_indonesia')} (Hal: {r.get('page_count', '?')})")

    # 4. Resolusi Link Download (Fast Path)
    print("\nStep 4: Persiapan Download Kilat (Fast Extraction)...")
    s4 = time.time()
    detail_url = enriched_results[0].get('detail_url')
    pdf_url = await p_scraper.resolve_pdf_link(detail_url)
    print(f"✅ Hasil Link: {pdf_url}")
    print(f"⚡ Waktu Download Resolution: {time.time() - s4:.2f}s")
    
    total_time = time.time() - start_total
    print("\n" + "="*50)
    print(f"🏁 SIMULASI SELESAI!")
    print(f"⏱️ Total Waktu Workflow: {total_time:.2f} detik")
    print("="*50)

if __name__ == "__main__":
    keyword = "tafsir ibnu katsir"
    asyncio.run(test_full_workflow(keyword))
