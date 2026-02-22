"""
PDF text extraction for AtlasMind
"""

import PyPDF2
from typing import Dict
import hashlib


def extract_text_from_pdf(pdf_file) -> Dict:
    """
    Extract text from uploaded PDF file
    
    Args:
        pdf_file: Gradio file upload object (has .name path)
    
    Returns:
        Dict with success status, pdf_id, and text or error message
    """
    try:
        # Generate unique ID for this PDF
        pdf_id = hashlib.md5(pdf_file.name.encode()).hexdigest()[:11]
        
        print(f"Processing PDF: {pdf_file.name}")
        print(f"PDF ID: {pdf_id}")
        
        # Open and read PDF
        with open(pdf_file.name, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            
            print(f"Total pages: {num_pages}")
            
            # Extract text from all pages
            full_text = []
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                if text.strip():  # Only add non-empty pages
                    full_text.append(text)
            
            combined_text = '\n\n'.join(full_text)
            
            if not combined_text.strip():
                return {
                    "success": False,
                    "error": "Could not extract text from PDF. Please use a text-based PDF (not scanned/image-based)."
                }
            
            print(f"Extracted {len(combined_text)} characters from {num_pages} pages")
            
            return {
                "success": True,
                "pdf_id": pdf_id,
                "text": combined_text,
                "num_pages": num_pages,
                "filename": pdf_file.name.split('\\')[-1].split('/')[-1]  # Get just filename
            }
            
    except Exception as e:
        print(f"PDF extraction error: {str(e)}")
        return {
            "success": False,
            "error": f"Error reading PDF: {str(e)}"
        }
