from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QFrame, QSizePolicy)
from PySide6.QtCore import Qt, Signal

class ResultCard(QFrame):
    download_requested = Signal(dict)       # PDF download (Shamela / non-archive)
    pdf_options_requested = Signal(dict)    # PDF options (archive.org only)
    full_text_requested = Signal(dict)      # Full Text download (archive.org only)
    ai_query_requested = Signal(dict)       # New signal

    def __init__(self, book_data, parent=None):
        super().__init__(parent)
        self.book_data = book_data
        self.setObjectName("resultCard")
        self.setFrameShape(QFrame.StyledPanel)
        
        # Allow card to grow vertically based on content
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(10)
        
        # Clean data from IDs (regex to find long hex strings)
        import re
        id_pattern = r'[a-f0-9]{20,}'
        
        def clean_title(t):
            if not t: return ""
            # Remove long hex IDs and extra dashes/dots
            t = re.sub(id_pattern, '', t)
            t = t.replace('.pdf', '').replace('.bok', '').replace(' - ', ' ').replace('  ', ' ')
            return t.strip(' .-')

        self.book_data['judul_arab'] = clean_title(self.book_data.get('judul_arab', ''))
        self.book_data['judul_indonesia'] = clean_title(self.book_data.get('judul_indonesia', ''))
        self.book_data['penulis_arab'] = clean_title(self.book_data.get('penulis_arab', ''))
        self.book_data['penulis_indonesia'] = clean_title(self.book_data.get('penulis_indonesia', ''))

        # 1. Primary Title (Latin Transliteration)
        primary_layout = QVBoxLayout()
        primary_layout.setSpacing(4)
        
        judul_latin = self.book_data.get('judul_indonesia', '')
        lbl_judul_latin = QLabel(judul_latin)
        lbl_judul_latin.setStyleSheet("font-size: 18px; font-weight: bold; color: #0d6efd;")
        lbl_judul_latin.setWordWrap(True)
        lbl_judul_latin.setAlignment(Qt.AlignLeft)
        
        penulis_latin = self.book_data.get('penulis_indonesia', '')
        lbl_penulis_latin = QLabel(f"Penulis: {penulis_latin}")
        lbl_penulis_latin.setStyleSheet("font-size: 14px; color: #495057; font-weight: 500;")
        lbl_penulis_latin.setAlignment(Qt.AlignLeft)
        if not penulis_latin: lbl_penulis_latin.hide()
        
        primary_layout.addWidget(lbl_judul_latin)
        primary_layout.addWidget(lbl_penulis_latin)

        # 2. Secondary Title (Arabic Original)
        arab_layout = QVBoxLayout()
        arab_layout.setSpacing(4)
        
        judul_arab = self.book_data.get('judul_arab', '')
        lbl_judul_arab = QLabel(judul_arab)
        lbl_judul_arab.setStyleSheet("font-size: 16px; font-weight: bold; color: #198754; font-style: italic;")
        lbl_judul_arab.setWordWrap(True)
        lbl_judul_arab.setAlignment(Qt.AlignRight)
        
        penulis_arab = self.book_data.get('penulis_arab', '')
        lbl_penulis_arab = QLabel(penulis_arab)
        lbl_penulis_arab.setStyleSheet("font-size: 13px; color: #6c757d;")
        lbl_penulis_arab.setAlignment(Qt.AlignRight)
        if not penulis_arab: lbl_penulis_arab.hide()
        
        arab_layout.addWidget(lbl_judul_arab)
        arab_layout.addWidget(lbl_penulis_arab)

        # Metadata Row (Pages & Size)
        metadata_layout = QHBoxLayout()
        metadata_layout.setSpacing(15)
        
        page_count = self.book_data.get('page_count') or "N/A"
        file_size = self.book_data.get('file_size') or "N/A"
        
        self.lbl_pages = QLabel(f"📄 {page_count} Hal")
        self.lbl_pages.setStyleSheet("font-size: 11px; color: #666; background: #f8f9fa; padding: 2px 6px; border-radius: 4px;")
        metadata_layout.addWidget(self.lbl_pages)
            
        self.lbl_size = QLabel(f"💾 {file_size}")
        self.lbl_size.setStyleSheet("font-size: 11px; color: #666; background: #f8f9fa; padding: 2px 6px; border-radius: 4px;")
        metadata_layout.addWidget(self.lbl_size)
        
        metadata_layout.addStretch()
        
        main_layout.addLayout(primary_layout)
        main_layout.addLayout(arab_layout)
        main_layout.addLayout(metadata_layout)

        # Actions row - simplified for better visibility
        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(0, 5, 0, 0)

        # Detect if this is an archive.org result
        detail_url = self.book_data.get('detail_url', '')
        self._is_archive = 'archive.org' in detail_url.lower()
        
        self.btn_url = QPushButton("🔗 URL")
        self.btn_url.setMinimumSize(100, 35)
        self.btn_url.setToolTip(f"Buka halaman sumber: {detail_url}")
        self.btn_url.clicked.connect(self.open_url)
        
        # 🤖 Tanya AI Button (Common for all)
        self.btn_ai = QPushButton("🤖 Tanya AI")
        self.btn_ai.setMinimumSize(110, 35)
        self.btn_ai.setToolTip("Tanyakan detail kitab ini (Resume, Daftar Isi, Nilai Penting) kepada AI")
        self.btn_ai.setStyleSheet("""
            QPushButton {
                background-color: #6f42c1; 
                color: white; 
                font-weight: bold; 
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #59359a;
            }
        """)
        self.btn_ai.clicked.connect(lambda: self.ai_query_requested.emit(self.book_data))
        
        if self._is_archive:
            # For archive.org: PDF Options button
            self.btn_download = QPushButton("⬇️ PDF")
            self.btn_download.setMinimumSize(110, 35)
            self.btn_download.setStyleSheet("background-color: #0d6efd; color: white; font-weight: bold; border-radius: 4px;")
            self.btn_download.setToolTip("Lihat & download pilihan PDF dari Archive.org")
            self.btn_download.clicked.connect(self.request_pdf_options)

            # Full Text button (green) — archive.org specific
            self.btn_fulltext = QPushButton("📄 Full Text")
            self.btn_fulltext.setMinimumSize(110, 35)
            self.btn_fulltext.setStyleSheet("background-color: #198754; color: white; font-weight: bold; border-radius: 4px;")
            self.btn_fulltext.setToolTip("Download Full Text (TXT) dari Archive.org — cocok untuk NotebookLM")
            self.btn_fulltext.clicked.connect(self.request_fulltext)

            action_layout.addStretch()
            action_layout.addWidget(self.btn_url)
            action_layout.addWidget(self.btn_ai)
            action_layout.addWidget(self.btn_fulltext)
            action_layout.addWidget(self.btn_download)
        else:
            # For non-archive: standard single PDF button
            self.btn_download = QPushButton("⬇️ PDF")
            self.btn_download.setMinimumSize(100, 35)
            self.btn_download.setStyleSheet("background-color: #0d6efd; color: white; font-weight: bold; border-radius: 4px;")
            self.btn_download.setToolTip("Download kitab (PDF)")
            self.btn_download.clicked.connect(self.request_download)

            action_layout.addStretch()
            action_layout.addWidget(self.btn_url)
            action_layout.addWidget(self.btn_ai)
            action_layout.addWidget(self.btn_download)

        main_layout.addLayout(action_layout)
        
        # Enforce a larger minimum height
        self.setMinimumHeight(200)
        self.setMinimumWidth(300)

    def update_metadata(self, page_count=None, file_size=None):
        """Update the metadata labels dynamically (from Archive.org API etc)."""
        if page_count is not None and str(page_count) != "0":
            self.lbl_pages.setText(f"📄 {page_count} Hal")
            self.lbl_pages.setStyleSheet("font-size: 11px; color: #198754; background: #e8f5e9; font-weight: bold; padding: 2px 6px; border-radius: 4px;")
        if file_size:
            self.lbl_size.setText(f"💾 {file_size}")
            self.lbl_size.setStyleSheet("font-size: 11px; color: #198754; background: #e8f5e9; font-weight: bold; padding: 2px 6px; border-radius: 4px;")

    def restore_download_button(self):
        """Restore download button after queue/finish."""
        self.btn_download.setEnabled(True)
        self.btn_download.setText("⬇️ PDF")
        
    def restore_fulltext_button(self):
        """Restore fulltext button."""
        if hasattr(self, 'btn_fulltext'):
            self.btn_fulltext.setEnabled(True)
            self.btn_fulltext.setText("📄 Full Text")

    def request_download(self):
        """Standard download (Shamela / non-archive)."""
        self.btn_download.setEnabled(False)
        self.btn_download.setText("⌛ Queue")
        self.download_requested.emit(self.book_data)

    def request_pdf_options(self):
        """PDF options dialog (archive.org)."""
        self.btn_download.setEnabled(False)
        self.btn_download.setText("⌛ Memuat...")
        self.pdf_options_requested.emit(self.book_data)

    def restore_pdf_button(self):
        """Restore PDF button after dialog closed."""
        self.btn_download.setEnabled(True)
        self.btn_download.setText("⬇️ PDF")

    def request_fulltext(self):
        """Full Text download (archive.org)."""
        self.btn_fulltext.setEnabled(False)
        self.btn_fulltext.setText("⌛ Memuat...")
        self.full_text_requested.emit(self.book_data)

    def restore_fulltext_button(self):
        """Restore Full Text button after dialog closed."""
        self.btn_fulltext.setEnabled(True)
        self.btn_fulltext.setText("📄 Full Text")

    def open_url(self):
        import webbrowser
        webbrowser.open(self.book_data.get('detail_url', 'https://archive.org'))

