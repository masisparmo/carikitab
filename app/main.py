import sys
import os
import httpx
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLineEdit, QComboBox, QPushButton, 
                               QTabWidget, QScrollArea, QLabel, QFrame, QMessageBox,
                               QProgressBar,
                               QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
                               QCheckBox, QDialog, QTextEdit, QRadioButton, QSpinBox, QSplitter,
                               QInputDialog, QTextBrowser, QListWidget, QListWidgetItem)
from PySide6.QtWidgets import QFileDialog
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, QThread, Signal, Slot, QTimer
import uuid
import logging
import json
from datetime import datetime
from app.core.utils import get_data_dir, get_writable_path, get_downloads_dir
from app.assets.help_content import HELP_HTML

# ==== Viewer Module Imports ====
from PySide6.QtCore import QUrl
try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False
    logging.warning("PySide6.QtWebEngineWidgets is missing. PDF Viewer will be limited.")

try:
    import ebooklib
    from ebooklib import epub
    from bs4 import BeautifulSoup
    HAS_EBOOKLIB = True
except ImportError:
    HAS_EBOOKLIB = False
    logging.warning("ebooklib or bs4 is missing. EPUB Viewer will be disabled.")
APP_VERSION = "1.6.5"

UI_STRINGS = {
    'id': {
        'tab_search': '🔍 Cari',
        'tab_split': '✂️ Alat Potong',
        'tab_ai': '🤖 AI Konsultan',
        'tab_viewer': '📖 Viewer',
        'tab_history': '📑 Riwayat',
        'viewer_empty': 'Silakan pilih file dari tab Riwayat atau tekan Buka untuk membaca file.',
        'viewer_open_btn': '📂 Buka Manual',
        'viewer_no_webengine': 'Perhatian: Komponen penampil PDF tidak tersedia. Membuka di aplikasi eksternal.',
        'tab_setting': '⚙️ Pengaturan',
        'tab_help': '❓ Bantuan',
        'tab_about': 'ℹ️ Tentang',
        'setting_theme': 'Tema Aplikasi',
        'setting_lang': 'Bahasa Aplikasi',
        'setting_api_title': 'Gemini API Keys',
        'setting_api_desc': "Digunakan untuk 'Smart Arabic Search' dan AI Konsultan. Gunakan koma (,) untuk memisahkan beberapa key.",
        'btn_save_settings': '💾 Simpan Semua Pengaturan',
        'btn_search': 'Cari',
        'search_placeholder': 'Ketik judul kitab atau nama penulis dalam Indonesia/Arab...',
        'chk_smart_search': 'Aktifkan Smart Arabic Search',
        'chk_fast_mode': 'Mode Cepat (Tanpa Transliterasi)',
        'status_ready': 'Siap.',
        'active_downloads': 'Unduhan Aktif',
        'ai_welcome_title': '🤖 Selamat Datang di AI Konsultan Kitab!',
        'ai_welcome_desc': 'Saya adalah asisten bertenaga Gemini yang siap membantu Anda menemukan informasi tentang kitab-kitab Islam klasik...',
        'ai_welcome_tips': 'Tips: Klik pada judul atau penulis yang disarankan untuk mencari file kitab tersebut secara otomatis.',
        'ai_new_chat': '➕ Percakapan Baru',
        'ai_history': '<b>Riwayat Obrolan:</b>',
        'ai_input_placeholder': 'Tanyakan sesuatu tentang kitab atau buku...',
        'ai_send': '🚀 Kirim',
        'history_refresh': '🔄 Segarkan',
        'history_open_folder': '📂 Buka Folder Unduhan',
        'history_cols': ["Judul", "Penulis", "Waktu", "Status", "Lokasi"],
        'archive_dialog_title': 'Unduh dari Archive.org',
        'archive_mode_pdf': '⬇️ PDF (Scan)',
        'archive_mode_pdf_text': '📝 PDF Teks',
        'archive_mode_fulltext': '📄 Full Text (TXT)',
        'archive_select_all': '✅ Pilih Semua',
        'archive_clear_all': '❌ Hapus Pilihan',
        'archive_btn_download': '⬇️ Unduh yang Dipilih',
        'header_lang_id': '🇮🇩 ID',
        'header_lang_en': '🇬🇧 EN',
        'header_theme_dark': '🌙 Gelap',
        'header_theme_light': '☀️ Terang',
        'setting_dl_folder': 'Folder Simpan PDF',
        'setting_dl_desc': 'Folder tempat menyimpan file kitab yang didownload.',
        'setting_dl_placeholder': 'Klik Browse untuk pilih folder...',
        'setting_browse': '📁 Browse',
        'setting_keys_placeholder': 'Paste API Keys di sini (pisahkan dengan koma)...',
        'setting_repair_title': 'Driver Pencarian (Playwright)',
        'setting_repair_desc': 'Jika pencarian tidak bekerja atau error, silakan klik tombol di bawah untuk mengunduh driver.',
        'setting_repair_btn': '🛠️ Perbaiki / Install Driver Pencarian',
        'help_html': HELP_HTML,
        'about_html': """
        <div style="font-family: sans-serif; line-height: 1.6; color: #212529;">
        <h2>📖 Apa itu Cari Kitab?</h2>
        <p><b>Cari Kitab</b> adalah aplikasi desktop modern yang dirancang untuk memudahkan para peneliti, santri, 
        mahasiswa, dan pecinta ilmu dalam mencari, mendownload, dan mengelola koleksi kitab Islam klasik maupun buku umum 
        secara digital dari berbagai sumber terpercaya.</p>
        <h2 style="color: #198754;">✨ Fitur Utama (v1.6.0)</h2>
        <ul>
            <li><b>AI Fallback Stability:</b> Mekanisme cerdas 3 lapis (Gemini Web, Brave AI, Google AI) demi menjamin ketersediaan jawaban meskipun API sedang limit.</li>
            <li><b>Smart Arabic Search:</b> Pencarian cerdas menggunakan Artificial Intelligence untuk menangani variasi judul kitab dalam bahasa Arab secara akurat.</li>
            <li><b>PDF Splitter Pro:</b> Alat bawaan untuk memotong file PDF besar berdasarkan halaman atau ukuran (MB).</li>
            <li><b>AI Konsultan Kitab:</b> Tanya jawab langsung seputar isi kitab dan referensi literatur Islam dengan dukungan Computer Vision (analisis 10 halaman pertama).</li>
        </ul>
        <h2 style="color: #6f42c1;">🆕 Update v1.6.0</h2>
        <ul>
            <li><b>Zoom & Scaling:</b> Penambahan fitur perbesaran/pengecilan huruf (Font Zoom) di area jawaban AI Konsultan.</li>
            <li><b>Rename UI Improvement:</b> Dialog penggantian nama file kini lebih lebar dan adaptif terhadap panjang nama file.</li>
            <li><b>Cleaner UI:</b> Pembersihan tag HTML pada riwayat obrolan agar tampilan lebih profesional.</li>
            <li><b>Fallback Optimization:</b> Prioritas fallback ditata ulang (Gemini Web menjadi Prioritas 1) untuk jawaban yang lebih panjang dan detail.</li>
        </ul>
        <h2 style="color: #dc3545;">👤 Informasi Developer</h2>
        <p>Aplikasi ini dikembangkan oleh <b>Isparmo</b> (@vibe-coding) untuk mendukung kemudahan akses terhadap literatur keislaman.</p>
        <p>
            <b>🌐 Website:</b> <a href="https://page.isparmo.com" style="color: #0d6efd; text-decoration: none;">https://page.isparmo.com</a><br>
            <b>📧 Email:</b> <a href="mailto:mail@isparmo.com" style="color: #0d6efd; text-decoration: none;">mail@isparmo.com</a><br>
            <b>💬 WhatsApp:</b> <a href="https://wa.me/628121083060" style="color: #0d6efd; text-decoration: none;">08121083060</a>
        </p>
        <hr style="border: 0; border-top: 1px solid #dee2e6; margin: 20px 0;">
        <p style="text-align: center; color: #6c757d; font-size: 11px;">© 2024-2025 Cari Kitab • Build with ❤️ for Ummah</p>
        </div>
        """
    },
    'en': {
        'tab_search': '🔍 Search',
        'tab_split': '✂️ Split Tool',
        'tab_ai': '🤖 AI Consultant',
        'tab_viewer': '📖 Viewer',
        'tab_history': '📑 History',
        'viewer_empty': 'Please select a file from History tab or click Open to read.',
        'viewer_open_btn': '📂 Open File',
        'viewer_no_webengine': 'Warning: PDF Viewer component is unavailable. Opening in external application.',
        'tab_setting': '⚙️ Settings',
        'tab_help': '❓ Help',
        'tab_about': 'ℹ️ About',
        'setting_theme': 'App Theme',
        'setting_lang': 'App Language',
        'setting_api_title': 'Gemini API Keys',
        'setting_api_desc': "Used for 'Smart Arabic Search' and AI Consultant. Use commas (,) to separate multiple keys.",
        'btn_save_settings': '💾 Save All Settings',
        'btn_search': 'Search',
        'search_placeholder': 'Type book title or author name in English/Arabic...',
        'chk_smart_search': 'Enable Smart Arabic Search',
        'chk_fast_mode': 'Fast Mode (No Transliteration)',
        'status_ready': 'Ready.',
        'active_downloads': 'Active Downloads',
        'ai_welcome_title': '🤖 Welcome to AI Book Consultant!',
        'ai_welcome_desc': 'I am a Gemini-powered assistant ready to help you find information about classical Islamic books...',
        'ai_welcome_tips': 'Tips: Click on suggested titles or authors to search for those books automatically.',
        'ai_new_chat': '➕ New Conversation',
        'ai_history': '<b>Chat History:</b>',
        'ai_input_placeholder': 'Ask something about books or authors...',
        'ai_send': '🚀 Send',
        'history_refresh': '🔄 Refresh',
        'history_open_folder': '📂 Open Download Folder',
        'history_cols': ["Title", "Author", "Time", "Status", "Location"],
        'archive_dialog_title': 'Download from Archive.org',
        'archive_mode_pdf': '⬇️ PDF (Scan)',
        'archive_mode_pdf_text': '📝 PDF With Text',
        'archive_mode_fulltext': '📄 Full Text (TXT)',
        'archive_select_all': '✅ Select All',
        'archive_clear_all': '❌ Clear Selection',
        'archive_btn_download': '⬇️ Download Selected',
        'header_lang_id': '🇮🇩 ID',
        'header_lang_en': '🇬🇧 EN',
        'header_theme_dark': '🌙 Dark',
        'header_theme_light': '☀️ Light',
        'setting_dl_folder': 'Save Folder (PDF)',
        'setting_dl_desc': 'Folder where downloaded books will be stored.',
        'setting_dl_placeholder': 'Click Browse to select a folder...',
        'setting_browse': '📁 Browse',
        'setting_keys_placeholder': 'Paste API Keys here (comma separated)...',
        'setting_repair_title': 'Search Driver (Playwright)',
        'setting_repair_desc': 'If search is not working or shows errors, click the button below to install the driver.',
        'setting_repair_btn': '🛠️ Repair / Install Search Driver',
        'help_html': HELP_HTML_EN if 'HELP_HTML_EN' in globals() else HELP_HTML,
        'about_html': """
        <div style="font-family: sans-serif; line-height: 1.6; color: #212529;">
        <h2>📖 What is Cari Kitab?</h2>
        <p><b>Cari Kitab</b> is a modern desktop application designed to make it easy for researchers, students, 
        and enthusiasts to search, download, and manage digital collections of classic Islamic books and general books 
        from various trusted sources.</p>
        <h2 style="color: #198754;">✨ Key Features (v1.6.0)</h2>
        <ul>
            <li><b>AI Fallback Stability:</b> Intelligent 3-layer mechanism (Gemini Web, Brave AI, Google AI) to ensure answer availability even when APIs are limited.</li>
            <li><b>Smart Arabic Search:</b> Smart search using Artificial Intelligence to accurately handle title variations in Arabic.</li>
            <li><b>PDF Splitter Pro:</b> Built-in tool to split large PDF files by page or size (MB).</li>
            <li><b>AI Book Consultant:</b> Direct Q&A about book content and literature references with Computer Vision support (first 10 pages analysis).</li>
        </ul>
        <h2 style="color: #6f42c1;">🆕 Update v1.6.0</h2>
        <ul>
            <li><b>Zoom & Scaling:</b> Added font enlargement/reduction feature (Font Zoom) in the AI Consultant response area.</li>
            <li><b>Rename UI Improvement:</b> File renaming dialogue is now wider and adaptive to filename length.</li>
            <li><b>Cleaner UI:</b> Removed HTML tags in chat history for a more professional look.</li>
            <li><b>Fallback Optimization:</b> Fallback priorities reorganized (Gemini Web as Priority 1) for longer, more detailed answers.</li>
        </ul>
        <h2 style="color: #dc3545;">👤 Developer Information</h2>
        <p>This application was developed by <b>Isparmo</b> (@vibe-coding) to support easy access to Islamic literature.</p>
        <p>
            <b>🌐 Website:</b> <a href="https://page.isparmo.com" style="color: #0d6efd; text-decoration: none;">https://page.isparmo.com</a><br>
            <b>📧 Email:</b> <a href="mailto:mail@isparmo.com" style="color: #0d6efd; text-decoration: none;">mail@isparmo.com</a><br>
            <b>💬 WhatsApp:</b> <a href="https://wa.me/628121083060" style="color: #0d6efd; text-decoration: none;">08121083060</a>
        </p>
        <hr style="border: 0; border-top: 1px solid #dee2e6; margin: 20px 0;">
        <p style="text-align: center; color: #6c757d; font-size: 11px;">© 2024-2025 Cari Kitab • Build with ❤️ for Ummah</p>
        </div>
        """
    }
}

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        # For directory builds (PyInstaller 6+), data files may be in _internal/
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        
        # 1. Try direct path
        path = os.path.join(base_path, relative_path)
        if os.path.exists(path):
            return path
            
        # 2. Try _internal/ prefix (for directory builds)
        path = os.path.join(base_path, "_internal", relative_path)
        if os.path.exists(path):
            return path
            
        return os.path.join(base_path, relative_path)
    except Exception:
        return os.path.join(os.path.abspath("."), relative_path)

def ensure_playwright_browsers(force=False):
    """ Check if playwright browsers are installed, if not, install them """
    from app.core.playwright_scraper import get_playwright_browsers_path
    browsers_path = get_playwright_browsers_path()
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = browsers_path
    
    # Check if chromium exists
    shared_path = os.path.join(browsers_path, "chromium-*")
    import glob
    existing = glob.glob(shared_path)
    
    if existing and not force:
        logger.info(f"Playwright browsers already exist at {browsers_path}")
        return True

    logger.info(f"Installing Playwright browsers to {browsers_path}...")
    try:
        # Avoid subprocess.run(sys.executable) in frozen mode as it triggers Errno 2
        # Use the playwright library's internal CLI entry point
        from playwright.__main__ import main
        import threading
        
        # Run install in a separate thread to avoid blocking the UI if called from main
        # Note: In our setup, this is called before MainWindow starts, so it's OK to block briefly.
        # But we'll use a safer approach for frozen apps.
        
        env = os.environ.copy()
        env["PLAYWRIGHT_BROWSERS_PATH"] = browsers_path
        
        # Use a more reliable way to invoke the CLI without exiting the app
        import subprocess
        if getattr(sys, 'frozen', False):
            # In frozen app, we can't easily use 'python -m'. 
            # We skip 'sys.executable' and try to find any available 'python' 
            # OR we use the direct driver (more advanced).
            # For now, let's catch the Errno 2 and suggest manual repair if needed.
            logger.warning("Auto-install in frozen mode is restricted. Trying fallback...")
            pass
            
        args = [sys.executable, "-m", "playwright", "install", "chromium"]
        # Use shell=True on Windows to help find executables if needed
        subprocess.run(args, env=env, check=True, capture_output=True, text=True, shell=(os.name == 'nt'))
        
        logger.info("Playwright browsers installed successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to install playwright browsers: {e}")
        return False


def load_app_env():
    """ Load settings from .env into os.environ at startup """
    env_path = get_writable_path(".env")
    if not os.path.exists(env_path):
        env_path_dev = os.path.join(os.getcwd(), ".env")
        if os.path.exists(env_path_dev):
            env_path = env_path_dev
    
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        k, v = line.split("=", 1)
                        os.environ[k.strip()] = v.strip()
            logger.info("Environment variables loaded from .env")
        except Exception as e:
            logger.error(f"Failed to load .env: {e}")

