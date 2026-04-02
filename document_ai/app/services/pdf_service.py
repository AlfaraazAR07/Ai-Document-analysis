import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass

try:
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

try:
    from unstructured.partition.pdf import partition_pdf
    HAS_UNSTRUCTURED = True
except ImportError:
    HAS_UNSTRUCTURED = False

from app.core.logger import logger


@dataclass
class PDFPage:
    page_number: int
    text: str
    elements: List[Dict[str, Any]]


class PDFService:
    
    def __init__(self):
        self.supports_unstructured = HAS_UNSTRUCTURED
        self.supports_pypdf = HAS_PYPDF
    
    def extract_text(self, file_path: str, include_layout: bool = True) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        if include_layout and self.supports_unstructured:
            return self._extract_with_unstructured(file_path)
        elif self.supports_pypdf:
            return self._extract_with_pypdf(file_path)
        else:
            raise ImportError("No suitable PDF library available. Install pypdf or unstructured.")
    
    def _extract_with_unstructured(self, file_path: str) -> Dict[str, Any]:
        try:
            elements = partition_pdf(
                filename=file_path,
                strategy="hi_res",
                infer_table_structure=True,
                include_page_breaks=True
            )
            
            pages = []
            current_page = []
            current_page_num = 1
            
            for element in elements:
                element_dict = {
                    'type': type(element).__name__,
                    'text': str(element),
                    'metadata': element.metadata.to_dict() if hasattr(element, 'metadata') else {}
                }
                
                page_num = element_dict['metadata'].get('page_number', 1)
                
                if page_num != current_page_num and current_page:
                    pages.append({
                        'page_number': current_page_num,
                        'elements': current_page,
                        'text': ' '.join([e['text'] for e in current_page])
                    })
                    current_page = []
                    current_page_num = page_num
                
                current_page.append(element_dict)
            
            if current_page:
                pages.append({
                    'page_number': current_page_num,
                    'elements': current_page,
                    'text': ' '.join([e['text'] for e in current_page])
                })
            
            return {
                'pages': pages,
                'total_pages': len(pages),
                'full_text': ' '.join([p['text'] for p in pages]),
                'has_layout': True
            }
        except Exception as e:
            logger.error(f"Error extracting with unstructured: {e}")
            return self._extract_with_pypdf(file_path)
    
    def _extract_with_pypdf(self, file_path: str) -> Dict[str, Any]:
        reader = PdfReader(file_path)
        pages = []
        
        for i, page in enumerate(reader.pages, 1):
            text = page.extract_text() or ""
            pages.append({
                'page_number': i,
                'text': text,
                'elements': [{'type': 'Text', 'text': text, 'metadata': {}}],
            })
        
        return {
            'pages': pages,
            'total_pages': len(pages),
            'full_text': '\n\n'.join([p['text'] for p in pages]),
            'has_layout': False
        }
    
    def get_page_count(self, file_path: str) -> int:
        if self.supports_pypdf:
            reader = PdfReader(file_path)
            return len(reader.pages)
        return 0
