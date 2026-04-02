import magic
from typing import Optional, Tuple
from pathlib import Path


class FileDetector:
    
    @staticmethod
    def detect_from_bytes(file_bytes: bytes) -> Tuple[str, bool]:
        mime = magic.Magic(mime=True)
        detected_mime = mime.from_buffer(file_bytes)
        
        is_supported = FileDetector._is_supported_mime(detected_mime)
        return detected_mime, is_supported
    
    @staticmethod
    def detect_from_extension(file_path: str) -> str:
        extension = Path(file_path).suffix.lower()
        mime_map = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.tiff': 'image/tiff',
            '.tif': 'image/tiff',
        }
        return mime_map.get(extension, 'application/octet-stream')
    
    @staticmethod
    def is_scanned_document(mime_type: str, content_hint: Optional[str] = None) -> bool:
        if mime_type.startswith('image/'):
            return True
        
        if mime_type == 'application/pdf':
            if content_hint:
                has_text = any([
                    'image' in content_hint.lower(),
                    'scan' in content_hint.lower(),
                    'ocr' in content_hint.lower()
                ])
                return not has_text
        
        return False
    
    @staticmethod
    def _is_supported_mime(mime_type: str) -> bool:
        supported_mimes = {
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/msword',
            'image/jpeg',
            'image/png',
            'image/gif',
            'image/bmp',
            'image/tiff',
        }
        return mime_type in supported_mimes
