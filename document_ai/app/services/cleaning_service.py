import re
from typing import List, Dict, Any


class CleaningService:
    
    @staticmethod
    def clean_text(text: str) -> str:
        text = CleaningService._remove_excessive_whitespace(text)
        text = CleaningService._fix_encoding_issues(text)
        text = CleaningService._normalize_unicode(text)
        text = CleaningService._remove_control_characters(text)
        
        return text.strip()
    
    @staticmethod
    def _remove_excessive_whitespace(text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text
    
    @staticmethod
    def _fix_encoding_issues(text: str) -> str:
        replacements = {
            '\u2018': "'",
            '\u2019': "'",
            '\u201c': '"',
            '\u201d': '"',
            '\u2013': '-',
            '\u2014': '-',
            '\u00a0': ' ',
            '\u2022': '*',
            '\u2023': '*',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    @staticmethod
    def _normalize_unicode(text: str) -> str:
        import unicodedata
        return unicodedata.normalize('NFKC', text)
    
    @staticmethod
    def _remove_control_characters(text: str) -> str:
        return ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    
    @staticmethod
    def split_into_sentences(text: str) -> List[str]:
        sentence_endings = r'(?<=[.!?])\s+'
        sentences = re.split(sentence_endings, text)
        return [s.strip() for s in sentences if s.strip()]
    
    @staticmethod
    def extract_language_hint(text: str) -> str:
        common_english_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
            'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
            'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she'
        }
        
        words = re.findall(r'\b\w+\b', text.lower())
        
        if not words:
            return 'unknown'
        
        english_word_count = sum(1 for word in words if word in common_english_words)
        english_ratio = english_word_count / len(words)
        
        if english_ratio > 0.1:
            return 'en'
        
        return 'unknown'
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100000) -> str:
        if len(text) <= max_length:
            return text
        
        return text[:max_length]
