import sys
import os
import time
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, Qt
from app.main import MainWindow
from app.ui.components import ResultCard

# Setup logging to stdout so user can see it
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", stream=sys.stdout)
logger = logging.getLogger("RobotTest")

def run_automated_test():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    print("\n[ROBOT] 🚀 Memulai Pengujian Real-Time...")
    print("[ROBOT] 🖥️ Menginisialisasi MainWindow...")
    window = MainWindow()
    window.show()
    
    # --- PHASE 1: SEARCH ---
    search_term = "ibnu jauzy"
    print(f"[ROBOT] 🔍 Mencari keyword: '{search_term}'")
    window.txt_search.setText(search_term)
    window.btn_search.click()
    
    print("[ROBOT] ⏳ Menunggu hasil pencarian (max 45s)...")
    timeout = 45
    start_time = time.time()
    while window.results_layout.count() <= 1:
        app.processEvents()
        if time.time() - start_time > timeout:
            print("[ROBOT] ❌ Timeout saat mencari!")
            app.quit()
            return
        time.sleep(0.5)
        
    print(f"[ROBOT] ✅ Ditemukan {window.results_layout.count() - 1} hasil.")
    
    # --- PHASE 2: TANYA AI ---
    first_card = None
    for i in range(window.results_layout.count()):
        widget = window.results_layout.itemAt(i).widget()
        if isinstance(widget, ResultCard):
            first_card = widget
            break
            
    if not first_card:
        print("[ROBOT] ❌ Tidak ada ResultCard yang ditemukan!")
        app.quit()
        return

    judul = first_card.book_data.get('judul_arab') or first_card.book_data.get('title') or "Kitab"
    print(f"[ROBOT] 🤖 Memicu 'Tanya AI' untuk: {judul}")
    # Trigger AI query
    first_card.ai_query_requested.emit(first_card.book_data)
    
    # --- PHASE 3: WAIT FOR AI ---
    print("[ROBOT] ⏳ Menunggu respon AI (Proses rotasi 16 key + fallback)...")
    print("[ROBOT] 📝 Pantau log di bawah ini:")
    
    timeout_ai = 180 # 3 menit
    start_time_ai = time.time()
    last_content = ""
    
    while True:
        app.processEvents()
        content = window.chat_display.toPlainText()
        
        if content != last_content:
            # Print new lines appearing in chat_display as simulation of log monitoring
            new_text = content[len(last_content):].strip()
            if new_text:
                print(f"[ROBOT-UI] {new_text}")
            last_content = content

        # Check for success markers from v1.5.9 prompt
        if "METADATA DOKUMEN" in content and "RESUME" in content:
            if len(content) > 1000: # Sufficiently long
                print("[ROBOT] ✅ Respon AI berhasil diterima dengan format lengkap!")
                break
                
        # Check for failure
        if "Gagal memproses AI bahkan setelah rotasi" in content:
            print("[ROBOT] ❌ AI Gagal Total setelah rotasi 16 key & Fallback.")
            break
        
        if time.time() - start_time_ai > timeout_ai:
            print("[ROBOT] ⚠️ Timeout menunggu AI (3 menit terlampaui).")
            break
        
        time.sleep(1)

    # --- PHASE 4: SCREENSHOT ---
    print("[ROBOT] 📸 Mengambil screenshot hasil...")
    app.processEvents()
    time.sleep(2)
    
    screenshot_path = os.path.join(os.getcwd(), "test_realtime_output.png")
    # Grab the whole window for context
    window.grab().save(screenshot_path)
    print(f"[ROBOT] 📁 Screenshot disimpan: {screenshot_path}")
    
    # Final Result Report
    if "METADATA DOKUMEN" in content:
        print("\n[RESULT] BERHASIL: Sistem rotasi dan format output berfungsi.")
    else:
        print("\n[RESULT] GAGAL: AI tidak memberikan output yang diharapkan.")

    app.quit()

if __name__ == "__main__":
    run_automated_test()
