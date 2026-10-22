import fitz
import httpx
import os

def test_peek_remote(url):
    print(f"Testing partial download and render: {url}")
    # Download first 1MB using Range header
    headers = {"Range": "bytes=0-1048575"}
    try:
        with httpx.Client(follow_redirects=True, timeout=30) as client:
            resp = client.get(url, headers=headers)
            print(f"Status: {resp.status_code}")
            if resp.status_code not in (200, 206):
                print("Failed to get partial content.")
                return False
            
            data = resp.content
            print(f"Downloaded {len(data)} bytes.")
            
            # Opening truncated PDF
            # PyMuPDF is quite robust with 'stream'
            try:
                # Open from stream directly
                doc = fitz.open(stream=data, filetype="pdf")
                print(f"Document opened. Pages detected: {doc.page_count}")
                if doc.page_count > 0:
                    page = doc[0]
                    pix = page.get_pixmap(matrix=fitz.Matrix(0.8, 0.8)) # Reasonable scale
                    print(f"Page 1 rendered: {pix.width}x{pix.height}")
                    doc.close()
                    return True
            except Exception as fe:
                print(f"Fitz error: {fe}")
                return False
    except Exception as e:
        print(f"Request error: {e}")
        return False

if __name__ == "__main__":
    # Test with a Shamela URL
    test_url = "https://shamela.org/pdf/96a75bf8048351d2222d7d9838022638"
    test_peek_remote(test_url)
