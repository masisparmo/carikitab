import os
import math
import logging
import fitz  # PyMuPDF is much faster for splitting
from pathlib import Path

logger = logging.getLogger(__name__)

class PdfSplitter:
    @staticmethod
    def split_by_pages(pdf_path, pages_per_part, output_dir=None, progress_callback=None):
        """Splits a PDF by page count using insert_pdf for accurate file sizes (FAST)."""
        try:
            doc = fitz.open(pdf_path)
            total_pages = doc.page_count
            
            if not output_dir:
                output_dir = Path(pdf_path).parent / "splits"
            else:
                output_dir = Path(output_dir)
                
            output_dir.mkdir(parents=True, exist_ok=True)
            
            base_name = Path(pdf_path).stem
            # Clean up base_name
            if base_name.rstrip().endswith('-'):
                base_name = base_name.rstrip()[:-1].strip()

            num_parts = math.ceil(total_pages / pages_per_part)
            
            splits = []
            for i in range(num_parts):
                if progress_callback:
                    progress_callback(i + 1, num_parts)
                    
                start = i * pages_per_part
                end = min(start + pages_per_part, total_pages)
                
                # New doc + insertion ensures only needed pages/resources are kept
                out_doc = fitz.open()
                out_doc.insert_pdf(doc, from_page=start, to_page=end-1)
                
                out_filename = f"{base_name}-{i+1}.pdf"
                out_path = output_dir / out_filename
                
                # garbage=1 is fast and removes unused objects (essential for small files)
                out_doc.save(str(out_path), garbage=1, deflate=False)
                out_doc.close()
                
                splits.append(str(out_path))
                logger.info(f"Created split: {out_path} (Pages {start}-{end-1})")
                
            doc.close()
            return splits
        except Exception as e:
            logger.error(f"Error splitting by pages: {e}")
            raise e

    @staticmethod
    def split_by_size(pdf_path, max_size_mb, output_dir=None, progress_callback=None):
        """Splits a PDF into parts by approximating size based on page ratio."""
        try:
            total_size_bytes = os.path.getsize(pdf_path)
            target_size_bytes = max_size_mb * 1024 * 1024
            
            if total_size_bytes <= target_size_bytes:
                return [str(pdf_path)]
                
            doc = fitz.open(pdf_path)
            total_pages = doc.page_count
            doc.close()
            
            num_parts = math.ceil(total_size_bytes / target_size_bytes)
            pages_per_part = math.ceil(total_pages / num_parts)
            
            return PdfSplitter.split_by_pages(pdf_path, pages_per_part, output_dir, progress_callback)
            
        except Exception as e:
            logger.error(f"Error splitting by size: {e}")
            raise e
