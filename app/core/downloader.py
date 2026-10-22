import httpx
import time
import os
from pathlib import Path
from PySide6.QtCore import QObject, Signal

class DownloadSignals(QObject):
    progress = Signal(str, int, int, float, str) # id, downloaded_bytes, total_bytes, speed_kbps, status
    finished = Signal(str, str) # id, path
    error = Signal(str, str) # id, error

class DownloadManager:
    def __init__(self, download_dir=None, max_concurrent=5):
        if download_dir is None:
            # Detect system Downloads folder
            if os.name == 'nt':
                # Use Windows shell to get Downloads folder robustly
                try:
                    import ctypes
                    from ctypes import wintypes
                    CSIDL_DOWNLOADS = 37 # Might not be available in CSIDL, use standard path fallback
                    # Fallback to standard %USERPROFILE%\Downloads
                    base = os.path.join(os.environ['USERPROFILE'], 'Downloads')
                    self.download_dir = Path(base) / "Cari Kitab"
                except:
                    self.download_dir = Path.home() / "Downloads" / "Cari Kitab"
            else:
                self.download_dir = Path.home() / "Downloads" / "Cari Kitab"
        else:
            self.download_dir = Path(download_dir)
            
        try:
            self.download_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            # If Downloads folder fails, use AppData as emergency fallback
            print(f"Failed to create downloads in {self.download_dir}: {e}")
            import sys
            if os.name == 'nt':
                base = os.environ.get('APPDATA') or os.path.expanduser('~\\AppData\\Roaming')
                self.download_dir = Path(base) / "Cari Kitab" / "downloads"
            else:
                self.download_dir = Path.home() / ".cari_kitab" / "downloads"
            self.download_dir.mkdir(parents=True, exist_ok=True)
        self.tasks = {} # id -> bool (active)
        self.signals = DownloadSignals()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://shamela.ws/"
        }

    def add_download(self, d_id, url, filename, download_dir=None):
        import threading
        thread = threading.Thread(target=self._run_download, args=(d_id, url, filename, download_dir))
        thread.daemon = True
        thread.start()

    def _run_download(self, d_id, url, filename, download_dir=None):
        import httpx
        import time
        import logging
        logger = logging.getLogger(__name__)
        
        # 0. Selection: User-provided dir or manager default
        active_dir = Path(download_dir) if download_dir else self.download_dir
        if not active_dir.exists():
            active_dir.mkdir(parents=True, exist_ok=True)

        # 1. USE PROVIDED FILENAME (Already sanitized by main.py)
        safe_filename = filename
        filepath = active_dir / safe_filename
        
        # 2. Resilient Download with httpx
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.signals.progress.emit(d_id, 0, 0, 0, f"Attempt {attempt+1}/{max_retries}")
                
                # Adjust Referer dynamically based on URL
                current_headers = self.headers.copy()
                if "shamela.org" in url:
                    current_headers["Referer"] = "https://shamela.org/"
                elif "shamela.ws" in url:
                    current_headers["Referer"] = "https://shamela.ws/"
                
                with httpx.Client(headers=current_headers, follow_redirects=True, timeout=60.0, verify=False) as client:
                    with client.stream("GET", url) as response:
                        if response.status_code != 200:
                            raise Exception(f"HTTP {response.status_code}")
                            
                        total_bytes = int(response.headers.get("Content-Length", 0))
                        downloaded_bytes = 0
                        start_time = time.time()
                        last_emit = start_time
                        
                        with open(filepath, "wb") as f:
                            for chunk in response.iter_bytes(chunk_size=128 * 1024):
                                if not chunk: break
                                f.write(chunk)
                                downloaded_bytes += len(chunk)
                                
                                curr = time.time()
                                if curr - last_emit > 0.4:
                                    elapsed = curr - start_time
                                    speed = (downloaded_bytes / 1024) / elapsed if elapsed > 0 else 0
                                    self.signals.progress.emit(d_id, downloaded_bytes, total_bytes, speed, "Downloading")
                                    last_emit = curr
                                    
                        self.signals.progress.emit(d_id, downloaded_bytes, total_bytes, 0, "Completed")
                        self.signals.finished.emit(d_id, str(filepath))
                        return # SUCCESS!
                        
            except Exception as e:
                logger.error(f"[Downloader] Error: {e}")
                if attempt == max_retries - 1:
                    self.signals.error.emit(d_id, f"Failed: {str(e)}")
                else:
                    time.sleep(3)

    def cancel_download(self, d_id):
        # Cancellation complex in threading, usually just let it finish or check a flag
        pass

    async def close(self):
        pass

# test
if __name__ == "__main__":
    pass
