#!/usr/bin/env python3
import os

base_path = os.path.dirname(os.path.abspath(__file__))

service_files = {
    'app/services/parser_service.py': '''from typing import Dict, Any, Optional
from app.services.pdf_service import PDFService
from app.services.docx_service import DOCXService
from app.services.image_service import ImageService
from app.services.ocr_service import OCRService


class ParserService:
    
    def __init__(self):
        self.pdf_service = PDFService()
        self.docx_service = DOCXService()
        self.image_service = ImageService()
    
    def parse(self, file_path: str, file_type: str, include_layout: bool = True, 
              ocr_provider: str = 'tesseract') -> Dict[str, Any]:
        file_type = file_type.lower()
        
        if file_type == 'pdf':
            return self._parse_pdf(file_path, include_layout)
        elif file_type in ['docx', 'doc']:
            return self._parse_docx(file_path, include_layout)
        elif file_type in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'tif', 'image']:
            return self._parse_image(file_path, ocr_provider)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def _parse_pdf(self, file_path: str, include_layout: bool) -> Dict[str, Any]:
        try:
            result = self.pdf_service.extract_text(file_path, include_layout)
            return {
                'success': True,
                'full_text': result['full_text'],
                'pages': result.get('pages', []),
                'total_pages': result.get('total_pages', 0),
                'has_layout': result.get('has_layout', False),
                'source_type': 'native' if result.get('has_layout') else 'scanned',
                'document_type': 'pdf'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'document_type': 'pdf'
            }
    
    def _parse_docx(self, file_path: str, include_layout: bool) -> Dict[str, Any]:
        try:
            result = self.docx_service.extract_text(file_path, include_layout)
            return {
                'success': True,
                'full_text': result['full_text'],
                'pages': result.get('pages', []),
                'total_pages': result.get('total_pages', 0),
                'has_layout': result.get('has_layout', False),
                'source_type': 'native',
                'document_type': 'docx'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'document_type': 'docx'
            }
    
    def _parse_image(self, file_path: str, ocr_provider: str) -> Dict[str, Any]:
        try:
            ocr_service = OCRService(provider=ocr_provider)
            result = ocr_service.extract_text(file_path)
            
            return {
                'success': result.get('success', False),
                'full_text': result.get('full_text', ''),
                'pages': result.get('pages', []),
                'total_pages': result.get('pages', 1),
                'has_layout': False,
                'source_type': 'scanned',
                'document_type': 'image',
                'ocr_used': True,
                'ocr_provider': result.get('provider', ocr_provider)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'document_type': 'image',
                'ocr_used': True
            }
''',
}

for filepath, content in service_files.items():
    full_path = os.path.join(base_path, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Created: {filepath}')

print('Done!')
