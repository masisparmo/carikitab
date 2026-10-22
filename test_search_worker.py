import asyncio
import sys
import os
import logging

from PySide6.QtWidgets import QApplication
from app.main import SearchWorker

# Enable logging to terminal for visibility
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(levelname)s - %(message)s")

def on_status_update(msg):
    print(f">> STATUS : {msg}")

def on_results_found(results):
    print(f"\n>> MENDAPATKAN {len(results)} HASIL:")
    for i, r in enumerate(results, 1):
        print(f"{i}. Judul Arab      : {r.get('judul_arab')}")
        print(f"   Judul Indonesia : {r.get('judul_indonesia', '-')}")
        print(f"   URL             : {r.get('detail_url', '-')}")

def on_error(msg):
    print(f"\n!! ERROR: {msg}")

def test_search():
    # Ciptakan QApplication mock agar QThread (SearchWorker) bisa berjalan
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    print("=== MEMULAI SIMULASI PENCARIAN 'minhajul qosidin' ===")
    
    # Paksa penggunaan API sembarang agar hit 429 berulang kali (simulasi app down)
    os.environ['GEMINI_API_KEYS'] = 'AIzaSy_FAKE_1,AIzaSy_FAKE_2'
    from app.services.gemini_search_assistant import global_rotator
    global_rotator.reload_keys()

    worker = SearchWorker(keyword="minhajul qosidin", use_llm=True, page_num=1, source="Shamela")
    
    # Sambungkan signals
    worker.status_update.connect(on_status_update)
    worker.results_found.connect(on_results_found)
    worker.error.connect(on_error)
    
    # Supaya loop event Qt menunggu worker selesai
    finished_loop = asyncio.new_event_loop()
    
    def on_finished():
        print("=== PROSES PENCARIAN SELESAI ===")
        app.quit()
        
    worker.finished.connect(on_finished)
    worker.start()
    
    app.exec() # Tahan thread hingga app.quit() dipanggil

if __name__ == "__main__":
    test_search()