# Configure logging - Use AppData for the log file to avoid PermissionError
app_log_path = get_writable_path("app.log")
logging.basicConfig(
    filename=app_log_path,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

def sanitize_filename(filename):
    # Strict Latin-only sanitization
    import re
    # Remove extension then re-add later to avoid stripping the dot
    name, ext = os.path.splitext(filename)
    
    # Strip non-ASCII characters (including Arabic)
    name = re.sub(r'[^\x00-\x7F]+', '', name)
    # Remove illegal OS characters
    illegal = '<>:"/\\|?*'
    name = "".join([c for c in name if c not in illegal]).strip()
    # Remove any extra hex IDs (regex for long hex strings)
    name = re.sub(r'[a-f0-9]{20,}', '', name)
    # Replace multiple spaces with one
    name = re.sub(r'\s+', ' ', name).strip(' .-')
    
    # Limit length
    return (name[:180] + ext) if name else ("Kitab" + ext)

from app.core.database import db
from app.core.scraper import ShamelaScraper
from app.core.downloader import DownloadManager
from app.ui.components import ResultCard, DownloadItem

from app.services.gemini_search_assistant import GeminiSearchAssistant
from app.services.search_ranker import SearchRanker
from app.core.google_scraper import GoogleShamelaScraper
from app.core.google_global_scraper import GoogleGlobalScraper
from app.core.pdf_splitter import PdfSplitter

# Worker thread for scraping so UI doesn't freeze
class SearchWorker(QThread):
    status_update = Signal(str)
    results_found = Signal(list)
    progress_val = Signal(int)
    error = Signal(str)
 
    def __init__(self, keyword, use_llm=False, page_num=1, source="Shamela", fast_mode=False):
        super().__init__()
        self.keyword = keyword
        self.use_llm = use_llm
        self.page_num = page_num
        self.source = source
        self.fast_mode = fast_mode

    def run(self):
        import asyncio
        async def do_search():
            llm_json = None
            search_query = self.keyword
            
            assistant = GeminiSearchAssistant()
            if self.use_llm:
                self.status_update.emit("[AI] Gemini Active: Normalizing query...")
                llm_json, err_str = await assistant.process_query(self.keyword)
                
                if llm_json:
                    arab_title = llm_json.get("arabic_title", "")
                    if len(arab_title) > 0:
                        search_query = arab_title
                    else:
                        search_query = llm_json.get("normalized_title", self.keyword)
                    self.status_update.emit("[OK] Gemini Success")
                else:
                    self.status_update.emit(f"[ERR] AI: {err_str}" if err_str else "[ERR] API Error / Skipped")
                    
            # 2. Search Logic based on Source
            all_res = []
            search_queries = [search_query]
            if self.use_llm and search_query != self.keyword:
                search_queries.append(self.keyword) # Fallback to raw
                
            for q in search_queries:
                self.status_update.emit(f"[SEARCH] {self.source} Search: {q}...")
                if self.source == "Shamela":
                    google_scraper = GoogleShamelaScraper(assistant=assistant)
                    try:
                        g_res = await google_scraper.search(q, page_num=self.page_num)
                        all_res.extend(g_res)
                    except Exception as e:
                        logger.error(f"Shamela Search failed for {q}: {e}")
                    await google_scraper.close()
                else:
                    global_scraper = GoogleGlobalScraper()
                    try:
                        g_res = await global_scraper.search(q, page_num=self.page_num)
                        all_res.extend(g_res)
                    except Exception as e:
                        logger.error(f"Global Search failed for {q}: {e}")
                    await global_scraper.close()
                
                if len(all_res) > 0: break # Found something!
            
            # 2b. Fallback for long Arabic Queries yielding 0 results
            if len(all_res) == 0 and len(search_query.split()) >= 3:
                fallback_q = ' '.join(search_query.split()[:2])
                self.status_update.emit(f"[SEARCH] Hasil 0. Fallback dengan keyword umum: {fallback_q}...")
                if self.source == "Shamela":
                    google_scraper = GoogleShamelaScraper(assistant=assistant)
                    try:
                        g_res = await google_scraper.search(fallback_q, page_num=self.page_num)
                        all_res.extend(g_res)
                    except Exception as e:
                        logger.error(f"Shamela Fallback Search failed: {e}")
                    await google_scraper.close()
                else:
                    global_scraper = GoogleGlobalScraper()
                    try:
                        g_res = await global_scraper.search(fallback_q, page_num=self.page_num)
                        all_res.extend(g_res)
                    except Exception as e:
                        logger.error(f"Global Fallback Search failed: {e}")
                    await global_scraper.close()
            
            # 3. Deduplicate by detail_url
            self.status_update.emit(f"[CLEAN] Membersihkan duplikat ({len(all_res)} hasil)...")
            seen = set()
            unique_res = []
            for r in all_res:
                url = r.get('detail_url', '')
                if url not in seen:
                    unique_res.append(r)
                    seen.add(url)
            
            enriched = []
            if self.use_llm and llm_json and unique_res:
                unique_res = SearchRanker.rank_results(unique_res, llm_json)
                if not self.fast_mode:
                    self.status_update.emit("[AI] Mentransliterasi & Memproses hasil (Top 10)...")
                    self.progress_val.emit(85)
                    enriched = await assistant.batch_translate_results(unique_res[:10])
                else:
                    self.status_update.emit("[AI] Mode Cepat Aktif: Melewati transliterasi...")
                    enriched = unique_res[:10]
            
            final_res = enriched if enriched else unique_res
            if final_res:
                self.status_update.emit("[META] Melengkapi info halaman & ukuran (Top 8)...")
                final_res = await self._enrich_metadata(final_res)
                self.progress_val.emit(100)
            
            self.results_found.emit(final_res)
            self.status_update.emit(f"[FINISH] Selesai! Menampilkan {len(unique_res)} kitab.")
            return unique_res
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(do_search())
        except Exception as e:
            error_msg = str(e)
            if "Executable doesn't exist" in error_msg or "Errno 2" in error_msg:
                error_msg = ("Browser pencarian belum terinstal atau rusak. "
                            "Aplikasi sedang mencoba mengunduh browser di latar belakang. "
                            "Mohon tunggu 1 menit lalu coba cari lagi.")
                # Trigger a background install attempt
                import threading
                threading.Thread(target=ensure_playwright_browsers, args=(True,)).start()
                
            self.error.emit(error_msg)

    async def _enrich_metadata(self, results):
        if not results: return results
        import httpx
        import re
        
        async def fetch_one(res):
            # Only enrich if metadata is missing
            if res.get('page_count') and res.get('file_size'):
                return res
            
            url = res.get('detail_url')
            if not url or "shamela.org/pdf/" not in url:
                return res
            
            try:
                # Fast HEAD check or a small GET for the head part of HTML
                # Increase timeout slightly to avoid dropping valid connections
                async with httpx.AsyncClient(timeout=12, follow_redirects=True) as client:
                    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
                    resp = await client.get(url, headers=headers)
                    if resp.status_code == 200:
                        html = resp.text
                        p_match = re.search(r'Pages:\s*(\d+)', html)
                        if p_match:
                            res['page_count'] = p_match.group(1).strip()
                        
                        s_match = re.search(r'Size:\s*(\d+)\s*bytes', html)
                        if s_match:
                            try:
                                size_bytes = int(s_match.group(1))
                                res['file_size'] = f"{size_bytes / (1024*1024):.1f} MB"
                            except: pass
            except Exception as e:
                logger.warning(f"Enrichment error for {url}: {e}")
            return res

        import asyncio
        # Reduced to top 8 results for better performance
        tasks = [fetch_one(r) for r in results[:8]]
        if len(results) > 8:
            # The rest are returned as is to avoid blocking
            enriched = await asyncio.gather(*tasks)
            for i, r in enumerate(enriched):
                results[i] = r
        else:
            results = await asyncio.gather(*tasks)
            
        return results

class PdfLinkWorker(QThread):
    finished = Signal(dict, str)
    failed = Signal(str)
    progress_val = Signal(int)
    status_update = Signal(str)

    def __init__(self, book_data, detail_url):
        super().__init__()
        self.book_data = book_data
        self.detail_url = detail_url

    def run(self):
        import asyncio
        async def do_resolve():
            self.status_update.emit(f"[DL] Menyiapkan Download: {self.book_data.get('judul_arab', 'Buku')}...")
            self.progress_val.emit(20)
            scraper = ShamelaScraper()
            try:
                pdf_url = await scraper.get_pdf_link(self.detail_url)
                self.progress_val.emit(100)
                if pdf_url:
                    self.finished.emit(self.book_data, pdf_url)
                else:
                    self.failed.emit("Link PDF tidak ditemukan.")
            except Exception as e:
                self.failed.emit(str(e))
            finally:
                await scraper.close()
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(do_resolve())
        except Exception as e:
            self.failed.emit(str(e))


class AsyncRunnerThread(QThread):
    def __init__(self, loop):
        super().__init__()
        self.loop = loop

    def run(self):
        import asyncio
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()


class KeySettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings - API Keys")
        self.resize(400, 250)
        
        layout = QVBoxLayout(self)
        
        lbl = QLabel("Masukkan Gemini API Keys (pisahkan dengan koma):")
        self.txt_keys = QTextEdit()
        self.txt_keys.setPlaceholderText("AIzaSyXXXX,AIzaSyYYYY,...")
        
        # Load existing
        env_path = get_writable_path(".env")
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("GEMINI_API_KEYS="):
                        self.txt_keys.setPlainText(line.split("=", 1)[1].strip())
                        break
        else:
            # Fallback to dev .env for easier setup
            env_path_dev = os.path.join(os.getcwd(), ".env")
            if os.path.exists(env_path_dev):
                with open(env_path_dev, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("GEMINI_API_KEYS="):
                            self.txt_keys.setPlainText(line.split("=", 1)[1].strip())
                            break
                        
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self.save_keys)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setObjectName("btnSecondary")
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        
        layout.addWidget(lbl)
        layout.addWidget(self.txt_keys)
        layout.addLayout(btn_layout)

    def save_keys(self):
        env_path = get_writable_path(".env")
        keys = self.txt_keys.toPlainText().strip()
        
        lines = []
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        else:
            # Maybe it exists in dev folder? Let's check to copy it if needed
            env_path_dev = os.path.join(os.getcwd(), ".env")
            if os.path.exists(env_path_dev) and not os.path.exists(env_path):
                with open(env_path_dev, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                
        # Update or append
        found = False
        for i, line in enumerate(lines):
            if line.startswith("GEMINI_API_KEYS="):
                lines[i] = f"GEMINI_API_KEYS={keys}\n"
                found = True
                break
                
        if not found:
            lines.append(f"GEMINI_API_KEYS={keys}\n")
            
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
            
        # reload in memory
        from app.services.gemini_search_assistant import global_rotator
        global_rotator.reload_keys()
        
        self.accept()

class SplitDialog(QDialog):
    def __init__(self, filename, pages="N/A", size_mb="N/A", parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Split PDF")
        self.setFixedWidth(420)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        lbl = QLabel(f"<b>Split Kitab:</b><br>{filename}")
        lbl.setWordWrap(True)
        layout.addWidget(lbl)
        
        # Info Badge
        info_lbl = QLabel(f"📊 Totals: {pages} Halaman • {size_mb}")
        info_lbl.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 5px; border-radius: 4px; color: #495057;")
        layout.addWidget(info_lbl)
        
        self.rb_pages = QRadioButton("Bagi berdasarkan jumlah HALAMAN (contoh: tiap 100 hal)")
        self.rb_size = QRadioButton("Bagi berdasarkan ukuran SIZE MB (contoh: tiap 50 MB)")
        self.rb_pages.setChecked(True)
        
        layout.addWidget(self.rb_pages)
        layout.addWidget(self.rb_size)
        
        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("Nilai (Angka):"))
        self.input_val = QSpinBox()
        self.input_val.setRange(1, 100000)
        self.input_val.setValue(100)
        h_layout.addWidget(self.input_val)
        layout.addLayout(h_layout)
        
        btns = QHBoxLayout()
        self.btn_ok = QPushButton("Mulai Proses Split")
        self.btn_ok.setStyleSheet("background-color: #0d6efd; color: white; font-weight: bold;")
        self.btn_ok.clicked.connect(self.accept)
        
        self.btn_cancel = QPushButton("Batal")
        self.btn_cancel.setObjectName("btnSecondary")
        self.btn_cancel.clicked.connect(self.reject)
        
        btns.addStretch()
        btns.addWidget(self.btn_cancel)
        btns.addWidget(self.btn_ok)
        layout.addLayout(btns)

    def get_values(self):
        return ("pages" if self.rb_pages.isChecked() else "size"), self.input_val.value()

class SplitWorker(QThread):
    finished = Signal(list)
    error = Signal(str)
    status_update = Signal(str)
    
    def __init__(self, pdf_path, split_type, value):
        super().__init__()
        self.pdf_path = pdf_path
        self.split_type = split_type
        self.value = value
        
    def run(self):
        try:
            self.status_update.emit("[WAIT] Menyiapkan split PDF...")
            splitter = PdfSplitter()
            
            def p_callback(curr, total):
                self.status_update.emit(f"[WAIT] Memproses bagian {curr} dari {total}...")
                
            if self.split_type == "pages":
                results = splitter.split_by_pages(self.pdf_path, self.value, progress_callback=p_callback)
            else:
                results = splitter.split_by_size(self.pdf_path, self.value, progress_callback=p_callback)
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))


class ArchiveFetchWorker(QThread):
    """
    Worker thread yang mengambil metadata file dari Archive.org.
    Emits finished(dict) ketika selesai, atau error(str) jika gagal.
    """
    finished = Signal(dict)
    error = Signal(str)
    status_update = Signal(str)

    def __init__(self, detail_url, mode="pdf"):
        super().__init__()
        self.detail_url = detail_url
        self.mode = mode  # "pdf" or "fulltext"

    def run(self):
        import asyncio
        from app.core.archive_fetcher import fetch_archive_files
        try:
            self.status_update.emit("[WAIT] Mengambil daftar file dari Archive.org...")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(fetch_archive_files(self.detail_url))
            loop.close()
            if result.get("error"):
                self.error.emit(result["error"])
            else:
                self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class ArchiveDownloadDialog(QDialog):
    """
    Dialog pemilihan file untuk download dari Archive.org.
    Mendukung multi-select dan toggle antara PDF Scan / PDF With Text / Full Text.
    File-file yang dipilih akan didownload secara berurutan (antrian).
    """
    # Signal: list of {name, url, size_mb} yang dipilih user
    files_selected = Signal(list)

    def __init__(self, archive_data: dict, initial_mode: str = "pdf", parent=None):
        super().__init__(parent)
        self.archive_data = archive_data
        self.initial_mode = initial_mode  # "pdf" or "fulltext"
        
        # Get translations
        self.current_lang = os.environ.get('APP_LANG', 'id')
        self.texts = UI_STRINGS.get(self.current_lang, UI_STRINGS['id'])

        title = archive_data.get("title", "Archive.org Item")
        self.setWindowTitle(f"{self.texts['archive_dialog_title']}: {title[:60]}...")
        self.setMinimumWidth(560)
        self.setMinimumHeight(480)

        self._build_ui(title)
        self._switch_mode(self.initial_mode)

    def _build_ui(self, title):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)

        # Header
        lbl_title = QLabel(f"<b>📥 {title}</b>")
        lbl_title.setWordWrap(True)
        lbl_title.setStyleSheet("font-size: 14px;")
        layout.addWidget(lbl_title)

        # Mode selector (tab-like buttons)
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(4)

        self.btn_mode_pdf = QPushButton(self.texts['archive_mode_pdf'])
        self.btn_mode_pdf.setCheckable(True)
        self.btn_mode_pdf.setChecked(True)
        self.btn_mode_pdf.setMinimumHeight(36)
        self.btn_mode_pdf.clicked.connect(lambda: self._switch_mode("pdf"))

        self.btn_mode_pdf_text = QPushButton(self.texts['archive_mode_pdf_text'])
        self.btn_mode_pdf_text.setCheckable(True)
        self.btn_mode_pdf_text.setMinimumHeight(36)
        self.btn_mode_pdf_text.clicked.connect(lambda: self._switch_mode("pdf_text"))

        self.btn_mode_fulltext = QPushButton(self.texts['archive_mode_fulltext'])
        self.btn_mode_fulltext.setCheckable(True)
        self.btn_mode_fulltext.setMinimumHeight(36)
        self.btn_mode_fulltext.clicked.connect(lambda: self._switch_mode("fulltext"))
        
        mode_layout.addWidget(self.btn_mode_pdf)
        mode_layout.addWidget(self.btn_mode_pdf_text)
        mode_layout.addWidget(self.btn_mode_fulltext)
        layout.addLayout(mode_layout)

        # Mode description label
        self.lbl_mode_desc = QLabel("")
        self.lbl_mode_desc.setStyleSheet("font-size: 11px; color: #6c757d; padding: 2px 0;")
        self.lbl_mode_desc.setWordWrap(True)
        layout.addWidget(self.lbl_mode_desc)

        # File list (scroll area dengan checkboxes)
        self.file_scroll = QScrollArea()
        self.file_scroll.setWidgetResizable(True)
        self.file_scroll.setMinimumHeight(220)

        self.file_container = QWidget()
        self.file_list_layout = QVBoxLayout(self.file_container)
        self.file_list_layout.setSpacing(4)
        self.file_list_layout.setContentsMargins(8, 8, 8, 8)
        self.file_list_layout.addStretch()

        self.file_scroll.setWidget(self.file_container)
        layout.addWidget(self.file_scroll)

        # Count / info label
        self.lbl_count = QLabel("0 file tersedia")
        self.lbl_count.setStyleSheet("font-size: 11px; color: #6c757d;")
        layout.addWidget(self.lbl_count)

        # Select All / Clear All
        sel_layout = QHBoxLayout()
        btn_select_all = QPushButton(self.texts['archive_select_all'])
        btn_select_all.setFixedHeight(30)
        btn_select_all.clicked.connect(self._select_all)
        btn_clear_all = QPushButton(self.texts['archive_clear_all'])
        btn_clear_all.setFixedHeight(30)
        btn_clear_all.clicked.connect(self._clear_all)
        sel_layout.addWidget(btn_select_all)
        sel_layout.addWidget(btn_clear_all)
        sel_layout.addStretch()
        layout.addLayout(sel_layout)

        # Action buttons
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Batal" if self.current_lang == 'id' else "Cancel")
        btn_cancel.setObjectName("btnSecondary")
        btn_cancel.setFixedHeight(38)
        btn_cancel.clicked.connect(self.reject)

        self.btn_download = QPushButton(self.texts['archive_btn_download'])
        self.btn_download.setFixedHeight(38)
        self.btn_download.setStyleSheet("background-color: #0d6efd; color: white; font-weight: bold; border-radius: 4px;")
        self.btn_download.clicked.connect(self._on_download)


        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(self.btn_download)
        layout.addLayout(btn_layout)

        # Simpan semua checkboxes untuk akses mudah
        self._checkboxes = []

    def _switch_mode(self, mode):
        """Ganti tampilan daftar file sesuai mode."""
        self.current_mode = mode

        # Update tombol mode
        self.btn_mode_pdf.setChecked(mode == "pdf")
        self.btn_mode_pdf_text.setChecked(mode == "pdf_text")
        self.btn_mode_fulltext.setChecked(mode == "fulltext")

        # Ambil file sesuai mode
        if mode == "pdf":
            files = self.archive_data.get("pdf_files", [])
            desc = "PDF Scan asli. Kualitas gambar terbaik namun tidak bisa di-search teksnya."
            btn_label = "⬇️ Download PDF Terpilih"
        elif mode == "pdf_text":
            files = self.archive_data.get("pdf_text_files", [])
            desc = "PDF dengan Text Layer dari OCR. Bisa di-search, copy-paste teks. Cocok untuk membaca & NotebookLM."
            btn_label = "⬇️ Download PDF+Text Terpilih"
        else:  # fulltext
            files = self.archive_data.get("full_text_files", [])
            desc = "File teks murni (.txt) hasil OCR. Ukuran sangat kecil, ideal untuk NotebookLM dan analisis teks."
            btn_label = "⬇️ Download Full Text Terpilih"

        # Update disabled state untuk mode yang tidak tersedia
        pdf_text_files = self.archive_data.get("pdf_text_files", [])
        if not pdf_text_files:
            self.btn_mode_pdf_text.setEnabled(False)
            self.btn_mode_pdf_text.setToolTip("PDF With Text tidak tersedia untuk item ini")
        else:
            self.btn_mode_pdf_text.setEnabled(True)
            self.btn_mode_pdf_text.setToolTip(f"{len(pdf_text_files)} file PDF With Text tersedia")

        self.lbl_mode_desc.setText(desc)
        self.btn_download.setText(btn_label)
        self._populate_files(files)

    def _populate_files(self, files):
        """Isi daftar file dengan checkboxes."""
        # Hapus checkbox lama
        self._checkboxes.clear()
        while self.file_list_layout.count() > 1:  # keep the stretch at end
            item = self.file_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not files:
            lbl_empty = QLabel("⚠️ Tidak ada file tersedia untuk format ini.")
            lbl_empty.setStyleSheet("color: #dc3545; padding: 10px;")
            self.file_list_layout.insertWidget(0, lbl_empty)
            self.lbl_count.setText("0 file tersedia")
            self.btn_download.setEnabled(False)
            return

        self.btn_download.setEnabled(True)
        for i, f in enumerate(files):
            name = f.get("name", "unknown")
            size_mb = f.get("size_mb", "N/A")

            cb = QCheckBox(f"  {name}\n  💾 {size_mb}")
            cb.setChecked(True)  # default semua terpilih
            cb.file_data = f  # simpan data di checkbox
            cb.setStyleSheet("padding: 4px; font-size: 12px;")
            self._checkboxes.append(cb)
            self.file_list_layout.insertWidget(i, cb)

        total_size = sum(f.get("size_bytes", 0) for f in files)
        total_mb = total_size / (1024 * 1024)
        self.lbl_count.setText(
            f"{len(files)} file tersedia • Total: {total_mb:.1f} MB"
        )

    def _select_all(self):
        for cb in self._checkboxes:
            cb.setChecked(True)

    def _clear_all(self):
        for cb in self._checkboxes:
            cb.setChecked(False)

    def _on_download(self):
        selected = [cb.file_data for cb in self._checkboxes if cb.isChecked()]
        if not selected:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Peringatan", "Pilih minimal 1 file untuk didownload.")
            return
        self.files_selected.emit(selected)
        self.accept()


