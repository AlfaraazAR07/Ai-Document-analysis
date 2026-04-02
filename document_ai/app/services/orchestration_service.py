import time
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from app.services.parser_service import ParserService
from app.services.cleaning_service import CleaningService
from app.services.entity_service import EntityService
from app.services.summary_service import SummaryService
from app.services.sentiment_service import SentimentService
from app.utils.base64_utils import decode_base64_to_file, cleanup_temp_file
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class OrchestrationService:
    
    def __init__(self):
        self.parser = ParserService()
        self.cleaner = CleaningService()
        self.entity_extractor = EntityService()
        self.summary_generator = SummaryService()
        self.sentiment_analyzer = SentimentService()
        self.settings = get_settings()
    
    async def process_document(
        self,
        file_name: str,
        file_data_base64: str,
        mime_type: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        start_time = time.time()
        temp_file_path = None
        
        try:
            options = options or {}
            include_layout = options.get('include_layout', True)
            ocr_provider = options.get('ocr_provider', self.settings.OCR_PROVIDER)
            use_llm = options.get('use_llm', False)
            
            file_path, file_ext = decode_base64_to_file(
                file_data_base64,
                file_name,
                self.settings.TEMP_UPLOAD_DIR
            )
            temp_file_path = file_path
            
            file_type = self._determine_file_type(file_ext, mime_type)
            
            parse_result = self.parser.parse(
                file_path,
                file_type,
                include_layout,
                ocr_provider
            )
            
            if not parse_result.get('success'):
                return self._error_response(
                    file_name,
                    parse_result.get('error', 'Failed to parse document'),
                    start_time
                )
            
            full_text = parse_result.get('full_text', '')
            full_text = self.cleaner.clean_text(full_text)
            full_text = self.cleaner.truncate_text(full_text)
            
            language = self.cleaner.extract_language_hint(full_text)
            
            entities = self.entity_extractor.extract_entities(full_text)
            
            summary = self.summary_generator.generate_summary(full_text)
            
            sentiment = self.sentiment_analyzer.analyze_sentiment(full_text, use_llm=use_llm)
            
            layout_elements = self._extract_layout_elements(parse_result)
            
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            return {
                'success': True,
                'document_type': file_type,
                'source_type': parse_result.get('source_type', 'unknown'),
                'summary': summary,
                'sentiment': sentiment,
                'entities': entities,
                'layout_elements': layout_elements,
                'metadata': {
                    'pages': parse_result.get('total_pages', 1),
                    'language': language,
                    'processing_time_ms': processing_time_ms,
                    'ocr_used': parse_result.get('ocr_used', False)
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing document: {e}", exc_info=True)
            return self._error_response(file_name, str(e), start_time)
        
        finally:
            if temp_file_path:
                cleanup_temp_file(temp_file_path)
    
    def _determine_file_type(self, file_ext: str, mime_type: str) -> str:
        if file_ext == '.pdf' or 'pdf' in mime_type.lower():
            return 'pdf'
        elif file_ext in ['.docx', '.doc'] or 'wordprocessingml' in mime_type.lower():
            return 'docx'
        elif file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif'] or 'image' in mime_type.lower():
            return 'image'
        else:
            return file_ext.strip('.')
    
    def _extract_layout_elements(self, parse_result: Dict[str, Any]) -> list:
        layout_elements = []
        
        pages = parse_result.get('pages', [])
        for page in pages:
            page_num = page.get('page_number', 1)
            elements = page.get('elements', [])
            
            for element in elements:
                if element.get('text') and element['text'].strip():
                    layout_elements.append({
                        'type': element.get('type', 'Text'),
                        'text': element['text'].strip()[:500],
                        'page': page_num
                    })
        
        return layout_elements[:100]
    
    def _error_response(self, file_name: str, error_message: str, start_time: float) -> Dict[str, Any]:
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return {
            'success': False,
            'document_type': None,
            'source_type': None,
            'summary': None,
            'sentiment': None,
            'entities': [],
            'layout_elements': [],
            'metadata': {
                'pages': 0,
                'language': 'unknown',
                'processing_time_ms': processing_time_ms,
                'ocr_used': False
            },
            'error': error_message
        }