class DownloadItem(QFrame):
    cancel_requested = Signal(str)
    split_requested = Signal(str, str, str) # id, filename, dir
    rename_requested = Signal(str, str, str) # id, current_filename, dir

    def __init__(self, download_id, filename, pages="N/A", size_mb="N/A", parent=None, author="Anonim", absolute_dir=""):
        super().__init__(parent)
        self.download_id = download_id
        self.filename = filename
        self.pages = pages
        self.size_mb = size_mb
        self.author = author
        from app.core.utils import get_downloads_dir
        self.absolute_dir = absolute_dir if absolute_dir else get_downloads_dir()
        self.setObjectName("downloadItem") 
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.init_ui()

    def init_ui(self):
        from PySide6.QtWidgets import QProgressBar
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Top row: filename and status
        top_layout = QHBoxLayout()
        self.lbl_filename = QLabel(self.filename)
        self.lbl_filename.setStyleSheet("font-weight: bold; font-size: 13px;")
        self.lbl_filename.setWordWrap(True)
        
        self.lbl_author = QLabel(f"Penulis: {self.author}")
        self.lbl_author.setStyleSheet("font-size: 11px; color: #495057;")
        self.lbl_author.setWordWrap(True)
        if not self.author or self.author.lower() in ['anonim', 'unknown', '']:
            self.lbl_author.hide()
        
        # Info label for pages/size
        self.lbl_info = QLabel(f"📄 {self.pages} Hal • 💾 {self.size_mb}")
        self.lbl_info.setStyleSheet("font-size: 11px; color: #6c757d;")
        
        self.lbl_status = QLabel("Queued")
        self.lbl_status.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        filename_vbox = QVBoxLayout()
        filename_vbox.setSpacing(2)
        filename_vbox.addWidget(self.lbl_filename)
        filename_vbox.addWidget(self.lbl_author)
        filename_vbox.addWidget(self.lbl_info)
        
        top_layout.addLayout(filename_vbox, stretch=1)
        top_layout.addWidget(self.lbl_status)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        
        # Bottom section: Stats and Buttons stacked vertically for better small-window support
        bottom_main = QVBoxLayout()
        bottom_main.setSpacing(8)
        
        self.lbl_stats = QLabel("0 MB / 0 MB • 0 KB/s")
        self.lbl_stats.setStyleSheet("font-size: 12px; color: #6c757d;")
        bottom_main.addWidget(self.lbl_stats)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(4)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        self.btn_split = QPushButton("✂️ Split")
        self.btn_split.setStyleSheet("background-color: #6f42c1; color: white; font-weight: bold; min-height: 32px; font-size: 11px;")
        self.btn_split.setFixedWidth(100)
        self.btn_split.setVisible(False)
        self.btn_split.clicked.connect(self.on_split_pdf)

        self.btn_rename = QPushButton("✏️ Rename")
        self.btn_rename.setStyleSheet("background-color: #0dcaf0; color: white; font-weight: bold; min-height: 32px; font-size: 11px;")
        self.btn_rename.setFixedWidth(100)
        self.btn_rename.setVisible(False)
        self.btn_rename.clicked.connect(self.on_rename_pdf)

        self.btn_open_file = QPushButton("📂 Buka")
        self.btn_open_file.setStyleSheet("background-color: #198754; color: white; font-weight: bold; min-height: 32px; font-size: 11px;")
        self.btn_open_file.setFixedWidth(100)
        self.btn_open_file.setVisible(False)
        self.btn_open_file.clicked.connect(self.on_open_file)

        self.btn_action = QPushButton("Cancel")
        self.btn_action.setObjectName("btnSecondary")
        self.btn_action.setStyleSheet("min-height: 32px; font-size: 11px;")
        self.btn_action.setToolTip("Batalkan unduhan aktif")
        self.btn_action.setFixedWidth(100)
        self.btn_action.clicked.connect(self.on_btn_action)
        
        buttons_layout.addWidget(self.btn_split)
        buttons_layout.addWidget(self.btn_rename)
        buttons_layout.addWidget(self.btn_open_file)
        buttons_layout.addWidget(self.btn_action)
        buttons_layout.addStretch()
        
        bottom_main.addLayout(buttons_layout)
        
        layout.addLayout(top_layout)
        layout.addWidget(self.progress_bar)
        layout.addLayout(bottom_main)
        
    def update_progress(self, downloaded, total, speed, status):
        percent = 0
        if total > 0:
            percent = int((downloaded / total) * 100)
            self.progress_bar.setValue(percent)
        else:
            self.progress_bar.setRange(0, 0) # Indeterminate
            
        # Format stats
        down_mb = downloaded / (1024*1024)
        total_mb = total / (1024*1024)
        self.lbl_stats.setText(f"{down_mb:.1f} MB / {total_mb:.1f} MB • {speed:.1f} KB/s")
        
        if status == "Downloading":
            self.lbl_status.setText(f"⏳ Downloading... {percent}%")
            self.lbl_status.setToolTip("Tombol Rename/Split akan muncul setelah download 100% (Selesai)")
            self.btn_action.setText("Cancel")
        else:
            self.lbl_status.setText(status)
            self.lbl_status.setToolTip("")
        
        if status in ["Completed", "Error", "Cancelled"]:
            self.progress_bar.setRange(0, 100)
            if status == "Completed":
                self.progress_bar.setValue(100)
                # Success Color
                self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #198754; }")
                self.btn_open_file.setVisible(True)
                self.btn_open_file.setText(f"Buka {self.filename.split('.')[-1].upper()}")
                self.btn_split.setVisible(True) # Show Split button
                self.btn_rename.setVisible(True) # Show Rename button
                self.btn_action.setText("Open Folder")
                self.lbl_status.setText("SELESAI ✅")
                self.lbl_status.setStyleSheet("font-weight: bold; color: #198754;")
            elif status == "Error":
                self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #dc3545; }")
                self.btn_action.setText("Remove")
                self.lbl_status.setStyleSheet("color: #dc3545;")
            else:
                self.progress_bar.setValue(0)
                self.btn_action.setText("Remove")

    def on_open_file(self):
        import os
        from pathlib import Path
        file_path = Path(self.absolute_dir) / self.filename
        if file_path.exists():
            if os.name == 'nt':
                os.startfile(str(file_path))
            else:
                import subprocess, sys
                subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', str(file_path)])

    def on_btn_action(self):
        text = self.btn_action.text()
        if text == "Cancel":
            self.cancel_requested.emit(self.download_id)
            self.lbl_status.setText("Cancelling...")
            self.btn_action.setEnabled(False)
        elif text == "Open Folder":
            import os
            from pathlib import Path
            downloads_dir = self.absolute_dir
            if os.name == 'nt':
                os.startfile(str(downloads_dir))
            else:
                import subprocess, sys
                subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', str(downloads_dir)])
        elif text == "Remove":
            self.deleteLater()

    def on_split_pdf(self):
        self.split_requested.emit(self.download_id, self.filename, self.absolute_dir)

    def on_rename_pdf(self):
        self.rename_requested.emit(self.download_id, self.filename, self.absolute_dir)