class ChatWorker(QThread):
    response_ready = Signal(str)
    error = Signal(str)
    status_update = Signal(str)
    
    def __init__(self, message, history=None, image_paths=None, metadata_header=None):
        super().__init__()
        self.message = message
        self.history = history or []
        self.image_paths = image_paths or [] # Multiple images
        self.metadata_header = metadata_header or ""
        
    def run(self):
        def try_fallback():
            try:
                from app.services.google_ai_fallback import GoogleAIFallback
                self.status_update.emit("[LIMIT] Limit Gemini tercapai. Mencari jawaban alternatif via Google AI...")
                
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # PENCERAHAN (Solusi Ringkas):
                system_instruction = "Sajikan jawaban dalam Bahasa Indonesia. WAJIB sertakan tulisan Arab aslinya di dalam kurung setelah setiap Anda menyebutkan judul kitab atau nama ulama (Contoh: Tafsir Al-Jalalain (تفسير الجلالين)). Pertanyaan: "
                
                # BUGFIX: Ambil override_prompt (yang berisi Metadata) bukan sel.message UI kosong
                base_prompt = getattr(self, 'override_prompt', self.message)
                fallback_prompt = system_instruction + base_prompt
                
                # BUGFIX: Injeksi manual 10 halaman (PDF Local Text Extraction) untuk Lapis 1 (Brave AI)
                vision_text = getattr(self, 'current_vision_text', '')
                if vision_text:
                    fallback_prompt += f"\n\n[DOKUMEN TEKS DARI BUKU UNTUK DIANALISIS]:\n{vision_text[:12000]}"
                
                # Use a combined timeout for the whole fallback process
                async def get_ans_with_timeout():
                    return await GoogleAIFallback().get_answer(fallback_prompt, status_signal=self.status_update)
                
                try:
                    ans = loop.run_until_complete(asyncio.wait_for(get_ans_with_timeout(), timeout=120))
                except asyncio.TimeoutError:
                    logger.warning("Google AI Fallback timed out after 120s")
                    return False
                
                if ans:
                    # POST-PROCESSING (Local Action): Format HTML dengan Regex Pintar 
                    # untuk mendeteksi: Latin (Arab) lalu menyulapnya menjadi Clickable Links mandiri.
                    import re
                    def make_fallback_link(match):
                        raw_latin = match.group(1).strip()
                        arab = match.group(2).strip()
                        clean_latin = re.sub(r'<[^>]+>', '', raw_latin).strip()
                        return f'<a href="search:{clean_latin}">{raw_latin}</a> (<a href="search:{arab}">{arab}</a>)'

                    # BUGFIX: Pola baru ini menolerir keberadaan tag HTML (seperti <b> / <i>) dari output AI asli.
                    pattern = r'((?:<[^>]+>)*[A-Za-z0-9\s\'-]+?(?:<[^>]+>)*)\s*\(([\u0600-\u06FF\s]+)\)'
                    ans = re.sub(pattern, make_fallback_link, ans)
                    
                    note = "<p><i style='color:#666;'>[Jawaban ini dihasilkan secara otomatis via Google AI karena API Gemini sedang limit]</i></p>"
                    # Prepend metadata header if exists
                    final_ans = self.metadata_header + ans + note
                    self.response_ready.emit(final_ans)
                    return True
            except Exception as fe:
                logger.error(f"Fallback failed: {fe}")
            return False

        try:
            from app.services.gemini_search_assistant import global_rotator
            import google.api_core.exceptions
            
            # --- HIGH-AVAILABILITY RETRY LOOP (v1.5.9) ---
            MAX_RETRIES = len(global_rotator.keys) or 10
            attempt = 0
            success = False
            
            while attempt < MAX_RETRIES and not success:
                api_key = global_rotator.get_key()
                # ===== SIMULASI REALTIME: Memaksa Fallback ====
                # logger.warning("[AI Chat-Simulasi] Memaksa Limit API. Melompat ke fallback...")
                # if try_fallback(): return
                # ===============================================
                if not api_key:
                    logger.warning("[AI Chat] All keys on cooldown. Trying fallback...")
                    if try_fallback(): return
                    self.error.emit("Semua limit API key habis. Silakan coba lagi nanti.")
                    return
                
                attempt += 1
                logger.info(f"[AI Chat] Attempt {attempt}: Using Key ending in *{api_key[-4:]}")
                
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=api_key)
                    
                    # Dynamic System Prompt based on whether we have metadata (document analysis) or not (general question)
                    if self.metadata_header:
                        system_prompt = """Anda adalah 'Pakar Analisis Kitab Klasik'.
Tugas Anda adalah membedah buku/kitab yang diberikan dengan struktur HTML yang sangat bersih.

STRUKTUR JAWABAN (WAJIB):
1. <h3 style='color:#2c3e50;'>📄 METADATA DOKUMEN</h3>
   (Sajikan tabel metadata teknis yang diberikan di awal menggunakan tag <table> standar)

2. <h3 style='color:#2c3e50;'>📚 DAFTAR ISI / STRUKTUR KITAB</h3>
   (Sajikan poin-poin bab atau struktur isi yang ditemukan dari gambar/teks halaman awal)

3. <h3 style='color:#2c3e50;'>📝 RESUME & ANALISIS (Max 500 Kata)</h3>
   (Berikan ringkasan isi kitab secara mendalam, teknis, dan profesional)

ATURAN FORMAT (SANGAT PENTING):
- WAJIB: Setiap kali menyebutkan Judul Kitab atau Nama Pengarang, pisahkan teks Latin dan Arab ke dalam dua link HTML yang berbeda agar keduanya bisa diklik secara mandiri.
- WAJIB: Formatnya HARUS seperti ini: <a href="search:Teks_Latin">Teks Latin</a> (<a href="search:Teks_Arab">Teks_Arab</a>). Contoh yang BENAR: <a href="search:Fiqh As-Sirah">Fiqh As-Sirah</a> (<a href="search:فقه السيرة">فقه السيرة</a>).
- DILARANG KERAS MENGGUNAKAN MARKDOWN (###, **, |).
- GUNAKAN HTML SEMANTIK: <h3>, <p>, <ul>, <li>, <b>, <i>, <table>, <tr>, <td>.
- BAHASA: Bahasa Indonesia formal level tinggi (Akademik/Santri Profesional)."""
                    else:
                        system_prompt = """Anda adalah 'Pakar Literatur Islam & Asisten Peneliti'.
Tugas Anda adalah menjawab pertanyaan pengguna seputar kitab, buku, atau tokoh Islam dengan akurat dan profesional.

ATURAN FORMAT (SANGAT PENTING):
- JANGAN tampilkan tabel METADATA jika tidak disediakan di awal.
- WAJIB: Setiap kali menyebutkan Judul Kitab atau Nama Pengarang, pisahkan teks Latin dan Arab ke dalam dua link HTML yang berbeda agar keduanya bisa diklik secara mandiri.
- WAJIB: Formatnya HARUS seperti ini: <a href="search:Teks_Latin">Teks Latin</a> (<a href="search:Teks_Arab">Teks_Arab</a>). Contoh yang BENAR: <a href="search:Shahih Bukhari">Shahih Bukhari</a> (<a href="search:صحيح البخاري">صحيح البخاري</a>).
- DILARANG KERAS MENGGUNAKAN MARKDOWN. Gunakan tag HTML: <h3>, <p>, <ul>, <li>, <b>, <i>.
- BAHASA: Bahasa Indonesia formal yang sopan dan berwibawa."""

                    model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_prompt)
                    
                    # Prepare message context
                    prompt = self.message
                    if self.history:
                        context = "\n".join([f"User: {m['user']}\nAI: {m['ai']}" for m in self.history[-3:]])
                        prompt = f"Context history:\n{context}\n\nUser Question: {self.message}"
                    
                    prompt_parts = []
                    # Handle multiple images
                    if self.image_paths:
                        from pathlib import Path
                        try:
                            import PIL.Image
                            for img_path in self.image_paths:
                                if os.path.exists(img_path):
                                    img = PIL.Image.open(img_path)
                                    prompt_parts.append(img)
                        except Exception as ie:
                            logger.error(f"PIL Image process failed: {ie}")
                            for img_path in self.image_paths:
                                if os.path.exists(img_path):
                                    prompt_parts.append({
                                        'mime_type': 'image/jpeg',
                                        'data': Path(img_path).read_bytes()
                                    })

                    prompt_parts.append(prompt)
                    
                    # Generate content
                    response = model.generate_content(prompt_parts)
                    
                    if response.text:
                        text = response.text
                        # Cleanup and Post-process (Safety Net)
                        if "```html" in text:
                            text = text.split("```html")[1].split("```")[0].strip()
                        elif "```" in text:
                            text = text.split("```")[1].strip()
                        
                        # Markdown to HTML converter logic
                        import re
                        text = re.sub(r'^###\s+(.*)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
                        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
                        
                        # Markdown Table to HTML conversion
                        if "|" in text and "--" in text:
                            lines = text.split('\n')
                            new_lines = []
                            in_table = False
                            for l in lines:
                                if "|" in l and "---" not in l:
                                    if not in_table:
                                        in_table = True
                                        new_lines.append('<table border="1" style="border-collapse: collapse; width: 100%;">')
                                    cols = [c.strip() for c in l.split("|") if c.strip()]
                                    new_lines.append("<tr>" + "".join([f"<td style='padding: 6px;'>{c}</td>" for c in cols]) + "</tr>")
                                elif in_table and "---" in l: continue
                                else:
                                    if in_table: in_table = False; new_lines.append('</table>')
                                    new_lines.append(l)
                            text = "\n".join(new_lines)

                        if "<p>" not in text.lower(): text = text.replace('\n', '<br>')
                        
                        # Post-processing to ensure all Latin (Arabic) patterns are clickable
                        import re
                        pattern = r'((?:<[^>]+>)*[A-Za-z0-9\s\'-]+?(?:<[^>]+>)*)\s*\(([\u0600-\u06FF\s]+)\)'
                        def make_link(match):
                            raw_latin = match.group(1).strip()
                            arab = match.group(2).strip()
                            clean_latin = re.sub(r'<[^>]+>', '', raw_latin).strip()
                            # Avoid double linking if AI already did it
                            if 'href=' in text[max(0, match.start()-20):match.end()+10]:
                                return match.group(0)
                            return f'<a href="search:{clean_latin}">{raw_latin}</a> (<a href="search:{arab}">{arab}</a>)'
                        
                        text = re.sub(pattern, make_link, text)
                        
                        # Prepend metadata header if exists
                        final_ans = (self.metadata_header if self.metadata_header else "") + text
                        self.response_ready.emit(final_ans)
                        success = True
                        logger.info(f"[AI Chat] Request successful with Key ending in *{api_key[-4:]}")
                    else:
                        raise Exception("Empty response text from AI.")

                except google.api_core.exceptions.ResourceExhausted:
                    logger.warning(f"[AI Chat] Key ending in *{api_key[-4:]} is exhausted (429). Rotating...")
                    global_rotator.report_error(api_key, 429)
                    continue # Try next key
                except Exception as attempt_error:
                    logger.error(f"[AI Chat] Attempt {attempt} error: {attempt_error}")
                    global_rotator.report_error(api_key, 500)
                    # If it's a critical non-rate-limit error (like bad request), we might still want to try next key
                    continue
            
            if not success:
                logger.warning("[AI Chat] All attempts failed. Jumping to fallback...")
                if try_fallback(): return
                self.error.emit("Gagal memproses AI bahkan setelah rotasi key. Silakan coba lagi.")

        except Exception as major_e:
            logger.error(f"ChatWorker critical fault: {major_e}")
            self.error.emit(f"Sistem Error: {str(major_e)}")

class VisionPeekerWorker(QThread):
    """Worker untuk mengambil cuplikan halaman PDF (Peeking) demi analisis ToC/Intro."""
    done = Signal(list, str) # List of local image paths, extracted 10-page text for Fallback
    status = Signal(str)

    def __init__(self, book_data):
        super().__init__()
        self.book_data = book_data

    def run(self):
        import httpx
        import fitz # PyMuPDF
        import tempfile
        import os
        from pathlib import Path
        
        image_paths = []
        extracted_text = ""
        d_url = self.book_data.get('detail_url', '') or self.book_data.get('url', '')
        
        # 1. Archive.org Peeking (Thumbnails are faster)
        if 'archive.org' in d_url.lower():
            from app.core.archive_fetcher import extract_archive_identifier
            ident = extract_archive_identifier(d_url)
            if ident:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
                # Ambil halaman 0-9 (ToC biasanya di sini)
                for p in range(10):
                    thumb_url = f"https://archive.org/download/{ident}/page/n{p}.jpg"
                    try:
                        resp = httpx.get(thumb_url, headers=headers, timeout=10)
                        if resp.status_code == 200:
                            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=f"_p{p}.jpg")
                            tmp.write(resp.content)
                            tmp.close()
                            image_paths.append(tmp.name)
                            self.status.emit(f"🖼️ Mengunduh cuplikan halaman {p+1}...")
                    except Exception: continue
        
        # 2. General PDF Peeking (Shamela / Direct)
        elif d_url.lower().endswith('.pdf') or 'shamela.org/pdf/' in d_url.lower():
            try:
                self.status.emit("🔍 Mengintip struktur file PDF (10 Halaman)...")
                # Buffer 5MB (Range Request) to ensure enough pages for high-res scans
                headers = {
                    "Range": "bytes=0-5242880",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                } 
                with httpx.Client(follow_redirects=True, timeout=25) as client:
                    resp = client.get(d_url, headers=headers)
                    if resp.status_code in (200, 206):
                        doc = fitz.open(stream=resp.content, filetype="pdf")
                        max_peek = min(doc.page_count, 10)
                        for p in range(max_peek):
                            page = doc[p]
                            # Extract Text for Fallback (10 pages context limit)
                            try:
                                extracted_text += page.get_text() + "\n\n"
                            except Exception: pass
                                
                            # High quality render for better OCR/AI vision
                            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
                            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=f"_p{p}.jpg")
                            pix.save(tmp.name)
                            image_paths.append(tmp.name)
                            self.status.emit(f"🖼️ Menyiapkan visual & teks halaman {p+1}...")
                        doc.close()
            except Exception as e:
                logger.error(f"Peeking failed: {e}")

        logger.info(f"[Deep Vision] Total images captured: {len(image_paths)}")
        self.done.emit(image_paths, extracted_text)

class TranslateWorker(QThread):
    response_ready = Signal(str)
    error = Signal(str)
    status_update = Signal(str)
    
    def __init__(self, text, target_lang):
        super().__init__()
        self.text = text
        self.target_lang = target_lang
        
    def run(self):
        try:
            from app.services.gemini_search_assistant import global_rotator
            import google.generativeai as genai
            import google.api_core.exceptions
            
            prompt = f"Terjemahkan teks berikut ke bahasa {self.target_lang}. Jika teks adalah bahasa arab, artikan dengan baik. Hanya berikan hasil terjemahan akhirnya saja tanpa penjelasan tambahan atau tanda kutip pembungkus:\n\n{self.text}"
            
            success = False
            
            # 1. Coba via Gemini jika ada API key
            if global_rotator.keys:
                MAX_RETRIES = min(len(global_rotator.keys), 5)
                attempt = 0
                
                while attempt < MAX_RETRIES and not success:
                    api_key = global_rotator.get_key()
                    if not api_key:
                        break
                        
                    attempt += 1
                    try:
                        self.status_update.emit(f"[AI] Menerjemahkan via Gemini ({api_key[-4:]})...")
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel("gemini-1.5-flash") # model fallback to standard
                        response = model.generate_content(prompt, request_options={"timeout": 30})
                        
                        if response and response.text:
                            self.response_ready.emit(response.text.strip())
                            success = True
                            break
                    except google.api_core.exceptions.ResourceExhausted:
                        global_rotator.report_error(api_key, 429)
                        continue
                    except Exception as attempt_error:
                        global_rotator.report_error(api_key, 500)
                        continue
                        
            # 2. Fallback jika Gemini gagal atau API key tidak ada / tidak valid
            if not success:
                try:
                    self.status_update.emit("Menerjemahkan via Google Translate Engine...")
                    import httpx
                    import urllib.parse
                    
                    dest_code = 'id' if 'indonesia' in self.target_lang.lower() else ('en' if 'inggris' in self.target_lang.lower() else 'ar')
                    translated = None
                    
                    # 2a. Google Translate Mobile Client API (POST - tahan blokir & bebas batas URL)
                    try:
                        gt_url = "https://translate.google.com/translate_a/single"
                        params = {'client': 'at', 'sl': 'auto', 'tl': dest_code, 'dt': 't'}
                        headers = {'User-Agent': 'GoogleTranslate/6.28.0.05.421483610 (Linux; U; Android 12; Pixel 6)'}
                        with httpx.Client(timeout=20) as client:
                            r = client.post(gt_url, params=params, data={'q': self.text}, headers=headers)
                            if r.status_code == 200:
                                data = r.json()
                                res_text = ''.join([item[0] for item in data[0] if item and item[0]])
                                if res_text.strip():
                                    translated = res_text.strip()
                    except Exception as gt_err:
                        import logging
                        logging.getLogger(__name__).warning(f"Google Translate API failed: {gt_err}")
                        
                    # 2b. Secondary Fallback: MyMemory API
                    if not translated:
                        self.status_update.emit("Mencoba engine terjemahan alternatif (MyMemory)...")
                        chunks = [self.text[i:i+450] for i in range(0, len(self.text), 450)]
                        results = []
                        with httpx.Client(timeout=20) as client:
                            for ch in chunks:
                                mm_url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(ch)}&langpair=auto|{dest_code}"
                                mr = client.get(mm_url)
                                if mr.status_code == 200:
                                    mdata = mr.json()
                                    results.append(mdata.get('responseData', {}).get('translatedText', ''))
                        res_text = ' '.join(results).strip()
                        if res_text:
                            translated = res_text
                            
                    if translated:
                        self.response_ready.emit(translated)
                        success = True
                    else:
                        raise Exception("Semua server terjemahan cadangan tidak merespon.")
                            
                except Exception as fb_err:
                    import logging
                    logging.getLogger(__name__).error(f"Fallback translate failed: {fb_err}")
                    self.error.emit(f"Gagal menerjemahkan: {fb_err}")
        except Exception as e:
            self.error.emit(f"Sistem Error: {str(e)}")

