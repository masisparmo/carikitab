# Cari Kitab - Digital Library Assistant 📖🔍

Aplikasi desktop (GUI) modern berbasis Python & PySide6 untuk mencari, mengunduh, membaca, memotong, dan menelaah kitab-kitab klasik Islam (*Kutubut Turats*) dari berbagai sumber terpercaya seperti **Maktabah Shamela**, **Internet Archive**, dan **Google**.

---

## 🌟 Fitur Utama

1. **Multi-Source Smart Search**
   - Pencarian otomatis ke Maktabah Shamela, Internet Archive, Google, dan mesin pencari lainnya.
   - Mendukung transliterasi otomatis dari huruf Latin ke huruf/istilah Arab secara cerdas.
2. **AI Konsultan Kitab**
   - Diskusi interaktif dengan AI (didukung oleh Google Gemini) untuk rekomendasi kitab, pemetaan tema, penjelasan sanad/pengarang, dan fikih/hadits.
   - Rotasi API Key otomatis (*Gemini Key Rotator*) untuk keandalan maksimal tanpa batas kuota mendadak.
   - Integrasi langsung: Klik nama kitab di dalam percakapan AI untuk langsung mencari kitab tersebut.
3. **Download Manager & Resumption**
   - Pengunduhan PDF berjalan di latar belakang tanpa membuat aplikasi macet (*non-blocking async*).
   - Riwayat unduhan tersimpan rapi di tab *Riwayat*.
4. **Built-in Document Viewer**
   - Penampil dokumen PDF & EPUB langsung di dalam aplikasi.
   - Fitur zoom in/out, navigasi halaman, dan ekstraksi teks ke format TXT / DOCX.
5. **PDF Splitter (Alat Pemotong Dokumen)**
   - Potong file PDF kitab per juz, per bab, atau rentang halaman tertentu secara akurat dan cepat.
6. **Desain Modern & Ramah Pengguna**
   - Pilihan Tema Gelap (*Dark Mode*) & Tema Terang (*Light Mode*).
   - Pilihan Bahasa Indonesia 🇮🇩 dan English 🇬🇧.
   - Panduan lengkap dan indeks daftar referensi kitab-kitab klasik per disiplin ilmu (Aqidah, Tafsir, Hadits, Fikih, dll).

---

## 🛠️ Persyaratan Sistem

- **Python**: Versi 3.10, 3.11, atau 3.12 (disarankan Python 3.12)
- **Sistem Operasi**: Windows 10/11 (atau Linux / macOS dengan penyesuaian lingkungan)
- **Koneksi Internet**: Untuk pencarian sumber daring dan pengunduhan PDF

---

## 🚀 Panduan Instalasi & Menjalankan

### 1. Clone Repository
```bash
git clone https://github.com/masisparmo/carikitab.git
cd carikitab
```

### 2. Buat & Aktifkan Virtual Environment (Opsional namun disarankan)
```bash
python -m venv .venv
# Di Windows:
.venv\Scripts\activate
# Di Linux/macOS:
source .venv/bin/activate
```

### 3. Pasang Dependencies
```bash
pip install -r requirements.txt
```

### 4. Pasang Browser Playwright
```bash
playwright install chromium
```

### 5. Konfigurasi Environment (.env)
Salin berkas `.env.example` menjadi `.env` dan masukkan API Key Gemini Anda:
```bash
cp .env.example .env
```
Isi `.env`:
```env
GEMINI_API_KEYS=AIzaSy...,AIzaSy...
```
*(Anda dapat memasukkan beberapa API Key yang dipisahkan dengan tanda koma `,` untuk rotasi otomatis)*.

### 6. Jalankan Aplikasi
```bash
python -m app.main
```

---

## 📦 Build Standalone Executable (.exe)

Aplikasi ini sudah dilengkapi dengan spesifikasi PyInstaller dan installer Inno Setup:

```bash
# Build binary via PyInstaller:
pyinstaller cari_kitab.spec

# Atau versi single executable:
pyinstaller cari_kitab_onefile.spec
```

Hasil build akan berada di folder `dist/CariKitab/`. Anda juga dapat mengompilasi installer setup menggunakan file [installer.iss](installer.iss) dengan Inno Setup Compiler.

---

## 📂 Struktur Direktori

```
carikitab/
├── app/
│   ├── assets/            # Ikon, logo, stylesheets (.qss), dan konten panduan
│   ├── core/              # Scraper (Shamela, Archive, Google), downloader, utils, transliterasi
│   ├── services/          # Gemini AI assistant, key rotator, LLM caching
│   ├── ui/                # Komponen antarmuka PySide6
│   └── main.py            # Entry point aplikasi utama
├── .env.example           # Template environment variable
├── .gitignore             # Pengabaian berkas binary, PDF, dan secrets
├── requirements.txt       # Daftar dependensi Python
├── cari_kitab.spec        # Konfigurasi build PyInstaller
└── installer.iss          # Skrip pembuatan installer Inno Setup
```

---

## 📄 Lisensi

Proyek ini dilisensikan di bawah lisensi yang tertera pada berkas [LICENSE](LICENSE).
