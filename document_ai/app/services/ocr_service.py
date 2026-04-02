import os
import logging
from typing import Dict, Any, Optional, List
from PIL import Image
import io

logger = logging.getLogger(__name__)


class OCRService:
    
    def __init__(self, provider: str = 'tesseract'):
        self.provider = provider
        self._tesseract = None
        self._easyocr = None
        self._google_vision = None
    
    def extract_text(self, file_path: str) -> Dict[str, Any]:
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if self.provider == 'tesseract':
            return self._extract_with_tesseract(file_path, file_ext)
        elif self.provider == 'easyocr':
            return self._extract_with_easyocr(file_path)
        elif self.provider == 'google_vision':
            return self._extract_with_google_vision(file_path)
        else:
            raise ValueError(f"Unknown OCR provider: {self.provider}")
    
    def _extract_with_tesseract(self, file_path: str, file_ext: str) -> Dict[str, Any]:
        try:
            import pytesseract
            
            if file_ext == '.pdf':
                try:
                    from pdf2image import convert_from_path
                    images = convert_from_path(file_path, dpi=300)
                    all_text = []
                    all_elements = []
                    
                    for i, image in enumerate(images, 1):
                        text = pytesseract.image_to_string(image)
                        all_text.append(text)
                        all_elements.append({
                            'page_number': i,
                            'text': text,
                            'type': 'OCRText'
                        })
                    
                    full_text = '\n\n'.join(all_text)
                except ImportError:
                    logger.warning("pdf2image not available, using direct text extraction")
                    full_text = self._extract_pdf_text_fallback(file_path)
                    all_elements = [{'page_number': 1, 'text': full_text, 'type': 'OCRText'}]
            else:
                image = Image.open(file_path)
                full_text = pytesseract.image_to_string(image)
                all_elements = [{
                    'page_number': 1,
                    'text': full_text,
                    'type': 'OCRText'
                }]
            
            return {
                'full_text': full_text or '',
                'elements': all_elements,
                'pages': len(all_elements),
                'provider': 'tesseract',
                'success': True
            }
        except ImportError as e:
            logger.error(f"Tesseract not available: {e}")
            return self._fallback_basic_extraction(file_path, file_ext)
        except Exception as e:
            logger.error(f"Error in Tesseract OCR: {e}")
            return self._fallback_basic_extraction(file_path, file_ext)
    
    def _extract_pdf_text_fallback(self, file_path: str) -> str:
        try:
            import fitz
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except:
            return ""
    
    def _extract_with_easyocr(self, file_path: str) -> Dict[str, Any]:
        try:
            import easyocr
            
            if self._easyocr is None:
                self._easyocr = easyocr.Reader(['en'], gpu=False)
            
            results = self._easyocr.readtext(file_path)
            
            full_text_parts = []
            elements = []
            
            for i, (bbox, text, confidence) in enumerate(results, 1):
                full_text_parts.append(text)
                elements.append({
                    'page_number': 1,
                    'text': text,
                    'confidence': confidence,
                    'type': 'OCRText'
                })
            
            full_text = ' '.join(full_text_parts)
            
            return {
                'full_text': full_text or '',
                'elements': elements,
                'pages': 1,
                'provider': 'easyocr',
                'success': True
            }
        except ImportError:
            logger.warning("EasyOCR not available, falling back to Tesseract")
            return self._extract_with_tesseract(file_path, os.path.splitext(file_path)[1].lower())
        except Exception as e:
            logger.error(f"Error in EasyOCR: {e}")
            return self._fallback_basic_extraction(file_path, os.path.splitext(file_path)[1].lower())
    
    def _extract_with_google_vision(self, file_path: str) -> Dict[str, Any]:
        try:
            from google.cloud import vision
            from google.cloud.vision_v1 import types
            
            client = vision.ImageAnnotatorClient()
            
            with io.open(file_path, 'rb') as f:
                content = f.read()
            
            image = vision.Image(content=content)
            response = client.document_text_detection(image=image)
            
            if response.full_text_annotation:
                full_text = response.full_text_annotation.text
                pages = []
                
                for page in response.full_text_annotation.pages:
                    page_text = ''
                    for block in page.blocks:
                        for paragraph in block.paragraphs:
                            for word in paragraph.words:
                                for symbol in word.symbols:
                                    page_text += symbol.text
                                    if symbol.property.detected_break:
                                        if symbol.property.detected_break.type == 1:
                                            page_text += ' '
                                        elif symbol.property.detected_break.type == 3:
                                            page_text += '\n'
                    pages.append({
                        'page_number': len(pages) + 1,
                        'text': page_text
                    })
                
                return {
                    'full_text': full_text or '',
                    'pages': pages,
                    'elements': [{'text': full_text, 'type': 'OCRText'}],
                    'provider': 'google_vision',
                    'success': True
                }
            
            return {'full_text': '', 'success': False, 'error': 'No text found'}
        except ImportError:
            logger.warning("Google Cloud Vision not available, falling back to Tesseract")
            return self._extract_with_tesseract(file_path, os.path.splitext(file_path)[1].lower())
        except Exception as e:
            logger.error(f"Error in Google Vision OCR: {e}")
            return self._fallback_basic_extraction(file_path, os.path.splitext(file_path)[1].lower())
    
    def _fallback_basic_extraction(self, file_path: str, file_ext: str) -> Dict[str, Any]:
        try:
            if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif']:
                image = Image.open(file_path)
                
                if hasattr(image, 'text') and image.text:
                    metadata_text = ' '.join(image.text.values())
                else:
                    metadata_text = f"[Image file: {os.path.basename(file_path)}]"
                
                return {
                    'full_text': metadata_text,
                    'elements': [{'page_number': 1, 'text': metadata_text, 'type': 'ImageMetadata'}],
                    'pages': 1,
                    'provider': 'fallback',
                    'success': True,
                    'warning': 'OCR not available, limited text extraction'
                }
            elif file_ext == '.pdf':
                try:
                    import fitz
                    doc = fitz.open(file_path)
                    text = ""
                    for page in doc:
                        text += page.get_text() + "\n\n"
                    doc.close()
                    
                    if text.strip():
                        return {
                            'full_text': text,
                            'elements': [{'page_number': 1, 'text': text, 'type': 'PDFText'}],
                            'pages': len(doc),
                            'provider': 'fallback_pymupdf',
                            'success': True
                        }
                except:
                    pass
                
                return {
                    'full_text': f"[PDF file: {os.path.basename(file_path)}]",
                    'elements': [],
                    'pages': 0,
                    'provider': 'fallback',
                    'success': True,
                    'warning': 'Unable to extract text from PDF'
                }
            else:
                return {
                    'full_text': f"[Document file: {os.path.basename(file_path)}]",
                    'elements': [],
                    'pages': 1,
                    'provider': 'fallback',
                    'success': True
                }
        except Exception as e:
            logger.error(f"Fallback extraction failed: {e}")
            return {
                'full_text': '',
                'elements': [],
                'pages': 0,
                'provider': 'none',
                'success': False,
                'error': str(e)
            }