class TranslatePopupDialog(QDialog):
    def __init__(self, text_to_translate, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Terjemahkan Teks / Translate Text")
        self.resize(800, 600)
        
        if parent:
            self.setStyleSheet(parent.styleSheet())
            
        layout = QVBoxLayout(self)
        
        # Tools
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Bahasa Tujuan:"))
        self.cb_lang = QComboBox()
        self.cb_lang.addItems(["Indonesia", "Inggris", "Arab"])
        top_layout.addWidget(self.cb_lang)
        
        self.btn_translate = QPushButton("🚀 Terjemahkan")
        self.btn_translate.clicked.connect(self.do_translate)
        top_layout.addWidget(self.btn_translate)
        
        self.lbl_status = QLabel("Siap.")
        self.lbl_status.setStyleSheet("color: #6c757d; font-size: 11px;")
        
        self.font_size = 12
        btn_zoom_out = QPushButton("-")
        btn_zoom_out.setFixedSize(30, 30)
        btn_zoom_out.setStyleSheet("font-weight: bold; font-size: 18px; padding: 0px; color: white;")
        btn_zoom_out.clicked.connect(lambda: self.change_font_size(-2))
        btn_zoom_in = QPushButton("+")
        btn_zoom_in.setFixedSize(30, 30)
        btn_zoom_in.setStyleSheet("font-weight: bold; font-size: 18px; padding: 0px; color: white;")
        btn_zoom_in.clicked.connect(lambda: self.change_font_size(2))
        self.lbl_zoom = QLabel("100%")
        
        top_layout.addStretch()
        top_layout.addWidget(btn_zoom_out)
        top_layout.addWidget(self.lbl_zoom)
        top_layout.addWidget(btn_zoom_in)
        top_layout.addSpacing(20)
        top_layout.addWidget(self.lbl_status)
        
        layout.addLayout(top_layout)
        
        # Splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left: Original
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0,0,0,0)
        left_layout.addWidget(QLabel("Teks Asli:"))
        self.txt_original = QTextEdit()
        self.txt_original.setPlainText(text_to_translate)
        left_layout.addWidget(self.txt_original)
        splitter.addWidget(left_widget)
        
        # Right: Result
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0,0,0,0)
        right_layout.addWidget(QLabel("Hasil Terjemahan:"))
        self.txt_result = QTextEdit()
        right_layout.addWidget(self.txt_result)
        
        # Export Buttons
        export_layout = QHBoxLayout()
        btn_copy = QPushButton("📋 Copy Hasil")
        btn_copy.clicked.connect(lambda: QApplication.clipboard().setText(self.txt_result.toPlainText()))
        btn_save_txt = QPushButton("💾 Simpan TXT")
        btn_save_txt.clicked.connect(self.save_txt)
        btn_save_docx = QPushButton("💾 Simpan DOCX")
        btn_save_docx.clicked.connect(self.save_docx)
        export_layout.addWidget(btn_copy)
        export_layout.addWidget(btn_save_txt)
        export_layout.addWidget(btn_save_docx)
        right_layout.addLayout(export_layout)
        
        splitter.addWidget(right_widget)
        layout.addWidget(splitter)
        
        self.worker = None

    def do_translate(self):
        text = self.txt_original.toPlainText().strip()
        if not text: return
        lang = self.cb_lang.currentText()
        self.btn_translate.setEnabled(False)
        self.txt_result.clear()
        
        self.worker = TranslateWorker(text, lang)
        self.worker.response_ready.connect(self.on_success)
        self.worker.error.connect(self.on_error)
        self.worker.status_update.connect(self.lbl_status.setText)
        self.worker.finished.connect(lambda: self.btn_translate.setEnabled(True))
        self.worker.start()
        
    def on_success(self, text):
        lang = self.cb_lang.currentText().lower()
        if 'arab' in lang:
            self.txt_result.setLayoutDirection(Qt.RightToLeft)
            self.txt_result.setAlignment(Qt.AlignRight)
        else:
            self.txt_result.setLayoutDirection(Qt.LeftToRight)
            self.txt_result.setAlignment(Qt.AlignLeft)
            
        self.txt_result.setPlainText(text)
        self.lbl_status.setText("✅ Berhasil.")
        
    def on_error(self, err):
        QMessageBox.warning(self, "Error", err)
        self.lbl_status.setText("❌ Gagal.")
        
    def change_font_size(self, delta):
        self.font_size = max(8, min(72, self.font_size + delta))
        f = self.txt_original.font()
        f.setPointSize(self.font_size)
        self.txt_original.setFont(f)
        self.txt_result.setFont(f)
        percent = int((self.font_size / 12) * 100)
        self.lbl_zoom.setText(f"{percent}%")
        
    def save_txt(self):
        text = self.txt_result.toPlainText()
        if not text: return
        path, _ = QFileDialog.getSaveFileName(self, "Simpan TXT", get_downloads_dir(), "Text Files (*.txt)")
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(text)
                QMessageBox.information(self, "Sukses", "Teks berhasil disimpan.")
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))
                
    def save_docx(self):
        text = self.txt_result.toPlainText()
        if not text: return
        path, _ = QFileDialog.getSaveFileName(self, "Simpan DOCX", get_downloads_dir(), "Word Document (*.docx)")
        if path:
            try:
                import docx
                doc = docx.Document()
                doc.add_paragraph(text)
                doc.save(path)
                QMessageBox.information(self, "Sukses", "Dokumen Word berhasil disimpan.")
            except ImportError:
                QMessageBox.warning(self, "Error", "Modul python-docx belum terinstal. Silakan jalankan: pip install python-docx")
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        load_app_env() # Load user settings immediately
        self.setWindowTitle(f"Cari Kitab v{APP_VERSION} - Digital Library Assistant")
        icon_path = resource_path("app/assets/logo.ico") if os.name == 'nt' else resource_path("app/assets/logo.png")
        self.setWindowIcon(QIcon(icon_path))
        self.resize(1100, 750)
        
        # Explicitly request standard window buttons to prevent some sandboxes from hiding them
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        
        self.download_manager = DownloadManager(download_dir=get_downloads_dir())
        self.download_manager.signals.progress.connect(self.on_download_progress)
        self.download_manager.signals.finished.connect(self.on_download_finished)
        self.download_manager.signals.error.connect(self.on_download_error)
        
        import asyncio
        self.async_loop = asyncio.new_event_loop()
        self.async_thread = AsyncRunnerThread(self.async_loop)
        self.async_thread.start()
        
        # Load preferences
        self.is_dark_mode = os.environ.get('APP_THEME', 'dark') == 'dark'
        self.current_lang = os.environ.get('APP_LANG', 'id')
        self.load_theme()
        QTimer.singleShot(100, self.retranslate_ui) 
        
        # Progress Bar & Global Status
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(12)
        self.lbl_global_status = QLabel("Ready.")
        self.lbl_global_status.setStyleSheet("font-size: 11px; color: #6c757d;")
        
        self.chat_history = []
        self.current_chat_session_id = None
        
        self.init_ui()

    def load_theme(self):
        theme_rel_path = "app/assets/theme_dark.qss" if self.is_dark_mode else "app/assets/theme_light.qss"
        theme_file = resource_path(theme_rel_path)
        try:
            with open(theme_file, "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            logger.error(f"Failed to load theme {theme_file}: {e}")

    def init_ui(self):
        # Main Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Header 
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(10, 10, 10, 10)
        
        # Logo
        self.lbl_logo = QLabel()
        logo_pix_path = resource_path("app/assets/logo.png")
        pix = QPixmap(logo_pix_path).scaled(38, 38, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.lbl_logo.setPixmap(pix)
        header_layout.addWidget(self.lbl_logo)
        
        title_lbl = QLabel("Cari Kitab")
        title_lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: #0d6efd; margin-left: 10px;")
        header_layout.addWidget(title_lbl)
        
        header_layout.addStretch()

        # ── Header Quick-Toggle Buttons ──────────────────────────────────────────
        # Language toggle button (ID / EN)
        self.btn_toggle_lang = QPushButton("🇮🇩 ID" if self.current_lang == 'id' else "🇬🇧 EN")
        self.btn_toggle_lang.setFixedWidth(70)
        self.btn_toggle_lang.setFixedHeight(32)
        self.btn_toggle_lang.setToolTip("Ganti Bahasa / Change Language (ID / EN)")
        self.btn_toggle_lang.setStyleSheet(
            "border: 1px solid #ced4da; border-radius: 16px; "
            "font-size: 12px; font-weight: bold; padding: 2px 8px;"
        )
        self.btn_toggle_lang.clicked.connect(self.toggle_lang_quick)
        header_layout.addWidget(self.btn_toggle_lang)

        # Theme toggle button (☀️ Light / 🌙 Dark)
        self.btn_toggle_theme = QPushButton("🌙 Dark" if self.is_dark_mode else "☀️ Light")
        self.btn_toggle_theme.setFixedWidth(80)
        self.btn_toggle_theme.setFixedHeight(32)
        self.btn_toggle_theme.setToolTip("Ganti Tema / Toggle Theme (Light / Dark)")
        self.btn_toggle_theme.setStyleSheet(
            "border: 1px solid #ced4da; border-radius: 16px; "
            "font-size: 12px; font-weight: bold; padding: 2px 8px;"
        )
        self.btn_toggle_theme.clicked.connect(self.toggle_theme_quick)
        header_layout.addWidget(self.btn_toggle_theme)
        # ─────────────────────────────────────────────────────────────────────────
        
        # Tabs
        self.tabs = QTabWidget()
        self.tab_search = QWidget()
        self.tab_split_tool = QWidget() # NEW General Split Tool
        self.tab_history = QWidget()
        self.tab_chat = QWidget()       # NEW AI Consultant
        self.tab_viewer = QWidget()     # NEW Viewer
        self.tab_setting = QWidget()    # NEW Setting Tab
        self.tab_help = QWidget()
        self.tab_about = QWidget()
        
        self.tabs.addTab(self.tab_search, "🔍 Search")
        self.tabs.addTab(self.tab_split_tool, "✂️ Split Tool")
        self.tabs.addTab(self.tab_chat, "🤖 AI Konsultan")
        self.tabs.addTab(self.tab_viewer, "📖 Viewer")
        self.tabs.addTab(self.tab_history, "📑 History")
        self.tabs.addTab(self.tab_setting, "⚙️ Setting")
        self.tabs.addTab(self.tab_help, "❓ Help")
        self.tabs.addTab(self.tab_about, "ℹ️ About")
        
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.tabs)
        
        # Bottom Status Bar
        status_bar_layout = QHBoxLayout()
        status_bar_layout.setContentsMargins(10, 0, 10, 10)
        status_bar_layout.addWidget(self.lbl_global_status)
        status_bar_layout.addWidget(self.progress_bar, stretch=1)
        main_layout.addLayout(status_bar_layout)

        self.setup_search_tab()
        self.setup_split_tool_tab()
        self.setup_history_tab()
        self.setup_chat_tab()
        self.setup_viewer_tab()
        self.setup_setting_tab()
        self.setup_help_tab()
        self.setup_about_tab()

    def setup_search_tab(self):
        layout = QVBoxLayout(self.tab_search)
        
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(800)
        self.search_timer.timeout.connect(self.do_search)
        
        # Search Bar Area
        search_layout = QHBoxLayout()
        
        # Search Source
        self.cb_source = QComboBox()
        self.cb_source.addItems(["Shamela (PDF/BOK)", "Global PDF (Archive/Drive)"])
        self.cb_source.setFixedWidth(180)
        
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Ketik judul kitab atau nama penulis dalam Indonesia/Arab...")
        self.txt_search.returnPressed.connect(self.do_search)
        
        self.btn_search = QPushButton("Search")
        self.btn_search.clicked.connect(self.do_search)
        
        search_layout.addWidget(self.cb_source)
        search_layout.addWidget(self.txt_search)
        search_layout.addWidget(self.btn_search)
        
        # Smart Search Integration Checkbox
        smart_layout = QHBoxLayout()
        self.chk_llm = QCheckBox("Aktifkan Smart Arabic Search")
        self.chk_llm.setToolTip("Keyword akan dinormalisasi ke bahasa Arab menggunakan Gemini")
        self.chk_llm.setChecked(True)
        
        self.chk_fast_mode = QCheckBox("Mode Cepat (Tanpa Transliterasi)")
        self.chk_fast_mode.setToolTip("Lewati proses transliterasi judul dan nama pengarang (lebih cepat)")
        self.chk_fast_mode.setChecked(False)
        
        self.lbl_llm_status = QLabel("Ready")
        self.lbl_llm_status.setStyleSheet("font-size: 11px; color: #6c757d;")
        self.lbl_llm_status.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        smart_layout.addWidget(self.chk_llm)
        smart_layout.addWidget(self.chk_fast_mode)
        smart_layout.addStretch()
        smart_layout.addWidget(self.lbl_llm_status)
        
        # Content Split Layout - Using QSplitter for manual resizing
        self.content_splitter = QSplitter(Qt.Horizontal)
        
        # Left: Search Results
        res_container = QWidget()
        res_layout = QVBoxLayout(res_container)
        res_layout.setContentsMargins(0, 0, 10, 0)
        
        self.lbl_status = QLabel("Ready.")
        self.lbl_status.setStyleSheet("color: #6c757d;")
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.setAlignment(Qt.AlignTop)
        scroll_area.setWidget(self.results_widget)
        
        self.download_items = {} 
        
        self.btn_load_more = QPushButton("Lihat 10 Hasil Berikutnya ⬇️")
        self.btn_load_more.setObjectName("btnSecondary")
        self.btn_load_more.setVisible(False)
        self.btn_load_more.clicked.connect(self.load_more_results)
        
        res_layout.addWidget(self.lbl_status)
        res_layout.addWidget(scroll_area)
        res_layout.addWidget(self.btn_load_more)
        
        # Right: Active Downloads
        down_container = QWidget()
        down_container.setMinimumWidth(300)
        down_layout = QVBoxLayout(down_container)
        down_layout.setContentsMargins(10, 0, 0, 0)
        
        self.lbl_active_downloads_title = QLabel("Aktif Downloads")
        self.lbl_active_downloads_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        down_scroll_area = QScrollArea()
        down_scroll_area.setWidgetResizable(True)
        self.downloads_widget = QWidget()
        self.downloads_layout = QVBoxLayout(self.downloads_widget)
        self.downloads_layout.setAlignment(Qt.AlignTop)
        down_scroll_area.setWidget(self.downloads_widget)
        
        down_layout.addWidget(self.lbl_active_downloads_title)
        down_layout.addWidget(down_scroll_area)
        
        self.content_splitter.addWidget(res_container)
        self.content_splitter.addWidget(down_container)
        
        # Set initial stretches (Results takes 70%, Downloads 30%)
        self.content_splitter.setStretchFactor(0, 7)
        self.content_splitter.setStretchFactor(1, 3)
        
        layout.setSpacing(10)
        
        # Add to main tab
        layout.addLayout(search_layout)
        layout.addLayout(smart_layout)
        layout.addWidget(self.content_splitter, stretch=1)

    def setup_split_tool_tab(self):
        layout = QVBoxLayout(self.tab_split_tool)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_msg = QLabel("<h2>✂️ General PDF Splitter</h2>Pilih file PDF mana saja dari komputer Anda untuk dipotong.")
        lbl_msg.setWordWrap(True)
        layout.addWidget(lbl_msg)
        
        # File selector
        file_layout = QHBoxLayout()
        self.txt_split_file = QLineEdit()
        self.txt_split_file.setPlaceholderText("Pilih file PDF...")
        self.txt_split_file.setReadOnly(True)
        btn_browse = QPushButton("📁 Pilih File")
        btn_browse.clicked.connect(self.choose_split_file)
        file_layout.addWidget(self.txt_split_file)
        file_layout.addWidget(btn_browse)
        layout.addLayout(file_layout)
        
        # File Info Frame (Hidden initially)
        self.frame_file_info = QFrame()
        self.frame_file_info.setObjectName("downloadItem") # Reuse style
        self.frame_file_info.setVisible(False)
        info_layout = QVBoxLayout(self.frame_file_info)
        self.lbl_file_details = QLabel("")
        self.lbl_file_details.setStyleSheet("font-size: 14px;")
        info_layout.addWidget(self.lbl_file_details)
        layout.addWidget(self.frame_file_info)
        
        # Split Options
        self.group_split = QWidget()
        self.group_split.setVisible(False)
        opt_layout = QVBoxLayout(self.group_split)
        
        self.rb_gen_pages = QRadioButton("Bagi berdasarkan jumlah HALAMAN (contoh: tiap 100 hal)")
        self.rb_gen_size = QRadioButton("Bagi berdasarkan ukuran SIZE MB (contoh: tiap 50 MB)")
        self.rb_gen_pages.setChecked(True)
        opt_layout.addWidget(self.rb_gen_pages)
        opt_layout.addWidget(self.rb_gen_size)
        
        val_layout = QHBoxLayout()
        val_layout.addWidget(QLabel("Nilai (Angka):"))
        self.input_gen_val = QSpinBox()
        self.input_gen_val.setRange(1, 1000000)
        self.input_gen_val.setValue(100)
        self.input_gen_val.setFixedWidth(120)
        val_layout.addWidget(self.input_gen_val)
        val_layout.addStretch()
        opt_layout.addLayout(val_layout)
        
        # Center the button instead of full width
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_run_gen_split = QPushButton("🚀 Mulai Proses Split")
        self.btn_run_gen_split.setFixedWidth(300)
        self.btn_run_gen_split.setStyleSheet("background-color: #0d6efd; color: white; font-weight: bold; min-height: 45px; border-radius: 8px;")
        self.btn_run_gen_split.clicked.connect(self.start_general_split)
        btn_layout.addWidget(self.btn_run_gen_split)
        btn_layout.addStretch()
        opt_layout.addLayout(btn_layout)
        
        layout.addWidget(self.group_split)
        layout.addStretch()

    def choose_split_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Pilih PDF", "", "PDF Files (*.pdf)")
        if file_path:
            self.txt_split_file.setText(file_path)
            try:
                import fitz
                doc = fitz.open(file_path)
                pages = doc.page_count
                size_mb = os.path.getsize(file_path) / (1024*1024)
                doc.close()
                
                self.lbl_file_details.setText(f"<b>File:</b> {os.path.basename(file_path)}<br>"
                                            f"📊 {pages} Halaman • 💾 {size_mb:.1f} MB")
                self.frame_file_info.setVisible(True)
                self.group_split.setVisible(True)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal membaca file: {e}")

    def start_general_split(self):
        pdf_path = self.txt_split_file.text()
        if not pdf_path: return
        
        s_type = "pages" if self.rb_gen_pages.isChecked() else "size"
        val = self.input_gen_val.value()
        
        # Reuse SplitWorker
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        # Reuse SplitWorker - FIXED ARGUMENT ORDER: (path, type, value)
        worker = SplitWorker(pdf_path, s_type, val)
        worker.finished.connect(lambda res: self.on_split_finished(os.path.basename(pdf_path), res))
        worker.error.connect(lambda err: self.on_search_error(f"Split Error: {err}"))
        worker.status_update.connect(self.lbl_global_status.setText)
        worker.start()
        
        # Disable button
        self.btn_run_gen_split.setEnabled(False)
        worker.finished.connect(lambda: self.btn_run_gen_split.setEnabled(True))
        
        if not hasattr(self, 'gen_split_workers'): self.gen_split_workers = []
        self.gen_split_workers.append(worker)

    def setup_chat_tab(self):
        layout = QVBoxLayout(self.tab_chat)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Splitter to separate Sidebar and Chat Area
        self.chat_splitter = QSplitter(Qt.Horizontal)
        
        # --- SIDEBAR (History) ---
        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("sidebarWidget")
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        
        self.btn_new_chat = QPushButton("➕ Percakapan Baru")
        self.btn_new_chat.setFixedHeight(40)
        self.btn_new_chat.setStyleSheet("background-color: #198754; color: white; font-weight: bold; border-radius: 5px;")
        self.btn_new_chat.clicked.connect(self.start_new_chat)
        
        sidebar_layout.addWidget(self.btn_new_chat)
        self.lbl_ai_history_title = QLabel("<b>Riwayat Obrolan:</b>")
        sidebar_layout.addWidget(self.lbl_ai_history_title)
        
        self.list_chat_history = QListWidget()
        self.list_chat_history.itemClicked.connect(self.on_chat_session_clicked)
        self.list_chat_history.itemClicked.connect(self.on_chat_session_clicked)
        sidebar_layout.addWidget(self.list_chat_history)
        
        # --- MAIN AREA (Conversation) ---
        main_chat_container = QWidget()
        main_chat_layout = QVBoxLayout(main_chat_container)
        main_chat_layout.setContentsMargins(15, 15, 15, 15)
        
        # Chat display
        self.chat_display = QTextBrowser()
        self.chat_display.setOpenExternalLinks(False)
        self.chat_display.setOpenLinks(False)
        self.chat_display.anchorClicked.connect(self.handle_chat_link)
        self.chat_display.setReadOnly(True)
        
        # Input area
        input_container = QWidget()
        input_inner_layout = QHBoxLayout(input_container)
        input_inner_layout.setContentsMargins(0, 0, 0, 0)
        
        self.txt_chat = QTextEdit()
        self.txt_chat.setPlaceholderText("Tanyakan sesuatu tentang kitab atau buku...")
        self.txt_chat.setFixedHeight(80)
        self.txt_chat.setStyleSheet("border: 1px solid #ced4da; border-radius: 8px; padding: 5px;")
        
        self.btn_send_chat = QPushButton("🚀 Kirim")
        self.btn_send_chat.setFixedWidth(100)
        self.btn_send_chat.setFixedHeight(80)
        self.btn_send_chat.setStyleSheet("background-color: #0d6efd; color: white; font-weight: bold; border-radius: 8px;")
        self.btn_send_chat.clicked.connect(self.send_chat_message)
        
        input_inner_layout.addWidget(self.txt_chat)
        input_inner_layout.addWidget(self.btn_send_chat)
        
        # Zoom toolbar for AI answers
        zoom_toolbar = QWidget()
        zoom_layout = QHBoxLayout(zoom_toolbar)
        zoom_layout.setContentsMargins(0, 0, 0, 5)
        zoom_layout.setSpacing(5)
        
        self.chat_font_size = 14  # Default font size
        
        btn_zoom_out = QPushButton("A−")
        btn_zoom_out.setFixedSize(36, 28)
        btn_zoom_out.setStyleSheet("font-size: 13px; font-weight: bold; border: 1px solid #ced4da; border-radius: 5px; background: transparent;")
        btn_zoom_out.setToolTip("Kecilkan huruf")
        btn_zoom_out.clicked.connect(lambda: self._zoom_chat(-1))
        
        self.lbl_zoom_level = QLabel("100%")
        self.lbl_zoom_level.setFixedWidth(45)
        self.lbl_zoom_level.setAlignment(Qt.AlignCenter)
        self.lbl_zoom_level.setStyleSheet("font-size: 12px; color: #888;")
        
        btn_zoom_in = QPushButton("A+")
        btn_zoom_in.setFixedSize(36, 28)
        btn_zoom_in.setStyleSheet("font-size: 15px; font-weight: bold; border: 1px solid #ced4da; border-radius: 5px; background: transparent;")
        btn_zoom_in.setToolTip("Besarkan huruf")
        btn_zoom_in.clicked.connect(lambda: self._zoom_chat(1))
        
        btn_zoom_reset = QPushButton("↺")
        btn_zoom_reset.setFixedSize(28, 28)
        btn_zoom_reset.setStyleSheet("font-size: 14px; border: 1px solid #ced4da; border-radius: 5px; background: transparent;")
        btn_zoom_reset.setToolTip("Reset ukuran huruf")
        btn_zoom_reset.clicked.connect(lambda: self._zoom_chat(0))
        
        zoom_layout.addStretch()
        zoom_layout.addWidget(btn_zoom_out)
        zoom_layout.addWidget(self.lbl_zoom_level)
        zoom_layout.addWidget(btn_zoom_in)
        zoom_layout.addWidget(btn_zoom_reset)
        
        main_chat_layout.addWidget(zoom_toolbar)
        main_chat_layout.addWidget(self.chat_display, stretch=1)
        main_chat_layout.addWidget(input_container)
        
        # Add to splitter
        self.chat_splitter.addWidget(sidebar_widget)
        self.chat_splitter.addWidget(main_chat_container)
        self.chat_splitter.setStretchFactor(1, 4) # Chat area is wider
        self.chat_splitter.setSizes([200, 600])
        
        layout.addWidget(self.chat_splitter)
        
        # Professional Alignment: Remove default document margin
        self.chat_display.document().setDocumentMargin(0)
        
        self.chat_history = []
        self.current_chat_session_id = None
        self.load_history_list()
        self.show_welcome_message()

    def _zoom_chat(self, direction):
        """Zoom in/out/reset font size di area jawaban AI."""
        if direction == 0:
            self.chat_font_size = 14  # Reset
        elif direction > 0:
            self.chat_font_size = min(self.chat_font_size + 2, 30)
        else:
            self.chat_font_size = max(self.chat_font_size - 2, 8)
        
        percent = round((self.chat_font_size / 14) * 100)
        self.lbl_zoom_level.setText(f"{percent}%")
        
        # Apply font size to chat display
        font = self.chat_display.font()
        font.setPointSize(self.chat_font_size)
        self.chat_display.setFont(font)
        self.chat_display.document().setDefaultFont(font)

    def start_new_chat(self):
        self.chat_history = []
        self.current_chat_session_id = None
        self.show_welcome_message()
        self.list_chat_history.clearSelection()

    def show_welcome_message(self):
        texts = UI_STRINGS.get(self.current_lang, UI_STRINGS['id'])
        welcome_html = f"""
        <div style="color: #3b82f6; font-family: 'Segoe UI', sans-serif; padding: 20px 10px;">
            <h2 style="margin-top: 0; color: #0d6efd;">{texts['ai_welcome_title']}</h2>
            <p style="font-size: 15px; line-height: 1.5; color: {'#e0e0e0' if self.is_dark_mode else '#212529'};">{texts['ai_welcome_desc']}</p>
            <div style="font-size: 14px; background-color: {'#2a2a2a' if self.is_dark_mode else '#f1f3f5'}; padding: 15px; border-radius: 8px; color: {'#cccccc' if self.is_dark_mode else '#495057'}; border: 1px solid {'#333' if self.is_dark_mode else '#dee2e6'};">
                <i style="color: #6c757d;">{texts['ai_welcome_tips']}</i>
            </div>
        </div>
        """
        self.chat_display.setHtml(welcome_html)

    def load_history_list(self):
        self.list_chat_history.clear()
        sessions = db.get_all_chat_sessions()
        for sess in sessions:
            title = sess.get('title', 'Unknown')
            # Strip any HTML tags from old titles
            import re as _re
            title = _re.sub(r'<[^>]+>', '', title).strip()
            # Extract date (ddmmyyyy)
            try:
                dt = datetime.strptime(sess.get('created_at', ''), "%Y-%m-%d %H:%M:%S")
                date_str = dt.strftime("%d%m%Y")
            except:
                date_str = ""
                
            item = QListWidgetItem(f"{title}\n({date_str})")
            item.setData(Qt.UserRole, sess.get('id'))
            self.list_chat_history.addItem(item)

    def on_chat_session_clicked(self, item):
        session_id = item.data(Qt.UserRole)
        sessions = db.get_all_chat_sessions()
        target = next((s for s in sessions if s['id'] == session_id), None)
        if target:
            self.current_chat_session_id = session_id
            try:
                self.chat_history = json.loads(target.get('messages_json', '[]'))
                self.refresh_chat_display()
            except Exception as e:
                logger.error(f"Failed to load session: {e}")

    def refresh_chat_display(self):
        full_html = ""
        # Themed colors for HTML
        user_color = "#3b82f6" if self.is_dark_mode else "#0d6efd"
        ai_bg = "#212121" if self.is_dark_mode else "#f1f3f5"
        ai_text = "#e0e0e0" if self.is_dark_mode else "#212529"
        text_color = "#e0e0e0" if self.is_dark_mode else "#333333"

        for item in self.chat_history:
            if item['role'] == 'user':
                full_html += f'<div style="margin-top: 20px; color: {user_color}; padding-left: 5px;"><b>👤 Anda:</b></div>'
                full_html += f'<div style="color: {text_color}; padding: 0 5px 15px 5px; font-size: 15px;">{item["text"]}</div>'
                full_html += f'<hr style="border:0; border-top: 1px solid {"#2d2d2d" if self.is_dark_mode else "#eeeeee"}; margin-bottom: 20px;">'
            else:
                ai_content = item.get("html", item.get("text", ""))
                # Modern bubble with cleaner padding
                full_html += f'<div style="background-color: {ai_bg}; padding: 20px; border-radius: 12px; color: {ai_text}; border: 1px solid {"#2d2d2d" if self.is_dark_mode else "#e0e4e8"}; font-size: 14px; line-height: 1.6;"><b>🤖 AI Konsultan:</b><br><br>{ai_content}</div><br>'
        
        if full_html:
            self.chat_display.setHtml(full_html)
            self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())
        else:
            self.show_welcome_message()

    def update_current_session(self):
        if not self.chat_history: return
        
        messages_json = json.dumps(self.chat_history, ensure_ascii=False)
        
        if self.current_chat_session_id is None:
            # Create new session
            # Title is first user question, limited length
            first_user_msg = next((m['text'] for m in self.chat_history if m['role'] == 'user'), "Percakapan Baru")
            # Strip HTML tags from title for clean sidebar display
            import re as _re
            clean_title = _re.sub(r'<[^>]+>', '', first_user_msg).strip()
            clean_title = clean_title.replace('\n', ' ').replace('\r', ' ')
            title = clean_title[:30] + "..." if len(clean_title) > 30 else clean_title
            self.current_chat_session_id = db.add_chat_session(title, messages_json)
            self.load_history_list()
        else:
            # Update existing
            db.update_chat_session(self.current_chat_session_id, messages_json)

    def handle_chat_link(self, url):
        link = url.toString()
        if link.startswith("search:"):
            from urllib.parse import unquote
            import re
            keyword = unquote(link.split(":", 1)[1].strip())
            
            # Bugfix: Jika AI memasukkan keseluruhan teks "Latin (Arab)" ke dalam URL, kita ekstrak Arab-nya saja.
            arabic_matches = re.findall(r'[\u0600-\u06FF\s]+', keyword)
            if arabic_matches:
                # Pilih potongan bahasa arab terpanjang yang didapat
                keyword = max(arabic_matches, key=len).strip()
                
            # Set search keyword
            self.txt_search.setText(keyword)
            # Switch to search tab
            self.tabs.setCurrentIndex(0)
        else:
            # Open standard links
            import webbrowser
            webbrowser.open(link)

    def send_chat_message(self, override_prompt=None, display_text=None, metadata_header=None):
        msg = display_text if display_text else self.txt_chat.toPlainText().strip()
        if not msg and not override_prompt:
            return

        # Prepare for UI
        self.chat_history.append({"role": "user", "text": msg})
        self.refresh_chat_display()
        self.txt_chat.clear()

        # Final prompt for model
        final_prompt = override_prompt if override_prompt else msg
        
        # Build history for context
        llm_history = []
        for item in self.chat_history[:-1]:
            if item['role'] == 'user':
                llm_history.append({"user": item['text'], "ai": ""})
            elif llm_history:
                llm_history[-1]["ai"] = item.get("text", item.get("html", ""))

        image_paths = getattr(self, 'current_vision_images', [])
        # Only use metadata if this was triggered from a specific book item
        metadata_to_send = metadata_header if metadata_header else getattr(self, 'current_vision_metadata', '')
        
        worker = ChatWorker(msg, llm_history, image_paths=image_paths, metadata_header=metadata_to_send)
        # Clear it so a normal message doesn't reuse it
        self.current_vision_images = []
        self.current_vision_metadata = ''
        
        worker.response_ready.connect(self.on_chat_response)
        worker.error.connect(lambda err: QMessageBox.warning(self, "AI Error", f"{err}"))
        worker.status_update.connect(self.lbl_global_status.setText)
        worker.start()
        
        self.lbl_global_status.setText("🤖 AI sedang berpikir...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        if not hasattr(self, 'chat_workers'): self.chat_workers = []
        self.chat_workers.append(worker)
        
        self.update_current_session()
        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())

    def on_chat_response(self, html):
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        self.lbl_global_status.setText("Ready.")
        
        current_html = self.chat_display.toHtml()
        ai_html = f'<div style="margin-top: 5px; background-color: #f1f3f5; padding: 15px; border-radius: 8px; color: #212529;"><b>🤖 AI Konsultan:</b><br>{html}</div><br>'
        self.chat_display.setHtml(current_html + ai_html)
        
        # Save to history
        self.chat_history.append({"role": "ai", "html": html})
        if len(self.chat_history) > 60: # Keep last 30 rounds
            self.chat_history = self.chat_history[-60:]
            
        self.update_current_session()
        
        # Scroll to bottom
        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())

    def setup_viewer_tab(self):
        layout = QVBoxLayout(self.tab_viewer)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Toolbar
        toolbar = QHBoxLayout()
        self.btn_viewer_open = QPushButton("📂 Buka Manual")
        self.btn_viewer_open.clicked.connect(self.viewer_open_dialog)
        self.btn_viewer_open.setFixedWidth(150)
        self.lbl_viewer_title = QLabel("")
        self.lbl_viewer_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #0d6efd;")
        
        self.btn_toggle_sbs = QPushButton("📝 Mode Terjemahan")
        self.btn_toggle_sbs.setCheckable(True)
        self.btn_toggle_sbs.clicked.connect(self.toggle_side_by_side)
        self.btn_toggle_sbs.setEnabled(False)
        
        self.btn_toolbar_copy = QPushButton("📋 Salin Teks Seleksi")
        self.btn_toolbar_copy.clicked.connect(self.toolbar_copy_selected)
        self.btn_toolbar_copy.setEnabled(False)
        
        self.btn_toolbar_trans = QPushButton("🌍 Terjemahkan Teks Seleksi")
        self.btn_toolbar_trans.setStyleSheet("background-color: #0d6efd; color: white; font-weight: bold;")
        self.btn_toolbar_trans.clicked.connect(self.toolbar_translate_selected)
        self.btn_toolbar_trans.setEnabled(False)
        
        toolbar.addWidget(self.btn_viewer_open)
        toolbar.addWidget(self.lbl_viewer_title)
        toolbar.addStretch()
        toolbar.addWidget(self.btn_toolbar_copy)
        toolbar.addWidget(self.btn_toolbar_trans)
        toolbar.addWidget(self.btn_toggle_sbs)
        layout.addLayout(toolbar)
        
        self.viewer_main_splitter = QSplitter(Qt.Horizontal)
        
        from PySide6.QtWidgets import QStackedWidget
        self.viewer_stack = QStackedWidget()
        
        # Page 0: Empty
        self.lbl_viewer_empty = QLabel("Silakan pilih file dari tab Riwayat atau tekan Buka untuk membaca file.")
        self.lbl_viewer_empty.setAlignment(Qt.AlignCenter)
        self.lbl_viewer_empty.setStyleSheet("color: #6c757d; font-size: 14px;")
        self.viewer_stack.addWidget(self.lbl_viewer_empty)
        
        # Custom Widgets for Context Menu
        class CustomWebEngineView(QWebEngineView if HAS_WEBENGINE else QLabel):
            def __init__(self, main_win):
                super().__init__()
                self.main_win = main_win
                if HAS_WEBENGINE:
                    self.setContextMenuPolicy(Qt.CustomContextMenu)
                    self.customContextMenuRequested.connect(self._custom_menu)
                    
            def _custom_menu(self, pos):
                # We use standard menu instead of rebuilding to preserve native PDF functions
                menu = self.createStandardContextMenu()
                menu.addSeparator()
                act_trans = menu.addAction("🌍 Terjemahkan Teks... (via Clipboard)")
                
                action = menu.exec(self.mapToGlobal(pos))
                if action == act_trans:
                    # WebEngine PDF selection is isolated. Force copy to clipboard first
                    self.triggerPageAction(self.page().WebAction.Copy)
                    from PySide6.QtCore import QTimer
                    QTimer.singleShot(200, self._open_trans)
                    
            def _open_trans(self):
                clip_text = QApplication.clipboard().text().strip()
                if clip_text:
                    self.main_win.open_translate_popup(clip_text)
                else:
                    QMessageBox.warning(self.main_win, "Kosong", "Gagal meraih teks. Mohon Blok teks lalu pilih 'Copy' (atau Ctrl+C) terlebih dahulu sebelum menekan Translate.")

        class CustomTextBrowser(QTextBrowser):
            def __init__(self, main_win):
                super().__init__()
                self.main_win = main_win
                self.setContextMenuPolicy(Qt.CustomContextMenu)
                self.customContextMenuRequested.connect(self._custom_menu)
                
            def _custom_menu(self, pos):
                menu = self.createStandardContextMenu()
                sel = self.textCursor().selectedText()
                if sel:
                    menu.addSeparator()
                    act_trans = menu.addAction("🌍 Terjemah Teks Ini (Popup)")
                    action = menu.exec(self.mapToGlobal(pos))
                    if action == act_trans:
                        self.main_win.open_translate_popup(sel)
                else:
                    menu.exec(self.mapToGlobal(pos))

        # Page 1: WebEngine (PDF)
        if HAS_WEBENGINE:
            self.viewer_web = CustomWebEngineView(self)
            self.viewer_web.settings().setAttribute(self.viewer_web.settings().WebAttribute.PluginsEnabled, True)
            self.viewer_web.settings().setAttribute(self.viewer_web.settings().WebAttribute.PdfViewerEnabled, True)
            self.viewer_stack.addWidget(self.viewer_web)
        else:
            lbl_no_web = QLabel("PySide6-WebEngine tidak terinstal. PDF tidak dapat dilihat secara internal.")
            lbl_no_web.setAlignment(Qt.AlignCenter)
            self.viewer_stack.addWidget(lbl_no_web)
            self.viewer_web = None
            
        # Page 2: TextBrowser (TXT/EPUB)
        self.viewer_text = CustomTextBrowser(self)
        self.viewer_text.setReadOnly(True)
        self.viewer_text.setOpenExternalLinks(True)
        self.viewer_stack.addWidget(self.viewer_text)
        
        self.viewer_main_splitter.addWidget(self.viewer_stack)
        
        # --- Right Panel (Side-by-Side Translate) ---
        self.sbs_panel = QWidget()
        sbs_layout = QVBoxLayout(self.sbs_panel)
        sbs_layout.setContentsMargins(0,0,0,0)
        
        sbs_toolbar = QHBoxLayout()
        sbs_toolbar.addWidget(QLabel("Halaman:"))
        self.sbs_page_spinner = QSpinBox()
        self.sbs_page_spinner.setMinimum(1)
        self.sbs_page_spinner.setMaximum(9999)
        self.sbs_page_spinner.valueChanged.connect(self.sync_pdf_to_spinner)
        
        self.cb_sbs_lang = QComboBox()
        self.cb_sbs_lang.addItems(["Indonesia", "Inggris", "Arab"])
        
        self.btn_sbs_translate = QPushButton("🚀 Terjemahkan")
        self.btn_sbs_translate.clicked.connect(self.do_sbs_translate)
        
        self.btn_sbs_save = QPushButton("💾 Simpan")
        self.btn_sbs_save.clicked.connect(self.save_sbs_translasi)
        
        self.sbs_font_size = 12
        btn_sbs_zoom_out = QPushButton("-")
        btn_sbs_zoom_out.setFixedSize(30, 30)
        btn_sbs_zoom_out.setStyleSheet("font-weight: bold; font-size: 18px; padding: 0px; color: white;")
        btn_sbs_zoom_out.clicked.connect(lambda: self.change_sbs_font_size(-2))
        btn_sbs_zoom_in = QPushButton("+")
        btn_sbs_zoom_in.setFixedSize(30, 30)
        btn_sbs_zoom_in.setStyleSheet("font-weight: bold; font-size: 18px; padding: 0px; color: white;")
        btn_sbs_zoom_in.clicked.connect(lambda: self.change_sbs_font_size(2))
        self.lbl_sbs_zoom = QLabel("100%")
        
        sbs_toolbar.addWidget(self.sbs_page_spinner)
        sbs_toolbar.addWidget(self.cb_sbs_lang)
        sbs_toolbar.addWidget(self.btn_sbs_translate)
        sbs_toolbar.addStretch()
        sbs_toolbar.addWidget(btn_sbs_zoom_out)
        sbs_toolbar.addWidget(self.lbl_sbs_zoom)
        sbs_toolbar.addWidget(btn_sbs_zoom_in)
        sbs_toolbar.addSpacing(10)
        sbs_toolbar.addWidget(self.btn_sbs_save)
        
        self.sbs_text = QTextEdit()
        self.sbs_text.setPlaceholderText("Hasil terjemahan halaman akan muncul di sini...\n\n(Hanya mengambil data ketika tombol Terjemahkan diklik guna menghemat kuota API).")
        
        sbs_layout.addLayout(sbs_toolbar)
        sbs_layout.addWidget(self.sbs_text)
        
        self.viewer_main_splitter.addWidget(self.sbs_panel)
        self.sbs_panel.hide() # Hidden by default
        
        self.viewer_main_splitter.setStretchFactor(0, 1)
        self.viewer_main_splitter.setStretchFactor(1, 1)
        layout.addWidget(self.viewer_main_splitter)
        
        self.current_viewer_file = None

    def change_sbs_font_size(self, delta):
        self.sbs_font_size = max(8, min(72, self.sbs_font_size + delta))
        f = self.sbs_text.font()
        f.setPointSize(self.sbs_font_size)
        self.sbs_text.setFont(f)
        percent = int((self.sbs_font_size / 12) * 100)
        self.lbl_sbs_zoom.setText(f"{percent}%")
        
    def sync_pdf_to_spinner(self, page_num):
        if hasattr(self, 'viewer_web') and self.viewer_web and self.viewer_stack.currentIndex() == 1:
            # Memanipulasi URL fragment untuk melompat ke halaman spesifik tanpa memuat ulang PDF
            self.viewer_web.page().runJavaScript(f"window.location.hash = 'page={page_num}';")

    def toolbar_copy_selected(self):
        from PySide6.QtWebEngineCore import QWebEnginePage
        if hasattr(self, 'viewer_web') and self.viewer_web and self.viewer_stack.currentIndex() == 1:
            self.viewer_web.triggerPageAction(QWebEnginePage.WebAction.Copy)
            QMessageBox.information(self, "Tersalin", "Teks pada PDF yang diblok telah disalin ke Clipboard sistem Anda.")
        elif self.viewer_stack.currentIndex() == 2:
            self.viewer_text.copy()
            QMessageBox.information(self, "Tersalin", "Teks yang diblok telah disalin ke Clipboard sistem Anda.")

    def toolbar_translate_selected(self):
        from PySide6.QtWebEngineCore import QWebEnginePage
        if hasattr(self, 'viewer_web') and self.viewer_web and self.viewer_stack.currentIndex() == 1:
            self.viewer_web.triggerPageAction(QWebEnginePage.WebAction.Copy)
        elif self.viewer_stack.currentIndex() == 2:
            self.viewer_text.copy()
            
        from PySide6.QtCore import QTimer
        QTimer.singleShot(300, self._open_translate_from_clipboard)
        
    def _open_translate_from_clipboard(self):
        text = QApplication.clipboard().text().strip()
        if text:
            # Tidak diclear otomatis agar user bs memutuskannya sendiri
            self.open_translate_popup(text)
        else:
            QMessageBox.warning(self, "Teks Kosong", "Pastikan Anda sudah menge-blok teks di PDF terlebih dahulu sebelum mengklik tombol Terjemahkan Teks Seleksi!")

    def open_translate_popup(self, text):
        popup = TranslatePopupDialog(text, self)
        popup.exec()
        
    def toggle_side_by_side(self):
        if self.btn_toggle_sbs.isChecked():
            self.sbs_panel.show()
        else:
            self.sbs_panel.hide()
            
    def do_sbs_translate(self):
        if not self.current_viewer_file: return
        page_num = self.sbs_page_spinner.value()
        
        extracted_text = ""
        ext = self.current_viewer_file.lower().split('.')[-1]
        
        if ext == 'pdf':
            try:
                import fitz
                doc = fitz.open(self.current_viewer_file)
                if page_num > doc.page_count:
                    QMessageBox.warning(self, "Error", f"PDF ini hanya memiliki {doc.page_count} halaman.")
                    doc.close()
                    return
                page = doc[page_num - 1]
                extracted_text = page.get_text()
                doc.close()
            except Exception as e:
                QMessageBox.warning(self, "Error PDF", f"Gagal membaca teks PDF:\n{e}")
                return
        else:
            QMessageBox.information(self, "Info", "Sistem terjemahan per-halaman saat ini dirancang optimal untuk file PDF. Untuk TXT/EPUB, silakan blok teks langsung pada dokumen lalu klik kanan -> Terjemahkan (Popup).")
            return
            
        if not extracted_text.strip():
            QMessageBox.information(self, "Kosong", f"Tidak ada teks yang dapat diekstrak pada halaman {page_num} (mungkin hasil scan murni tanpa metadata teks).")
            return
            
        self.btn_sbs_translate.setEnabled(False)
        self.sbs_text.setPlainText("⏳ Sedang memproses terjemahan halaman...")
        lang = self.cb_sbs_lang.currentText()
        
        if hasattr(self, 'sbs_worker') and self.sbs_worker:
            self.sbs_worker.terminate()
            
        self.sbs_worker = TranslateWorker(extracted_text, lang)
        self.sbs_worker.response_ready.connect(self.on_sbs_success)
        self.sbs_worker.error.connect(lambda err: self.sbs_text.setPlainText(f"Error: {err}"))
        self.sbs_worker.finished.connect(lambda: self.btn_sbs_translate.setEnabled(True))
        self.sbs_worker.start()
        
    def on_sbs_success(self, text):
        lang = self.cb_sbs_lang.currentText().lower()
        if 'arab' in lang:
            self.sbs_text.setLayoutDirection(Qt.RightToLeft)
            self.sbs_text.setAlignment(Qt.AlignRight)
        else:
            self.sbs_text.setLayoutDirection(Qt.LeftToRight)
            self.sbs_text.setAlignment(Qt.AlignLeft)
        self.sbs_text.setPlainText(text)
        
    def save_sbs_translasi(self):
        text = self.sbs_text.toPlainText()
        if not text: return
        path, _ = QFileDialog.getSaveFileName(self, "Simpan Terjemahan", get_downloads_dir(), "Word Document (*.docx);;Text Files (*.txt)")
        if not path: return
        
        import os
        try:
            if path.endswith('.docx'):
                import docx
                doc = docx.Document()
                doc.add_paragraph(f"Terjemahan File: {os.path.basename(self.current_viewer_file)}")
                doc.add_paragraph(f"Halaman: {self.sbs_page_spinner.value()}")
                doc.add_paragraph("")
                doc.add_paragraph(text)
                doc.save(path)
            else:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(f"Terjemahan File: {os.path.basename(self.current_viewer_file)}\nHalaman: {self.sbs_page_spinner.value()}\n\n{text}")
            QMessageBox.information(self, "Sukses", "Terjemahan berhasil disimpan!")
        except ImportError:
            QMessageBox.warning(self, "Error", "Modul python-docx belum terinstal. Jalankan instalasi dari terminal.")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def viewer_open_dialog(self):
        path, _ = QFileDialog.getOpenFileName(self, "Buka File", get_downloads_dir(), "Supported Files (*.pdf *.txt *.epub *.pub);;All Files (*.*)")
        if path:
            self.open_in_viewer(path)

    def open_in_viewer(self, file_path):
        import os
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "Error", f"File tidak ditemukan:\n{file_path}")
            return
            
        self.current_viewer_file = file_path
        self.btn_toggle_sbs.setEnabled(True)
        self.btn_toolbar_copy.setEnabled(True)
        self.btn_toolbar_trans.setEnabled(True)
        self.tabs.setCurrentWidget(self.tab_viewer)
        filename = os.path.basename(file_path)
        self.lbl_viewer_title.setText(filename)
        
        ext = filename.lower().split('.')[-1]
        
        if ext == 'pdf':
            if HAS_WEBENGINE and self.viewer_web:
                self.viewer_web.setUrl(QUrl.fromLocalFile(file_path))
                self.viewer_stack.setCurrentIndex(1)
            else:
                QMessageBox.warning(self, "Viewer Diarahkan", "Penampil internal tidak tersedia. File akan dibuka oleh sistem.")
                if os.name == 'nt': os.startfile(file_path)
                
        elif ext == 'txt':
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.viewer_text.setPlainText(content)
                self.viewer_stack.setCurrentIndex(2)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal membaca TXT:\n{e}")
                
        elif ext in ['epub', 'pub']:
            if not HAS_EBOOKLIB:
                QMessageBox.warning(self, "Viewer Dibatasi", "Library ebooklib tidak terinstal. Buka dengan sistem.")
                if os.name == 'nt': os.startfile(file_path)
                return
            try:
                self.lbl_global_status.setText("Memuat EPUB...")
                QApplication.processEvents()
                from bs4 import BeautifulSoup
                from ebooklib import epub
                import ebooklib
                book = epub.read_epub(file_path)
                full_html = ""
                for item in book.get_items():
                    if item.get_type() == ebooklib.ITEM_DOCUMENT:
                        html_content = item.get_content().decode('utf-8')
                        soup = BeautifulSoup(html_content, 'html.parser')
                        body = soup.find('body')
                        if body:
                            full_html += str(body) + "<br><hr><br>"
                self.viewer_text.setHtml(full_html)
                self.viewer_stack.setCurrentIndex(2)
                self.lbl_global_status.setText("Ready.")
            except Exception as e:
                logger.error(f"Failed to load EPUB: {e}")
                QMessageBox.warning(self, "Error", f"Gagal membaca EPUB:\n{e}")
                if os.name == 'nt': os.startfile(file_path)
        else:
            QMessageBox.information(self, "Info", "Dibuka menggunakan eksternal.")
            if os.name == 'nt': os.startfile(file_path)

    def setup_history_tab(self):
        layout = QVBoxLayout(self.tab_history)
        
        top_layout = QHBoxLayout()
        btn_refresh = QPushButton("🔄 Refresh")
        btn_refresh.setObjectName("btnSecondary")
        btn_refresh.clicked.connect(self.load_history)
        
        btn_open_folder = QPushButton("📂 Open Download Folder")
        btn_open_folder.clicked.connect(self.open_downloads_folder)
        
        top_layout.addWidget(btn_refresh)
        top_layout.addStretch()
        top_layout.addWidget(btn_open_folder)
        
        self.table_history = QTableWidget()
        self.table_history.setColumnCount(5)
        self.table_history.setHorizontalHeaderLabels(["Judul", "Penulis", "Waktu", "Status", "Lokasi"])
        self.table_history.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_history.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_history.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_history.itemDoubleClicked.connect(self.on_history_double_clicked)
        
        layout.addLayout(top_layout)
        layout.addWidget(self.table_history)
        
    def on_history_double_clicked(self, item):
        row = item.row()
        file_path_item = self.table_history.item(row, 4)
        if file_path_item:
            path = file_path_item.text()
            if path and os.path.exists(path):
                self.open_in_viewer(path)
            else:
                QMessageBox.warning(self, "Error", "File tidak ditemukan di sistem.")
        
    def load_history(self):
        history_path = get_writable_path("download_history.json")
        if not os.path.exists(history_path): return
        
        try:
            with open(history_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            self.table_history.setRowCount(0)
            for item in reversed(history):
                row = self.table_history.rowCount()
                self.table_history.insertRow(row)
                
                self.table_history.setItem(row, 0, QTableWidgetItem(item.get('judul_arab', item.get('judul_latin', 'Unknown'))))
                self.table_history.setItem(row, 1, QTableWidgetItem(item.get('penulis_arab', item.get('penulis_latin', 'Unknown'))))
                self.table_history.setItem(row, 2, QTableWidgetItem(item.get('timestamp', '')))
                self.table_history.setItem(row, 3, QTableWidgetItem(item.get('status', 'Completed')))
                self.table_history.setItem(row, 4, QTableWidgetItem(item.get('file_path', '')))
        except Exception as e:
            logger.error(f"Failed to load history: {e}")
        
    def setup_about_tab(self):
        layout = QVBoxLayout(self.tab_about)
        layout.setContentsMargins(30, 20, 30, 20)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        container = QWidget()
        content_layout = QVBoxLayout(container)
        content_layout.setSpacing(20)
        
        # Logo & App Name
        header_layout = QHBoxLayout()
        lbl_big_logo = QLabel()
        pix = QPixmap("app/assets/logo.png").scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        lbl_big_logo.setPixmap(pix)
        header_layout.addWidget(lbl_big_logo)
        
        title_vbox = QVBoxLayout()
        lbl_title = QLabel("Cari Kitab")
        lbl_title.setStyleSheet("font-size: 32px; font-weight: bold; color: #0d6efd;")
        lbl_version = QLabel(f"Digital Library Searcher - Version {APP_VERSION}")
        lbl_version.setStyleSheet("font-size: 14px; color: #6c757d;")
        title_vbox.addWidget(lbl_title)
        title_vbox.addWidget(lbl_version)
        header_layout.addLayout(title_vbox)
        header_layout.addStretch()
        
        # Sections
        texts = UI_STRINGS.get(self.current_lang, UI_STRINGS['id'])
        self.lbl_about_content = QLabel(texts['about_html'])
        self.lbl_about_content.setWordWrap(True)
        self.lbl_about_content.setOpenExternalLinks(True)
        self.lbl_about_content.setTextInteractionFlags(Qt.LinksAccessibleByMouse | Qt.TextSelectableByMouse)
        
        content_layout.addLayout(header_layout)
        content_layout.addWidget(self.lbl_about_content)
        content_layout.addStretch()
        
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
    def setup_setting_tab(self):
        layout = QVBoxLayout(self.tab_setting)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        texts = UI_STRINGS.get(self.current_lang, UI_STRINGS['id'])
        
        # Title
        self.lbl_setting_main_title = QLabel(f"<h2>⚙️ {texts['tab_setting']}</h2>")
        layout.addWidget(self.lbl_setting_main_title)
        
        # Download Folder Section
        dl_group = QFrame()
        dl_group.setFrameStyle(QFrame.StyledPanel)
        dl_group.setObjectName("settingGroup")
        dl_layout = QVBoxLayout(dl_group)
        self.lbl_setting_dl_folder = QLabel(f"<b>{texts['setting_dl_folder']}</b>")
        dl_layout.addWidget(self.lbl_setting_dl_folder)
        self.lbl_setting_dl_desc = QLabel(texts['setting_dl_desc'])
        dl_layout.addWidget(self.lbl_setting_dl_desc)
        
        path_layout = QHBoxLayout()
        self.txt_download_path = QLineEdit()
        self.txt_download_path.setPlaceholderText(texts['setting_dl_placeholder'])
        self.txt_download_path.setText(os.environ.get('DOWNLOAD_DIR', ''))
        
        self.btn_browse_dl = QPushButton(texts['setting_browse'])
        self.btn_browse_dl.setFixedWidth(100)
        self.btn_browse_dl.clicked.connect(self.browse_download_folder)
        
        path_layout.addWidget(self.txt_download_path)
        path_layout.addWidget(self.btn_browse_dl)
        dl_layout.addLayout(path_layout)
        layout.addWidget(dl_group)

        # Settings Group (Theme & Language)
        settings_row = QHBoxLayout()
        
        # Theme Section
        theme_group = QFrame()
        theme_group.setFrameStyle(QFrame.StyledPanel)
        theme_group.setObjectName("settingGroup")
        theme_layout = QVBoxLayout(theme_group)
        self.lbl_setting_theme = QLabel(f"<b>{texts['setting_theme']}</b>")
        theme_layout.addWidget(self.lbl_setting_theme)
        
        self.rb_theme_light = QRadioButton("Terang (Light)" if self.current_lang == 'id' else "Light Mode")
        self.rb_theme_dark = QRadioButton("Gelap (Dark)" if self.current_lang == 'id' else "Dark Mode")
        if self.is_dark_mode: self.rb_theme_dark.setChecked(True)
        else: self.rb_theme_light.setChecked(True)
        
        self.rb_theme_light.toggled.connect(self.update_theme_from_radio)
        
        theme_layout.addWidget(self.rb_theme_light)
        theme_layout.addWidget(self.rb_theme_dark)
        
        # Language Section
        lang_group = QFrame()
        lang_group.setFrameStyle(QFrame.StyledPanel)
        lang_group.setObjectName("settingGroup")
        lang_layout = QVBoxLayout(lang_group)
        self.lbl_setting_lang = QLabel(f"<b>{texts['setting_lang']}</b>")
        lang_layout.addWidget(self.lbl_setting_lang)
        
        self.rb_lang_id = QRadioButton("Indonesia")
        self.rb_lang_en = QRadioButton("English")
        
        if self.current_lang == 'en': self.rb_lang_en.setChecked(True)
        else: self.rb_lang_id.setChecked(True)
        
        self.rb_lang_id.toggled.connect(self.change_language)
        
        lang_layout.addWidget(self.rb_lang_id)
        lang_layout.addWidget(self.rb_lang_en)
        
        settings_row.addWidget(theme_group)
        settings_row.addWidget(lang_group)
        layout.addLayout(settings_row)

        # Gemini API Keys Section
        key_group = QFrame()
        key_group.setFrameStyle(QFrame.StyledPanel)
        key_group.setObjectName("settingGroup")
        key_layout = QVBoxLayout(key_group)
        self.lbl_setting_api_title = QLabel(f"<b>{texts['setting_api_title']}</b>")
        key_layout.addWidget(self.lbl_setting_api_title)
        self.lbl_setting_api_desc = QLabel(texts['setting_api_desc'])
        key_layout.addWidget(self.lbl_setting_api_desc)
        
        # Load keys from session
        from app.services.gemini_search_assistant import global_rotator
        current_keys = ",".join(global_rotator.keys)
        
        key_input_layout = QHBoxLayout()
        self.txt_keys_tab = QLineEdit() 
        self.txt_keys_tab.setPlaceholderText(texts['setting_keys_placeholder'])
        self.txt_keys_tab.setText(current_keys)
        self.txt_keys_tab.setEchoMode(QLineEdit.Password)
        self.txt_keys_tab.setFixedHeight(40)
        
        self.btn_toggle_keys = QPushButton("👁️")
        self.btn_toggle_keys.setFixedWidth(40)
        self.btn_toggle_keys.setFixedHeight(40)
        self.btn_toggle_keys.setCheckable(True)
        self.btn_toggle_keys.clicked.connect(self.toggle_api_key_visibility)
        
        key_input_layout.addWidget(self.txt_keys_tab)
        key_input_layout.addWidget(self.btn_toggle_keys)
        key_layout.addLayout(key_input_layout)
        layout.addWidget(key_group)

        # Save Button
        save_btn_layout = QHBoxLayout()
        save_btn_layout.addStretch()
        self.btn_save_settings = QPushButton(texts['btn_save_settings'])
        self.btn_save_settings.setFixedWidth(300)
        self.btn_save_settings.setFixedHeight(45)
        self.btn_save_settings.setStyleSheet("background-color: #0d6efd; color: white; font-weight: bold; border-radius: 8px;")
        self.btn_save_settings.clicked.connect(self.save_settings_from_tab)
        save_btn_layout.addWidget(self.btn_save_settings)
        save_btn_layout.addStretch()
        layout.addLayout(save_btn_layout)
        
        # Search Driver Section
        driver_group = QFrame()
        driver_group.setFrameStyle(QFrame.StyledPanel)
        driver_group.setObjectName("settingGroup")
        driver_layout = QVBoxLayout(driver_group)
        self.lbl_setting_repair_title = QLabel(f"<b>{texts['setting_repair_title']}</b>")
        driver_layout.addWidget(self.lbl_setting_repair_title)
        self.lbl_setting_repair_desc = QLabel(texts['setting_repair_desc'])
        driver_layout.addWidget(self.lbl_setting_repair_desc)
        
        self.btn_repair_search = QPushButton(texts['setting_repair_btn'])
        self.btn_repair_search.setFixedWidth(300)
        self.btn_repair_search.setStyleSheet("background-color: #198754; color: white; font-weight: bold;")
        self.btn_repair_search.clicked.connect(self.repair_search_drivers)
        driver_layout.addWidget(self.btn_repair_search)
        layout.addWidget(driver_group)
        
        layout.addStretch()

    def setup_help_tab(self):
        layout = QVBoxLayout(self.tab_help)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Help display using QTextBrowser for link support
        self.help_display = QTextBrowser()
        self.help_display.setOpenExternalLinks(False)
        self.help_display.setOpenLinks(False)
        texts = UI_STRINGS.get(self.current_lang, UI_STRINGS['id'])
        self.help_display.setHtml(texts['help_html'])
        self.help_display.anchorClicked.connect(self.handle_chat_link)
        self.help_display.setStyleSheet("background-color: white; border-radius: 8px; padding: 15px;")
        
        layout.addWidget(self.help_display)

    def browse_download_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Pilih Folder Download")
        if folder:
            self.txt_download_path.setText(folder)

    def repair_search_drivers(self):
        self.btn_repair_search.setEnabled(False)
        self.btn_repair_search.setText("⌛ Mengunduh Driver (Mungkin lama)...")
        self.lbl_global_status.setText("Sedang mengunduh driver Playwright (Chromium)...")
        
        # Run in a thread to keep UI alive
        class RepairWorker(QThread):
            done = Signal(bool)
            def run(self):
                # We need to run 'playwright install chromium'
                # In frozen mode, using 'python -m playwright' might not work directly.
                # Let's try to find the 'playwright' module path and use it.
                import subprocess
                import os
                import sys
                from app.core.playwright_scraper import get_playwright_browsers_path
                
                try:
                    # Point to user appdata
                    env = os.environ.copy()
                    env["PLAYWRIGHT_BROWSERS_PATH"] = get_playwright_browsers_path()
                    
                    # Try direct call if possible, or via python
                    # In frozen mode, sys.executable might point to the executable itself,
                    # and -m playwright might not work.
                    # We need to ensure playwright is installed and its CLI is accessible.
                    # The `playwright install` command is usually available if playwright is installed.
                    
                    # Attempt to run playwright install directly
                    # This assumes 'playwright' command is in PATH or accessible.
                    # For frozen apps, it's better to rely on the python module.
                    
                    # Check if running in a frozen environment
                    if getattr(sys, 'frozen', False):
                        # In a frozen environment (e.g., PyInstaller)
                        # The playwright module might be bundled.
                        # We need to find the playwright CLI entry point.
                        # A common way is to call it via the bundled Python interpreter.
                        # However, PyInstaller often bundles the 'playwright' package
                        # and its 'install' command might not be directly exposed as a CLI.
                        # The most reliable way is to ensure `playwright install` is run
                        # during the build process or to manually manage browser binaries.
                        # For simplicity and common cases, we'll try the standard `python -m playwright`
                        # which often works even in frozen apps if the environment is set up correctly.
                        # If it fails, the user will get an error message.
                        
                        # For PyInstaller, the `playwright` package's `__main__.py`
                        # should be executable via `sys.executable -m playwright`.
                        cmd = [sys.executable, "-m", "playwright", "install", "chromium"]
                    else:
                        # Not frozen, standard Python environment
                        cmd = [sys.executable, "-m", "playwright", "install", "chromium"]

                    logger.info(f"Running Playwright install command: {' '.join(cmd)}")
                    process = subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
                    logger.info(f"Playwright install stdout: {process.stdout}")
                    if process.stderr:
                        logger.warning(f"Playwright install stderr: {process.stderr}")
                    self.done.emit(True)
                except subprocess.CalledProcessError as e:
                    logger.error(f"Playwright install failed (CalledProcessError): {e.stderr}")
                    QMessageBox.critical(None, "Instalasi Gagal", 
                                         f"Gagal menginstal driver Playwright (Chromium).\n"
                                         f"Pesan Error: {e.stderr.strip()}\n"
                                         f"Pastikan Anda memiliki koneksi internet yang stabil.")
                    self.done.emit(False)
                except FileNotFoundError:
                    logger.error("Playwright command not found. Is Playwright installed?")
                    QMessageBox.critical(None, "Instalasi Gagal", 
                                         "Perintah 'playwright' tidak ditemukan. "
                                         "Pastikan Playwright terinstal dengan benar di lingkungan Anda.")
                    self.done.emit(False)
                except Exception as e:
                    logger.error(f"Repair failed: {e}")
                    QMessageBox.critical(None, "Instalasi Gagal", 
                                         f"Terjadi kesalahan tidak terduga saat menginstal driver: {e}\n"
                                         f"Pastikan Anda memiliki koneksi internet yang stabil.")
                    self.done.emit(False)
        
        self.repair_thread = RepairWorker()
        self.repair_thread.done.connect(self.on_repair_done)
        self.repair_thread.start()

    def on_repair_done(self, success):
        self.btn_repair_search.setEnabled(True)
        self.btn_repair_search.setText("🛠️ Perbaiki / Install Driver Pencarian")
        if success:
            QMessageBox.information(self, "Berhasil", "Driver pencarian berhasil diinstal! Silakan coba cari kembali.")
            self.lbl_global_status.setText("Driver Playwright siap.")
        else:
            # Error message already shown by the worker itself
            self.lbl_global_status.setText("Gagal menginstal driver.")

    # ─── Quick Toggle Handlers (Header Buttons) ──────────────────────────────

    def toggle_theme_quick(self):
        """Toggle tema langsung dari tombol header (Light ↔ Dark)."""
        self.is_dark_mode = not self.is_dark_mode
        # Update label tombol header
        self.btn_toggle_theme.setText("🌙 Dark" if self.is_dark_mode else "☀️ Light")
        # Sinkronkan dengan radio button di Settings
        if self.is_dark_mode:
            self.rb_theme_dark.setChecked(True)
        else:
            self.rb_theme_light.setChecked(True)
        # Load theme (memanggil update_theme_from_radio via signal akan double-fire,
        # jadi langsung panggil load_theme dan save)
        self.load_theme()
        self._save_env_key("APP_THEME", "dark" if self.is_dark_mode else "light")
        self.lbl_global_status.setText(
            f"🎨 Tema diubah ke {'Gelap (Dark)' if self.is_dark_mode else 'Terang (Light)'}"
        )

    def toggle_lang_quick(self):
        """Toggle bahasa langsung dari tombol header (ID ↔ EN)."""
        new_lang = "en" if self.current_lang == "id" else "id"
        self.current_lang = new_lang
        # Update label tombol header
        self.btn_toggle_lang.setText("🇮🇩 ID" if new_lang == "id" else "🇬🇧 EN")
        # Sinkronkan dengan radio button di Settings
        if new_lang == "en":
            self.rb_lang_en.setChecked(True)
        else:
            self.rb_lang_id.setChecked(True)
        self.retranslate_ui()
        self._save_env_key("APP_LANG", new_lang)

    def _save_env_key(self, key: str, value: str):
        """Simpan satu key=value ke file .env (buat jika belum ada)."""
        env_path = get_writable_path(".env")
        lines = []
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        found = False
        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[i] = f"{key}={value}\n"
                found = True
        if not found:
            lines.append(f"{key}={value}\n")
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    # ─────────────────────────────────────────────────────────────────────────

    def update_theme_from_radio(self):
        self.is_dark_mode = self.rb_theme_dark.isChecked()
        # Update header button label juga
        self.btn_toggle_theme.setText("🌙 Dark" if self.is_dark_mode else "☀️ Light")
        self.load_theme()
        # Save preference
        env_path = get_writable_path(".env")
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            found = False
            for i, line in enumerate(lines):
                if line.startswith("APP_THEME="):
                    lines[i] = f"APP_THEME={'dark' if self.is_dark_mode else 'light'}\n"
                    found = True
            if not found:
                lines.append(f"APP_THEME={'dark' if self.is_dark_mode else 'light'}\n")
            with open(env_path, "w", encoding="utf-8") as f:
                f.writelines(lines)

    def change_language(self):
        new_lang = "en" if self.rb_lang_en.isChecked() else "id"
        if new_lang != self.current_lang:
            self.current_lang = new_lang
            # Sinkronkan label tombol header
            self.btn_toggle_lang.setText("🇮🇩 ID" if new_lang == "id" else "🇬🇧 EN")
            self.retranslate_ui()
            self._save_env_key("APP_LANG", new_lang)

    def retranslate_ui(self):
        texts = UI_STRINGS.get(self.current_lang, UI_STRINGS['id'])
        
        # Tab Labels
        self.tabs.setTabText(0, texts['tab_search'])
        self.tabs.setTabText(1, texts['tab_split'])
        self.tabs.setTabText(2, texts['tab_ai'])
        self.tabs.setTabText(3, texts['tab_viewer'])
        self.tabs.setTabText(4, texts['tab_history'])
        self.tabs.setTabText(5, texts['tab_setting'])
        self.tabs.setTabText(6, texts['tab_help'])
        self.tabs.setTabText(7, texts['tab_about'])
        
        # Viewer Labels
        if hasattr(self, 'lbl_viewer_empty'): self.lbl_viewer_empty.setText(texts['viewer_empty'])
        if hasattr(self, 'btn_viewer_open'): self.btn_viewer_open.setText(texts['viewer_open_btn'])
        
        # Setting Tab Labels
        if hasattr(self, 'lbl_setting_main_title'):
            self.lbl_setting_main_title.setText(f"<h2>⚙️ {texts['tab_setting']}</h2>")
        if hasattr(self, 'lbl_setting_dl_folder'):
            self.lbl_setting_dl_folder.setText(f"<b>{texts['setting_dl_folder']}</b>")
        if hasattr(self, 'lbl_setting_dl_desc'):
            self.lbl_setting_dl_desc.setText(texts['setting_dl_desc'])
        if hasattr(self, 'txt_download_path'):
            self.txt_download_path.setPlaceholderText(texts['setting_dl_placeholder'])
        if hasattr(self, 'btn_browse_dl'):
            self.btn_browse_dl.setText(texts['setting_browse'])
            
        self.lbl_setting_theme.setText(f"<b>{texts['setting_theme']}</b>")
        self.lbl_setting_lang.setText(f"<b>{texts['setting_lang']}</b>")
        self.lbl_setting_api_title.setText(f"<b>{texts['setting_api_title']}</b>")
        self.lbl_setting_api_desc.setText(texts['setting_api_desc'])
        self.btn_save_settings.setText(texts['btn_save_settings'])
        self.rb_lang_id.setText("Indonesia")
        self.rb_theme_light.setText("Terang (Light)" if self.current_lang == 'id' else "Light Mode")
        self.rb_theme_dark.setText("Gelap (Dark)" if self.current_lang == 'id' else "Dark Mode")
        
        if hasattr(self, 'txt_keys_tab'):
            self.txt_keys_tab.setPlaceholderText(texts['setting_keys_placeholder'])
            
        if hasattr(self, 'lbl_setting_repair_title'):
            self.lbl_setting_repair_title.setText(f"<b>{texts['setting_repair_title']}</b>")
        if hasattr(self, 'lbl_setting_repair_desc'):
            self.lbl_setting_repair_desc.setText(texts['setting_repair_desc'])
        if hasattr(self, 'btn_repair_search'):
            self.btn_repair_search.setText(texts['setting_repair_btn'])

        # Header Buttons Quick Switch Labels
        self.btn_toggle_lang.setText(texts['header_lang_id'] if self.current_lang == 'id' else texts['header_lang_en'])
        self.btn_toggle_theme.setText(texts['header_theme_dark'] if self.is_dark_mode else texts['header_theme_light'])
        
        # Search Tab
        self.btn_search.setText(texts['btn_search'])
        self.txt_search.setPlaceholderText(texts['search_placeholder'])
        self.chk_llm.setText(texts['chk_smart_search'])
        if hasattr(self, 'chk_fast_mode'):
            self.chk_fast_mode.setText(texts['chk_fast_mode'])
        if hasattr(self, 'lbl_active_downloads_title'):
            self.lbl_active_downloads_title.setText(texts['active_downloads'])
        
        # AI Tab
        if hasattr(self, 'btn_new_chat'): self.btn_new_chat.setText(texts['ai_new_chat'])
        if hasattr(self, 'lbl_ai_history_title'): self.lbl_ai_history_title.setText(texts['ai_history'])
        self.txt_chat.setPlaceholderText(texts['ai_input_placeholder'])
        if hasattr(self, 'btn_send_chat'): self.btn_send_chat.setText(texts['ai_send'])
        
        # Help Tab
        if hasattr(self, 'help_display'):
            self.help_display.setHtml(texts['help_html'])
            
        # About Tab
        if hasattr(self, 'lbl_about_content'):
            self.lbl_about_content.setText(texts['about_html'])
        
        # History Tab
        if hasattr(self, 'table_history'):
            self.table_history.setHorizontalHeaderLabels(texts['history_cols'])
        
        self.lbl_global_status.setText(texts['status_ready'])
        if hasattr(self, 'btn_history_refresh'): self.btn_history_refresh.setText(texts['history_refresh'])
        if hasattr(self, 'btn_history_open_folder'): self.btn_history_open_folder.setText(texts['history_open_folder'])
        self.table_history.setHorizontalHeaderLabels(texts['history_cols'])
        
        # Status Bar
        self.lbl_global_status.setText(texts['status_ready'])
        
        # Welcome message refresh if empty
        if not self.chat_history:
            self.show_welcome_message()

    def toggle_api_key_visibility(self):
        if self.btn_toggle_keys.isChecked():
            self.txt_keys_tab.setEchoMode(QLineEdit.Normal)
            self.btn_toggle_keys.setText("🔒")
        else:
            self.txt_keys_tab.setEchoMode(QLineEdit.Password)
            self.btn_toggle_keys.setText("👁️")

    def save_settings_from_tab(self):
        env_path = get_writable_path(".env")
        keys = self.txt_keys_tab.text().strip()
        dl_dir = self.txt_download_path.text().strip()
        
        lines = []
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        else:
            # Check dev folder
            env_path_dev = os.path.join(os.getcwd(), ".env")
            if os.path.exists(env_path_dev):
                with open(env_path_dev, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                
        # Update or append keys
        key_found = False
        dl_found = False
        for i, line in enumerate(lines):
            if line.startswith("GEMINI_API_KEYS="):
                lines[i] = f"GEMINI_API_KEYS={keys}\n"
                key_found = True
            elif line.startswith("DOWNLOAD_DIR="):
                lines[i] = f"DOWNLOAD_DIR={dl_dir}\n"
                dl_found = True
                
        if not key_found:
            lines.append(f"GEMINI_API_KEYS={keys}\n")
        if not dl_found:
            lines.append(f"DOWNLOAD_DIR={dl_dir}\n")
            
        try:
            with open(env_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
                
            # Update session
            os.environ["DOWNLOAD_DIR"] = dl_dir
            from app.services.gemini_search_assistant import global_rotator
            global_rotator.reload_keys()
            
            QMessageBox.information(self, "Success", "Pengaturan berhasil disimpan!")
            self.lbl_global_status.setText("✅ Settings saved.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan pengaturan: {e}")
        
        self.tabs.currentChanged.connect(self.on_tab_changed)

    def on_tab_changed(self, index):
        if index == 4: # History Tab is index 4
            self.load_history()

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.btn_theme.setText("☀️ Theme" if self.is_dark_mode else "🌙 Theme")
        self.load_theme()

    def open_settings(self):
        dlg = KeySettingsDialog(self)
        if dlg.exec():
            QMessageBox.information(self, "Success", "API Keys berhasil disimpan.")

    def do_search(self):
        self.search_timer.stop() # Cancel timer if running
        keyword = self.txt_search.text().strip()
        if not keyword:
            return
            
        self.btn_search.setEnabled(False)
        self.lbl_status.setText(f"Mencari '{keyword}'...")
        
        # Clear old results
        for i in reversed(range(self.results_layout.count())): 
            widget = self.results_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
            
        # Prevent QThread Destroyed error by keeping references to old running workers
        if hasattr(self, 'worker') and self.worker.isRunning():
            try:
                self.worker.results_found.disconnect()
                self.worker.error.disconnect()
                self.worker.status_update.disconnect()
            except Exception:
                pass
            if not hasattr(self, 'old_workers'):
                self.old_workers = []
            self.old_workers.append(self.worker)
            # Prune old workers that have finished
            self.old_workers = [w for w in self.old_workers if w.isRunning()]
            
        source = "Global" if "Global" in self.cb_source.currentText() else "Shamela"
        fast_enabled = self.chk_fast_mode.isChecked() if hasattr(self, 'chk_fast_mode') else False
        self.worker = SearchWorker(keyword, self.chk_llm.isChecked(), page_num=1, source=source, fast_mode=fast_enabled)
        self.current_source = source
        self.current_query = keyword
        self.current_page = 1
        
        self.worker.results_found.connect(self.on_search_finished)
        self.worker.error.connect(self.on_search_error)
        self.worker.status_update.connect(self.lbl_llm_status.setText)
        self.worker.status_update.connect(self.lbl_global_status.setText)
        self.worker.progress_val.connect(self.update_global_progress)
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(10)
        self.worker.start()

    def update_global_progress(self, val):
        self.progress_bar.setValue(val)
        if val >= 100:
            QTimer.singleShot(2000, lambda: self.progress_bar.setVisible(False))

    def load_more_results(self):
        self.current_page += 1
        self.btn_load_more.setEnabled(False)
        self.btn_load_more.setText("⏳ Loading...")
        
        fast_enabled = self.chk_fast_mode.isChecked() if hasattr(self, 'chk_fast_mode') else False
        self.worker = SearchWorker(self.current_query, self.chk_llm.isChecked(), page_num=self.current_page, source=self.current_source, fast_mode=fast_enabled)
        self.worker.results_found.connect(self.on_load_more_finished)
        self.worker.error.connect(self.on_search_error)
        self.worker.status_update.connect(self.lbl_llm_status.setText)
        self.worker.status_update.connect(self.lbl_global_status.setText)
        self.worker.progress_val.connect(self.update_global_progress)
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(10)
        self.worker.start()

    def on_load_more_finished(self, results):
        self.btn_load_more.setEnabled(True)
        self.btn_load_more.setText("Lihat 10 Hasil Berikutnya ⬇️")
        
        if not results:
            self.btn_load_more.setVisible(False)
            QMessageBox.information(self, "Info", "Tidak ada hasil lagi.")
            return

        for data in results:
            card = ResultCard(data)
            card.download_requested.connect(lambda bd, c=card: self.on_download_requested(bd, c))
            card.pdf_options_requested.connect(lambda bd, c=card: self.on_archive_pdf_requested(bd, c))
            card.full_text_requested.connect(lambda bd, c=card: self.on_archive_fulltext_requested(bd, c))
            card.ai_query_requested.connect(self.on_ai_query_requested)
            self.results_layout.addWidget(card)
            # Auto-fetch metadata if Archive.org
            self._trigger_metadata_fetch(card, data)
        
        self.lbl_status.setText(f"Menampilkan {self.results_layout.count()} kitab.")

    def on_search_finished(self, results):
        self.btn_search.setEnabled(True)
        self.btn_search.setText("Search")
        self.progress_bar.setVisible(False)
        
        # Clear previous results (including any help labels)
        for i in reversed(range(self.results_layout.count())): 
            item = self.results_layout.itemAt(i)
            if item:
                w = item.widget()
                if w and w != self.btn_load_more:
                    w.setParent(None)
                    w.deleteLater()
        
        self.lbl_status.setText(f"Ditemukan {len(results)} kitab.")
        
        if len(results) == 0:
            msg = "Tidak ditemukan hasil. Tips: Pastikan driver pencarian sudah terinstal di Tab Setting, atau coba matikan 'Smart Arabic Search'."
            self.lbl_status.setText(f"Ditemukan 0 kitab. {msg}")
            # Add a helpful label in the results area
            help_lbl = QLabel(f"\n\n\n<center><font color='#6c757d'>{msg}</font></center>")
            help_lbl.setWordWrap(True)
            help_lbl.setAlignment(Qt.AlignCenter)
            self.results_layout.addWidget(help_lbl)
            return

        for data in results:
            card = ResultCard(data)
            card.download_requested.connect(lambda bd, c=card: self.on_download_requested(bd, c))
            card.pdf_options_requested.connect(lambda bd, c=card: self.on_archive_pdf_requested(bd, c))
            card.full_text_requested.connect(lambda bd, c=card: self.on_archive_fulltext_requested(bd, c))
            card.ai_query_requested.connect(self.on_ai_query_requested)
            self.results_layout.addWidget(card)
            # Auto-fetch metadata if Archive.org
            self._trigger_metadata_fetch(card, data)

        if len(results) >= 8: # If we have many results, show Load More
            self.btn_load_more.setVisible(True)
            self.btn_load_more.setText(f"Lihat 10 Hasil Berikutnya (Halaman {self.current_page + 1}) ⬇️")
        else:
            self.btn_load_more.setVisible(False)

    def on_search_error(self, err):
        self.btn_search.setEnabled(True)
        self.lbl_status.setText(f"Error: {err}")
        QMessageBox.warning(self, "Search Error", str(err))

    def on_ai_query_requested(self, book_data):
        """Fitur Tanya AI: Deep Vision (Cover + Contents) dan pindah ke tab AI."""
        self.tabs.setCurrentWidget(self.tab_chat)
        
        judul = book_data.get('judul_indonesia') or book_data.get('judul_arab') or book_data.get('title', 'Kitab')
        penulis = book_data.get('penulis_indonesia') or book_data.get('penulis_arab') or book_data.get('author', 'Anonim')
        
        d_url = book_data.get('detail_url', '') or book_data.get('url', '')
        f_size = book_data.get('file_size') or book_data.get('size_mb') or book_data.get('size', 'N/A')
        p_count = book_data.get('page_count') or book_data.get('pages', 'N/A')
        
        # Auto-detect Source Label from URL or metadata
        source = book_data.get('source_label')
        if not source:
            if 'shamela.org' in d_url.lower(): source = "Shamela.org"
            elif 'archive.org' in d_url.lower(): source = "Archive.org"
            else: source = "Cari Kitab Database"
        
        # Pre-format Metadata as HTML Table to Ensure AI uses it
        metadata_table = f"""
        <table border="1" style="border-collapse: collapse; width: 100%; margin-bottom: 20px; background-color: {'#2a2a2a' if self.is_dark_mode else '#f8f9fa'}; color: {'#eee' if self.is_dark_mode else '#333'};">
            <tr style="background-color: #0d6efd; color: white;">
                <td colspan="2" style="padding: 10px; text-align: center;"><b>📄 INFORMASI TEKNIS EBOOK</b></td>
            </tr>
            <tr><td style="padding: 8px; width: 30%;"><b>Judul:</b></td><td style="padding: 8px;">{judul}</td></tr>
            <tr><td style="padding: 8px;"><b>Karya:</b></td><td style="padding: 8px;">{penulis}</td></tr>
            <tr><td style="padding: 8px;"><b>Halaman:</b></td><td style="padding: 8px;">{p_count} Halaman (Fakta Sistem)</td></tr>
            <tr><td style="padding: 8px;"><b>Ukuran:</b></td><td style="padding: 8px;">{f_size}</td></tr>
            <tr><td style="padding: 8px;"><b>Link:</b></td><td style="padding: 8px;"><a href="{d_url}" style="color: #0d6efd;">Akses {source}</a></td></tr>
        </table>
        """
        
        prompt = f"""[USER QUESTION]
Analisislah kitab berdasarkan 10 halaman gambar yang terlampir.

[TABEL METADATA WAJIB (Copy-Paste ini di baris pertama jawaban Anda!)]
{metadata_table}

[INSTRUKSI KHUSUS]
- Langsung berikan <h3>RESUME MENDALAM</h3> (minimal 3 paragraf).
- Langsung berikan <h3>DAFTAR ISI</h3> yang berhasil diidentifikasi.
- GUNAKAN PURE HTML. DILARANG KERAS MENGGUNAKAN MARKDOWN (###, **, |, ---)."""

        # Start Peeker Worker
        display_text = f"🔍 <b>Menganalisis Kitab:</b> {judul}<br>Silakan tunggu, saya sedang membedah 10 halaman awal untuk memberikan resume mendalam..."
        
        self.peeker = VisionPeekerWorker(book_data)
        self.peeker.status.connect(self.lbl_global_status.setText)
        self.peeker.done.connect(lambda paths, text: self._start_ai_chat_with_multi_vision(prompt, display_text, paths, text, metadata_table))
        self.peeker.start()

    def _start_ai_chat_with_multi_vision(self, hidden_prompt, display_text, image_paths, extracted_text="", metadata_table=""):
        """Memulai chat dengan banyak gambar visual, menyembunyikan prompt teknis."""
        if self.chat_history:
            self.start_new_chat()
            
        self.current_vision_images = image_paths
        self.current_vision_text = extracted_text
        self.current_vision_metadata = metadata_table
        self.send_chat_message(override_prompt=hidden_prompt, display_text=display_text, metadata_header=metadata_table)

    def on_download_requested(self, book_data, card=None):
        """Alur download standar (Shamela / non-archive.org)."""
        # 0. Check Download Folder first
        final_dir = os.environ.get('DOWNLOAD_DIR')
        if not final_dir or not os.path.isdir(final_dir):
            selected = QFileDialog.getExistingDirectory(self, "Pilih Folder untuk Menyimpan Download")
            if not selected:
                return
            final_dir = selected
        else:
            final_dir = get_downloads_dir()

        d_url = book_data.get('detail_url') or book_data.get('url')
        if not d_url:
            QMessageBox.warning(self, "Error", "Link buku tidak valid.")
            return

        worker = PdfLinkWorker(book_data, d_url)
        worker.finished.connect(lambda b, u: self.start_download(b, u, final_dir, card))
        worker.failed.connect(self.on_search_error)
        worker.status_update.connect(self.lbl_global_status.setText)
        worker.progress_val.connect(self.update_global_progress)
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(10)
        worker.start()
        if not hasattr(self, 'pdf_workers'):
            self.pdf_workers = []
        self.pdf_workers.append(worker)

    # ─── Metadata Auto-Fetch Handlers ─────────────────────────────────────────

    def _trigger_metadata_fetch(self, card, data):
        """Picu pengambilan metadata secara background untuk card Archive.org."""
        url = data.get('detail_url', '') or data.get('url', '')
        if 'archive.org' not in url.lower():
            return
            
        # Gunakan ArchiveFetchWorker tapi jangan ganggu UI utama (silent)
        worker = ArchiveFetchWorker(url, mode="pdf") 
        worker.finished.connect(lambda archive_data: self._on_metadata_auto_fetched(archive_data, card))
        worker.start()
        
        # Simpan referensi agar tidak di-garbage collect
        if not hasattr(self, '_metadata_workers'):
            self._metadata_workers = []
        self._metadata_workers.append(worker)
        # Bersihkan worker yang sudah selesai secara berkala
        self._metadata_workers = [w for w in self._metadata_workers if w.isRunning()]

    def _on_metadata_auto_fetched(self, archive_data, card):
        """Update label metadata pada card setelah data asli didapat (Halaman & Ukuran per Kategori)."""
        pages = archive_data.get("pages")
        
        # 1. Hitung ukuran tiap kategori
        cat_sizes = []
        
        # Original PDF
        pdf_orig = archive_data.get("pdf_files", [])
        if pdf_orig:
            total_pdf = sum([float(f.get("size_mb", "0").split(" ")[0]) for f in pdf_orig if " MB" in f.get("size_mb", "")])
            if total_pdf > 0: cat_sizes.append(f"{total_pdf:.1f}MB (PDF)")
            
        # Searchable PDF
        pdf_text = archive_data.get("pdf_text_files", [])
        if pdf_text:
            total_text_pdf = sum([float(f.get("size_mb", "0").split(" ")[0]) for f in pdf_text if " MB" in f.get("size_mb", "")])
            if total_text_pdf > 0: cat_sizes.append(f"{total_text_pdf:.1f}MB (PDF Text)")
            
        # Full Text
        full_text = archive_data.get("full_text_files", [])
        if full_text:
            total_ft = sum([float(f.get("size_mb", "0").split(" ")[0]) for f in full_text if " MB" in f.get("size_mb", "")])
            if total_ft > 0: cat_sizes.append(f"{total_ft:.1f}MB (TXT)")

        # Gabungkan menjadi satu string: 10MB (PDF) | 2MB (TXT)
        size_str = " | ".join(cat_sizes) if cat_sizes else None
        
        # Update card UI
        card.update_metadata(page_count=pages, file_size=size_str)


    # ─── Archive.org Download Handlers ────────────────────────────────────────

    def _get_download_dir(self) -> str:
        """Dapatkan folder download, prompt ke user jika belum diset."""
        final_dir = os.environ.get('DOWNLOAD_DIR')
        if not final_dir or not os.path.isdir(final_dir):
            final_dir = get_downloads_dir()
        return final_dir

    def on_archive_pdf_requested(self, book_data: dict, card):
        """Dipanggil saat user klik tombol PDF pada card archive.org."""
        self._launch_archive_fetch(book_data, card, initial_mode="pdf")

    def on_archive_fulltext_requested(self, book_data: dict, card):
        """Dipanggil saat user klik tombol Full Text pada card archive.org."""
        self._launch_archive_fetch(book_data, card, initial_mode="fulltext")

    def _launch_archive_fetch(self, book_data: dict, card, initial_mode: str):
        """Jalankan ArchiveFetchWorker untuk mengambil metadata file archive.org."""
        d_url = book_data.get('detail_url') or book_data.get('url', '')
        if not d_url:
            QMessageBox.warning(self, "Error", "Link archive.org tidak valid.")
            return

        self.lbl_global_status.setText("⏳ Mengambil daftar file dari Archive.org...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(15)

        worker = ArchiveFetchWorker(d_url, mode=initial_mode)
        worker.status_update.connect(self.lbl_global_status.setText)
        worker.finished.connect(
            lambda data: self._on_archive_fetch_done(data, book_data, card, initial_mode)
        )
        worker.error.connect(
            lambda err, c=card: self._on_archive_fetch_error(err, c)
        )
        worker.start()

        if not hasattr(self, '_archive_workers'):
            self._archive_workers = []
        self._archive_workers.append(worker)

    def _on_archive_fetch_done(self, archive_data: dict, book_data: dict, card, initial_mode: str):
        """Setelah metadata berhasil diambil, tampilkan dialog pilihan file."""
        self.progress_bar.setVisible(False)
        self.lbl_global_status.setText("✅ Metadata Archive.org berhasil diambil.")

        # Restore tombol card
        if initial_mode == "fulltext":
            card.restore_fulltext_button()
        else:
            card.restore_pdf_button()

        # Buka dialog
        dialog = ArchiveDownloadDialog(archive_data, initial_mode=initial_mode, parent=self)
        dialog.files_selected.connect(
            lambda files: self._start_archive_downloads(files, book_data, card)
        )
        dialog.exec()

    def _on_archive_fetch_error(self, error_msg: str, card):
        """Tangani error saat fetch metadata archive.org."""
        self.progress_bar.setVisible(False)
        self.lbl_global_status.setText(f"❌ Gagal: {error_msg}")
        card.restore_pdf_button()
        if hasattr(card, 'restore_fulltext_button'):
            card.restore_fulltext_button()
        QMessageBox.warning(self, "Error Archive.org", error_msg)

    def _start_archive_downloads(self, files: list, book_data: dict, card=None):
        """
        Antri semua file yang dipilih user untuk didownload secara berurutan.
        Setiap file masuk ke queue download_manager satu per satu.
        """
        target_dir = self._get_download_dir()
        judul = book_data.get('judul_indonesia') or book_data.get('judul_arab', 'Archive')
        
        for f in files:
            file_name = f.get("name", "unknown")
            file_url = f.get("url", "")
            size_mb = f.get("size_mb", "N/A")
            size_bytes = f.get("size_bytes", 0)

            if not file_url:
                continue

            # Sanitasi: gunakan nama file asli dari archive.org
            safe_filename = sanitize_filename(file_name)

            import uuid
            d_id = str(uuid.uuid4())[:8]

            # Estimasi pages dari ukuran (archive.org tidak selalu ada metadata pages)
            pages = book_data.get('page_count', 'N/A')
            penulis_gabung = book_data.get('penulis_indonesia') or book_data.get('penulis_arab', 'Anonim')

            item = DownloadItem(d_id, safe_filename, pages=pages, size_mb=size_mb, author=penulis_gabung, absolute_dir=target_dir)
            item.cancel_requested.connect(self.download_manager.cancel_download)
            item.split_requested.connect(self.on_split_requested)
            item.rename_requested.connect(self.on_rename_requested)
            self.downloads_layout.insertWidget(0, item)
            self.download_items[d_id] = item

            # Simpan ke DB history
            dest_path = Path(target_dir) / safe_filename
            history_id = db.add_history(
                judul_arab=book_data.get('judul_arab', ''),
                judul_indonesia=judul,
                penulis_arab=book_data.get('penulis_arab', ''),
                penulis_indonesia=book_data.get('penulis_indonesia', ''),
                lokasi_file=str(dest_path),
                status="Queued"
            )
            item.history_id = history_id

            # Antri download
            import asyncio
            asyncio.run_coroutine_threadsafe(
                self._trigger_dl(d_id, file_url, safe_filename, target_dir, card),
                self.async_loop
            )

        # Pindah ke tab History supaya user bisa melihat progress
        self.tabs.setCurrentWidget(self.tab_history)
        self.lbl_global_status.setText(
            f"✅ {len(files)} file ditambahkan ke antrian download."
        )

    def start_download(self, book_data, pdf_url, target_dir, card=None):
        # 1. Prepare Display Name & Sanitized Filename
        judul = book_data.get('judul_indonesia') or book_data.get('judul_arab', 'Buku')
        penulis = book_data.get('penulis_indonesia') or book_data.get('penulis_arab', '')
        
        # Ensure name format: Judul - Penulis
        if penulis and penulis.lower() not in ['anonim', 'unknown', '']:
            full_name = f"{judul} - {penulis}"
        else:
            full_name = f"{judul}"
        
        ext = ".pdf" if ".pdf" in pdf_url.lower() else ".bok"
        filename = sanitize_filename(full_name + ext)
        
        # Unique Download ID
        import uuid
        d_id = str(uuid.uuid4())[:8]
        
        # 2. Add UI item (Newest first)
        pages = book_data.get('page_count', 'N/A')
        size_mb = book_data.get('file_size', 'N/A')
        item = DownloadItem(d_id, filename, pages=pages, size_mb=size_mb, author=penulis, absolute_dir=target_dir)
        item.cancel_requested.connect(self.download_manager.cancel_download)
        item.split_requested.connect(self.on_split_requested)
        item.rename_requested.connect(self.on_rename_requested)
        self.downloads_layout.insertWidget(0, item)
        self.download_items[d_id] = item
        
        # 3. Save to DB history (Queued) with correct path
        dest_path = Path(target_dir) / filename
        history_id = db.add_history(
            judul_arab=book_data.get('judul_arab', ''), 
            judul_indonesia=book_data.get('judul_indonesia', ''),
            penulis_arab=book_data.get('penulis_arab', ''),
            penulis_indonesia=book_data.get('penulis_indonesia', ''),
            lokasi_file=str(dest_path),
            status="Queued"
        )
        item.history_id = history_id
        
        # 4. Enqueue download into the asyncio loop via threadsafe call
        # Pass the directory to download manager if needed, but manager 
        # usually handles base dir. We'll pass the full path.
        import asyncio
        asyncio.run_coroutine_threadsafe(
            self._trigger_dl(d_id, pdf_url, filename, target_dir, card), 
            self.async_loop
        )

    async def _trigger_dl(self, d_id, url, filename, target_dir, card=None):
        """Memicu download via manager dan menyimpan mapping card."""
        if card:
            if not hasattr(self, 'card_downloads'):
                self.card_downloads = {}
            self.card_downloads[d_id] = card
        self.download_manager.add_download(d_id, url, filename, download_dir=target_dir)

    @Slot(str, int, int, float, str)
    def on_download_progress(self, d_id, downloaded, total, speed, status):
        if d_id in self.download_items:
            item = self.download_items[d_id]
            item.update_progress(downloaded, total, speed, status)

    @Slot(str, str)
    def on_download_finished(self, d_id, path):
        if d_id in self.download_items:
            item = self.download_items[d_id]
            # Force UI update to Completed just in case
            item.update_progress(100, 100, 0, "Completed")
            
            # Update DB
            if hasattr(item, 'history_id'):
                db.update_history_status(item.history_id, "Completed", path)
                logger.info(f"Updated DB history {item.history_id} to Completed")

            # Restore card button status if mapped
            if hasattr(self, 'card_downloads') and d_id in self.card_downloads:
                card = self.card_downloads[d_id]
                try:
                    card.restore_download_button()
                    # Also check for fulltext restore if relevant
                    if hasattr(card, 'restore_fulltext_button'):
                        card.restore_fulltext_button()
                except Exception:
                    pass
                del self.card_downloads[d_id]
            
    @Slot(str, str)
    def on_download_error(self, d_id, error_msg):
        # We already show error in UI via progress slot when status is Error
        pass

    @Slot(str, str, str)
    def on_split_requested(self, d_id, filename, d_dir):
        pdf_path = Path(d_dir) / filename
        if not pdf_path.exists() or pdf_path.stat().st_size == 0:
            QMessageBox.warning(self, "Error", "File PDF asli tidak ditemukan atau berukuran 0 Bytes (Corrupted).")
            return

        item = self.download_items.get(d_id)
        pages = item.pages if item else "N/A"
        size_mb = item.size_mb if item else "N/A"
        
        dlg = SplitDialog(filename, pages=pages, size_mb=size_mb, parent=self)
        if dlg.exec_():
            split_type, val = dlg.get_values()
            
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            self.lbl_global_status.setText(f"Splitting PDF: {filename}...")
            
            self.sw = SplitWorker(str(pdf_path), split_type, val)
            self.sw.status_update.connect(lambda s: self.lbl_global_status.setText(s))
            self.sw.finished.connect(lambda res: self.on_split_finished(filename, res))
            self.sw.error.connect(self.on_split_error)
            self.sw.start()

    def on_split_finished(self, filename, results):
        self.progress_bar.setVisible(False)
        self.lbl_global_status.setText(f"✅ Split Selesai! {len(results)} bagian dibuat.")
        
        import os
        # Show specific success
        d_dir = get_downloads_dir()
        msg = f"PDF Berhasil dipisah menjadi {len(results)} bagian.\n"
        msg += f"Lokasi: {Path(d_dir) / 'splits'}\n\n"
        for r in results[:10]:
            msg += f"- {os.path.basename(r)}\n"
        if len(results) > 10:
            msg += f"...and {len(results)-10} more."
            
        QMessageBox.information(self, "Split Sukses", msg)
        
        # Open folder
        downloads_dir = Path(get_downloads_dir()) / "splits"
        if os.name == 'nt':
            os.startfile(str(downloads_dir.absolute()))

    def on_split_error(self, err):
        self.progress_bar.setVisible(False)
        self.lbl_global_status.setText("❌ Gagal memproses split.")
        QMessageBox.critical(self, "Split Error", f"Terjadi kesalahan saat memisah PDF:\n{err}")

    def on_rename_requested(self, d_id, current_filename, d_dir):
        # 1. Ask for new name via custom wider dialog
        dialog = QInputDialog(self)
        dialog.setWindowTitle("Rename PDF")
        dialog.setLabelText("Nama file baru:")
        dialog.setTextValue(current_filename)
        dialog.setInputMode(QInputDialog.TextInput)
        # Set minimum width: at least 50% of filename length (in pixels), minimum 500px
        min_width = max(500, len(current_filename) * 8)
        dialog.setMinimumWidth(min_width)
        dialog.resize(min_width, 150)
        
        ok = dialog.exec()
        new_name = dialog.textValue()
        
        if not ok or not new_name.strip():
            return
            
        # 2. Sanitize and add extension if missing
        ext = os.path.splitext(current_filename)[1]
        if not new_name.lower().endswith(ext.lower()):
            new_name += ext
            
        new_name = sanitize_filename(new_name)
        
        if new_name == current_filename:
            return
            
        # 3. Rename physical file
        old_path = Path(d_dir) / current_filename
        new_path = Path(d_dir) / new_name
        
        if new_path.exists():
            QMessageBox.warning(self, "Rename Gagal", "File dengan nama tersebut sudah ada.")
            return
            
        try:
            if old_path.exists():
                old_path.rename(new_path)
                
            # 4. Update UI Item
            item = self.download_items.get(d_id)
            if item:
                item.filename = new_name
                item.lbl_filename.setText(new_name)
                # Note: item.btn_open_file might need text update if it shows extension
                if item.btn_open_file.isVisible():
                    item.btn_open_file.setText(f"Buka {new_name.split('.')[-1].upper()}")
            
            # 5. Update DB
            if item and hasattr(item, 'history_id'):
                db.update_history_status(item.history_id, "Completed", str(new_path))
                logger.info(f"Updated DB history {item.history_id} with new path: {new_path}")
                
            QMessageBox.information(self, "Sukses", f"File berhasil diubah menjadi:\n{new_name}")
            self.lbl_global_status.setText(f"✅ Rename sukses: {new_name}")
            
        except Exception as e:
            logger.error(f"Rename failed: {e}")
            QMessageBox.critical(self, "Error", f"Gagal mengubah nama file:\n{e}")

    def load_history(self):
        records = db.get_all_history()
        self.table_history.setRowCount(len(records))
        for row_idx, r in enumerate(records):
            judul = f"{r.get('judul_arab') or ''} / {r.get('judul_indonesia') or ''}"
            penulis = f"{r.get('penulis_arab') or ''} / {r.get('penulis_indonesia') or ''}"
            self.table_history.setItem(row_idx, 0, QTableWidgetItem(judul))
            self.table_history.setItem(row_idx, 1, QTableWidgetItem(penulis))
            self.table_history.setItem(row_idx, 2, QTableWidgetItem(str(r.get('tanggal_download') or '')))
            self.table_history.setItem(row_idx, 3, QTableWidgetItem(str(r.get('status') or '')))
            self.table_history.setItem(row_idx, 4, QTableWidgetItem(str(r.get('lokasi_file') or '')))

    def open_downloads_folder(self):
        downloads_dir = get_downloads_dir()
        if os.name == 'nt':
            os.startfile(str(downloads_dir))

    def closeEvent(self, event):
        import asyncio
        asyncio.run_coroutine_threadsafe(self.download_manager.close(), self.async_loop)
        self.async_loop.call_soon_threadsafe(self.async_loop.stop)
        self.async_thread.wait()
        super().closeEvent(event)

if __name__ == "__main__":
    # 0. Fix for PyInstaller + multiprocessing (CRITICAL to prevent fork bomb)
    import multiprocessing
    multiprocessing.freeze_support()

    # 1. Fix taskbar icon grouping on Windows (CRITICAL for taskbar icon)
    # Must be done before creating QApplication
    if os.name == 'nt':
        try:
            import ctypes
            myappid = 'vibe.cari.kitab.v1' # arbitrary unique string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception as e:
            print("Failed to set AppUserModelID:", e)

    app = QApplication(sys.argv)
    
    # 2. Set App-wide Icon (Robust Path)
    # Use .ico for Windows for better taskbar compatibility
    if os.name == 'nt':
        icon_path = Path(resource_path("app/assets/logo.ico"))
    else:
        icon_path = Path(resource_path("app/assets/logo.png"))
    
    if icon_path.exists():
        app_icon = QIcon(str(icon_path))
        app.setWindowIcon(app_icon)
    else:
        # Fallback to PNG if ICO is missing
        icon_path_alt = Path(resource_path("app/assets/logo.png"))
        if icon_path_alt.exists():
            app.setWindowIcon(QIcon(str(icon_path_alt)))
        else:
            logger.warning(f"Logo not found at {icon_path}")
        
    # 3. Ensure Playwright browsers (Safe call)
    ensure_playwright_browsers()
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
