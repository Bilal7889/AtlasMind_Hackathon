"""
PDF text extraction for AtlasMind
"""

import hashlib
import os
from pathlib import Path
from typing import Dict

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False


def extract_text_from_pdf(file_path: str) -> Dict:
    """
    Extract plain text from a PDF file.

    Args:
        file_path: Path to the PDF file (e.g. from Gradio upload)

    Returns:
        Dict with success status, content_id, and text or error message
    """
    if not HAS_PYMUPDF:
        return {
            "success": False,
            "error": "PDF support not installed. Install with: pip install pymupdf"
        }

    if not file_path or not str(file_path).strip():
        return {"success": False, "error": "No file provided."}

    path = Path(file_path)
    if not path.exists():
        return {"success": False, "error": "File not found."}
    if path.suffix.lower() != ".pdf":
        return {"success": False, "error": "File is not a PDF."}

    try:
        doc = fitz.open(path)
        parts = []
        for page in doc:
            parts.append(page.get_text())
        doc.close()
        full_text = "\n".join(parts).strip()
    except Exception as e:
        return {"success": False, "error": f"Could not read PDF: {str(e)}"}

    if not full_text:
        return {"success": False, "error": "No text could be extracted from the PDF."}

    # Stable content_id for same file content (for vector DB collection name)
    content_id = hashlib.sha256(full_text.encode("utf-8")[:50000]).hexdigest()[:16]
    content_id = f"pdf_{content_id}"

    return {
        "success": True,
        "content_id": content_id,
        "transcript": full_text,
    }
