import sys
import os
import time
import logging
from PySide6.QtWidgets import QApplication
from app.main import MainWindow
from app.ui.components import ResultCard

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", stream=sys.stdout)

def run_realtime_test():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    # Paksa pancing Rate Limit API agar jatuh ke Lapis Fallback
    os.environ['GEMINI_API_KEYS'] = 'AIzaSy_FAKE_1,AIzaSy_FAKE_2'
    from app.services.gemini_search_assistant import global_rotator
    global_rotator.reload_keys()

    print("\n[ROBOT] 🚀 Membuka GUI Aplikasi secara Real-Time...")
    window = MainWindow()
    window.show()
    
    # Pilih tab Search
    window.tabs.setCurrentIndex(0)
    
    # --- PHASE 1: SEARCH ---
    search_term = "minhajul qosidin"
    print(f"[ROBOT] 🔍 Mengetik keyword: '{search_term}'")
    window.txt_search.setText(search_term)
    
    print("[ROBOT] 🖱️ Mengklik tombol Cari...")
    window.btn_search.click()
    
    print("[ROBOT] ⏳ Menunggu hasil pencarian. Perhatikan log proses Fallback lapis demi lapis...")
    
    timeout = 90
    start_time = time.time()
    
    # Tunggu sampai jumlah item di results_layout lebih dari 1 (1 itu stretch di akhir)
    # atau status bar berisi kata 'Selesai' atau 'Tidak ditemukan'
    while True:
        app.processEvents()
        status_text = window.statusBar().currentMessage()
        
        if window.results_layout.count() > 1:
            print("[ROBOT] ✅ Hasil pencarian mulai muncul di layar!")
            # Beri waktu UI untuk render semua card
            time.sleep(3)
            app.processEvents()
            break
            
        if "Selesai" in status_text or "Tidak ditemukan" in status_text or "Error" in status_text:
            if "Selesai" in status_text and window.results_layout.count() > 1:
                break
            elif "Tidak ditemukan" in status_text:
                print("[ROBOT] ❌ Pencarian gagal (0 kitab).")
                break
            
        if time.time() - start_time > timeout:
            print("[ROBOT] ⚠️ Timeout 90 detik tercapai!")
            break
            
        time.sleep(1)
        
    print(f"[ROBOT] ✅ UI menampilkan {max(0, window.results_layout.count() - 1)} kartu kitab.")
    
    # --- PHASE 2: SCREENSHOT ---
    print("[ROBOT] 📸 Mengambil screenshot hasil GUI...")
    app.processEvents()
    time.sleep(1)
    
    screenshot_path = os.path.join(os.getcwd(), "test_realtime_gui.png")
    window.grab().save(screenshot_path)
    print(f"[ROBOT] 📁 Screenshot disimpan: {screenshot_path}")
    
    # Tutup aplikasi otomatis
    print("[ROBOT] 🚪 Menutup aplikasi...")
    app.quit()

if __name__ == "__main__":
    run_realtime_test()
