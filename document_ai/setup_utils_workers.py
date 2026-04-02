#!/usr/bin/env python3
"""
Script to populate utils and workers files for Document AI
"""
import os

def create_file(path, content):
    """Create a file with the given content"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Created: {path}')

def main():
    base = os.path.dirname(os.path.abspath(__file__))
    
    # Base64 Utils
    create_file(f'{base}/app/utils/base64_utils.py', '''import base64
import os
import tempfile
from typing import Tuple, Optional
from pathlib import Path


def decode_base64_to_bytes(base64_string: str) -> bytes:
    try:
        return base64.b64decode(base64_string)
    except Exception as e:
        raise ValueError(f"Failed to decode base64 string: {str(e)}")


def decode_base64_to_file(base64_string: str, file_name: str, output_dir: Optional[str] = None) -> Tuple[str, str]:
    if output_dir is None:
        output_dir = tempfile.gettempdir()
    
    os.makedirs(output_dir, exist_ok=True)
    
    file_extension = Path(file_name).suffix.lower()
    safe_name = Path(file_name).stem
    temp_file_path = os.path.join(output_dir, f"{safe_name}_{os.urandom(8).hex()}{file_extension}")
    
    file_bytes = decode_base64_to_bytes(base64_string)
    
    with open(temp_file_path, 'wb') as f:
        f.write(file_bytes)
    
    return temp_file_path, file_extension


def encode_file_to_base64(file_path: str) -> str:
    with open(file_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


def get_mime_type(file_extension: str) -> str:
    mime_types = {
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
    return mime_types.get(file_extension.lower(), 'application/octet-stream')


def is_supported_format(file_extension: str) -> bool:
    supported_extensions = {'.pdf', '.docx', '.doc', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif'}
    return file_extension.lower() in supported_extensions


def cleanup_temp_file(file_path: str) -> None:
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception:
        pass
''')
    
    # Regex Extractors
    create_file(f'{base}/app/utils/regex_extractors.py', '''import re
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class RegexMatch:
    text: str
    confidence: float = 0.9
    label: str = ""


class RegexExtractors:
    
    MONEY_PATTERNS = [
        r'₹\\s*[\\d,]+\\.?\\d*',
        r'\\$\\s*[\\d,]+\\.?\\d*',
        r'Rs\\.?\\s*[\\d,]+\\.?\\d*',
        r'INR\\s*[\\d,]+\\.?\\d*',
        r'[\\d,]+\\.?\\d*\\s*(?:rupees?|Rs\\.?|INR)',
        r'[\\d,]+\\.?\\d*\\s*(?:dollars?|USD)',
        r'[\\d,]+\\.?\\d*\\s*(?:pounds?|GBP)',
        r'[\\d,]+\\.?\\d*\\s*(?:euros?|EUR)',
    ]
    
    DATE_PATTERNS = [
        r'\\d{1,2}\\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\\s+\\d{4}',
        r'\\d{1,2}/\\d{1,2}/\\d{4}',
        r'\\d{4}-\\d{2}-\\d{2}',
        r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\\s+\\d{1,2},?\\s+\\d{4}',
        r'\\d{1,2}\\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\\s+\\d{4}',
    ]
    
    EMAIL_PATTERN = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}'
    PHONE_PATTERN = r'(?:\\+?\\d{1,3}[-.\\s]?)?\\(?\\d{3}\\)?[-.\\s]?\\d{3}[-.\\s]?\\d{4}'
    URL_PATTERN = r'https?://[^\\s<>\\"]+'
    ADDRESS_PATTERN = r'\\d+\\s+[\\w\\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)'
    
    @classmethod
    def extract_money(cls, text: str) -> List[RegexMatch]:
        matches = []
        for pattern in cls.MONEY_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                matches.append(RegexMatch(
                    text=match.group().strip(),
                    confidence=0.95,
                    label="MONEY"
                ))
        return matches
    
    @classmethod
    def extract_dates(cls, text: str) -> List[RegexMatch]:
        matches = []
        for pattern in cls.DATE_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                matches.append(RegexMatch(
                    text=match.group().strip(),
                    confidence=0.95,
                    label="DATE"
                ))
        return matches
    
    @classmethod
    def extract_emails(cls, text: str) -> List[RegexMatch]:
        matches = []
        for match in re.finditer(cls.EMAIL_PATTERN, text):
            matches.append(RegexMatch(
                text=match.group().strip(),
                confidence=0.95,
                label="EMAIL"
            ))
        return matches
    
    @classmethod
    def extract_phones(cls, text: str) -> List[RegexMatch]:
        matches = []
        for match in re.finditer(cls.PHONE_PATTERN, text):
            matches.append(RegexMatch(
                text=match.group().strip(),
                confidence=0.90,
                label="PHONE"
            ))
        return matches
    
    @classmethod
    def extract_urls(cls, text: str) -> List[RegexMatch]:
        matches = []
        for match in re.finditer(cls.URL_PATTERN, text):
            matches.append(RegexMatch(
                text=match.group().strip(),
                confidence=0.95,
                label="URL"
            ))
        return matches
    
    @classmethod
    def extract_all(cls, text: str) -> Dict[str, List[RegexMatch]]:
        return {
            'money': cls.extract_money(text),
            'dates': cls.extract_dates(text),
            'emails': cls.extract_emails(text),
            'phones': cls.extract_phones(text),
            'urls': cls.extract_urls(text),
        }
''')
    
    # File Detector
    create_file(f'{base}/app/services/file_detector.py', '''import magic
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
''')
    
    # Celery Tasks
    create_file(f'{base}/app/workers/tasks.py', '''from celery import Celery
import asyncio
from typing import Dict, Any, Optional

from app.core.config import get_settings
from app.services.orchestration_service import OrchestrationService

settings = get_settings()

celery_app = Celery(
    'document_ai',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
)


@celery_app.task(bind=True, name='process_document_async')
def process_document_async(self, file_name: str, file_data_base64: str, 
                           mime_type: str, options: Optional[Dict[str, Any]] = None):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        orchestrator = OrchestrationService()
        result = loop.run_until_complete(
            orchestrator.process_document(file_name, file_data_base64, mime_type, options)
        )
        
        loop.close()
        
        return result
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
''')
    
    print("\\nAll utils and workers files created successfully!")

if __name__ == '__main__':
    main()
