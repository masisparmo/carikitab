"""
archive_fetcher.py
Mengambil metadata file dari Archive.org Metadata API.
Menyediakan daftar PDF, PDF With Text, dan Full Text untuk sebuah item Archive.org.
"""
import logging
import re
import asyncio
from typing import Dict, List

logger = logging.getLogger(__name__)


def extract_archive_identifier(detail_url: str) -> str:
    """
    Ekstrak identifier Archive.org dari URL detail page.
    Contoh:
      https://archive.org/details/1-tafsir-ibnu-katsir-surat-1-2/0%20Tafsir...
      -> "1-tafsir-ibnu-katsir-surat-1-2"
    """
    # Match: archive.org/details/{identifier}[/...]
    m = re.search(r'archive\.org/(?:details|stream|download)/([^/?#]+)', detail_url)
    if m:
        return m.group(1)
    return ""


def build_download_url(server: str, directory: str, filename: str) -> str:
    """Membangun URL download langsung dari archive.org."""
    # Format: https://{server}{directory}/{encoded_filename}
    from urllib.parse import quote
    encoded = quote(filename, safe='')
    return f"https://{server}{directory}/{encoded}"


async def fetch_archive_files(detail_url: str) -> Dict[str, List[Dict]]:
    """
    Mengambil daftar file dari Archive.org Metadata API.

    Returns dict dengan key:
        - "pdf_files"       : PDF scan asli (Image Container PDF)
        - "pdf_text_files"  : PDF dengan text layer (Additional Text PDF)
        - "full_text_files" : File teks murni OCR (DjVuTXT)
        - "identifier"      : identifier archive.org
        - "title"           : judul koleksi (dari metadata)
        - "error"           : pesan error jika gagal (None jika sukses)

    Setiap file adalah dict: {name, url, size_mb, size_bytes}
    """
    result = {
        "pdf_files": [],
        "pdf_text_files": [],
        "full_text_files": [],
        "identifier": "",
        "title": "",
        "pages": None,
        "error": None,
    }

    identifier = extract_archive_identifier(detail_url)
    if not identifier:
        result["error"] = f"Tidak dapat mengekstrak identifier dari URL: {detail_url}"
        logger.warning(result["error"])
        return result

    result["identifier"] = identifier

    api_url = f"https://archive.org/metadata/{identifier}"
    logger.info(f"[ArchiveFetcher] Fetching metadata: {api_url}")

    try:
        import httpx
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            resp = await client.get(api_url, headers=headers)
            resp.raise_for_status()
            data = resp.json()

    except Exception as e:
        result["error"] = f"Gagal mengambil metadata dari archive.org: {e}"
        logger.error(result["error"])
        return result

    # Ambil server dan direktori untuk membangun URL download
    server = data.get("server", "archive.org")
    directory = data.get("dir", f"/0/items/{identifier}")

    # Ambil judul dan halaman dari metadata
    meta = data.get("metadata", {})
    result["title"] = meta.get("title", identifier)
    
    # Deteksi jumlah halaman: Cek berbagai field umum di archive.org
    page_fields = ["pages", "imagecount", "page_count", "image_count", "pagenumber", "page_number", "pagecount", "total_pages"]
    pages_found = None
    for field in page_fields:
        val = meta.get(field)
        if val and str(val).isdigit() and int(val) > 0:
            pages_found = str(val)
            break
            
    result["pages"] = pages_found

    files = data.get("files", [])
    logger.info(f"[ArchiveFetcher] Total files: {len(files)} untuk '{result['title']}'")

    for f in files:
        fmt = f.get("format", "")
        name = f.get("name", "")
        size_bytes_str = f.get("size", "0")

        try:
            size_bytes = int(size_bytes_str)
        except (ValueError, TypeError):
            size_bytes = 0

        size_mb = f"{size_bytes / (1024 * 1024):.1f} MB" if size_bytes > 0 else "N/A"

        file_info = {
            "name": name,
            "url": build_download_url(server, directory, name),
            "size_bytes": size_bytes,
            "size_mb": size_mb,
        }

        # Klasifikasikan berdasarkan format (lebih fleksibel)
        fmt_lower = fmt.lower()
        
        # 1. PDF Scan / Original
        if any(x in fmt_lower for x in ["image container pdf", "text pdf"]) or fmt_lower == "pdf":
            result["pdf_files"].append(file_info)
            # Ambil pages dari metadata file jika root tidak ada
            if not result["pages"] and f.get("pages"):
                result["pages"] = f.get("pages")
        
        # 2. PDF With Text / Searchable
        elif "additional text pdf" in fmt_lower or "searchable pdf" in fmt_lower:
            result["pdf_text_files"].append(file_info)
            if not result["pages"] and f.get("pages"):
                result["pages"] = f.get("pages")
                
        # 3. Full Text (TXT / DjVuTXT)
        elif any(x in fmt_lower for x in ["djvutxt", "txt", "djvu txt"]):
            result["full_text_files"].append(file_info)

        # 4. Fallback Page Count dari JP2 ZIP (Sangat Akurat)
        elif "single page processed jp2 zip" in fmt_lower:
            if not result["pages"] and f.get("filecount"):
                result["pages"] = f.get("filecount")

    # Urutkan berdasarkan nama agar tampil rapi
    for key in ("pdf_files", "pdf_text_files", "full_text_files"):
        result[key].sort(key=lambda x: x["name"])

    logger.info(
        f"[ArchiveFetcher] Hasil: {len(result['pdf_files'])} PDF, "
        f"{len(result['pdf_text_files'])} PDF With Text, "
        f"{len(result['full_text_files'])} Full Text"
    )
    return result


def is_archive_url(url: str) -> bool:
    """Cek apakah URL berasal dari Archive.org."""
    return "archive.org" in url.lower()
