import re
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class RegexMatch:
    text: str
    confidence: float = 0.9
    label: str = ""


class RegexExtractors:
    
    MONEY_PATTERNS = [
        r'₹\s*[\d,]+\.?\d*',
        r'\$\s*[\d,]+\.?\d*',
        r'Rs\.?\s*[\d,]+\.?\d*',
        r'INR\s*[\d,]+\.?\d*',
        r'[\d,]+\.?\d*\s*(?:rupees?|Rs\.?|INR)',
        r'[\d,]+\.?\d*\s*(?:dollars?|USD)',
        r'[\d,]+\.?\d*\s*(?:pounds?|GBP)',
        r'[\d,]+\.?\d*\s*(?:euros?|EUR)',
    ]
    
    DATE_PATTERNS = [
        r'\d{1,2}\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}',
        r'\d{1,2}/\d{1,2}/\d{4}',
        r'\d{4}-\d{2}-\d{2}',
        r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}',
        r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}',
    ]
    
    EMAIL_PATTERN = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    PHONE_PATTERN = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    URL_PATTERN = r'https?://[^\s<>\"]+'
    ADDRESS_PATTERN = r'\d+\s+[\w\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)'
    
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
