#!/usr/bin/env python3
"""
Script to populate remaining service files for Document AI
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
    
    # Cleaning Service
    create_file(f'{base}/app/services/cleaning_service.py', '''import re
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
        text = re.sub(r'\\s+', ' ', text)
        text = re.sub(r'\\n\\s*\\n', '\\n\\n', text)
        return text
    
    @staticmethod
    def _fix_encoding_issues(text: str) -> str:
        replacements = {
            '\\u2018': "'",
            '\\u2019': "'",
            '\\u201c': '"',
            '\\u201d': '"',
            '\\u2013': '-',
            '\\u2014': '-',
            '\\u00a0': ' ',
            '\\u2022': '*',
            '\\u2023': '*',
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
        return ''.join(char for char in text if ord(char) >= 32 or char in '\\n\\r\\t')
    
    @staticmethod
    def split_into_sentences(text: str) -> List[str]:
        sentence_endings = r'(?<=[.!?])\\s+'
        sentences = re.split(sentence_endings, text)
        return [s.strip() for s in sentences if s.strip()]
    
    @staticmethod
    def extract_language_hint(text: str) -> str:
        common_english_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
            'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
            'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she'
        }
        
        words = re.findall(r'\\b\\w+\\b', text.lower())
        
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
''')
    
    # Entity Service
    create_file(f'{base}/app/services/entity_service.py', '''import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

try:
    import spacy
    HAS_SPACY = True
except ImportError:
    HAS_SPACY = False


class EntityService:
    
    def __init__(self):
        self._nlp = None
        if HAS_SPACY:
            try:
                self._nlp = spacy.load('en_core_web_sm')
            except OSError:
                logger.warning("spaCy model 'en_core_web_sm' not available. Entity extraction will be limited.")
    
    def extract_entities(self, text: str, use_llm: bool = False) -> List[Dict[str, Any]]:
        if not text or len(text.strip()) < 10:
            return []
        
        entities = []
        
        if self._nlp:
            entities.extend(self._extract_with_spacy(text))
        
        entities.extend(self._extract_with_regex(text))
        
        entities = self._deduplicate_entities(entities)
        
        return entities
    
    def _extract_with_spacy(self, text: str) -> List[Dict[str, Any]]:
        try:
            doc = self._nlp(text[:100000])
            
            entities = []
            for ent in doc.ents:
                entities.append({
                    'text': ent.text.strip(),
                    'label': ent.label_,
                    'confidence': 0.9
                })
            
            return entities
        except Exception as e:
            logger.error(f"Error in spaCy entity extraction: {e}")
            return []
    
    def _extract_with_regex(self, text: str) -> List[Dict[str, Any]]:
        from app.utils.regex_extractors import RegexExtractors
        
        entities = []
        
        regex_results = RegexExtractors.extract_all(text)
        
        label_map = {
            'money': 'MONEY',
            'dates': 'DATE',
            'emails': 'EMAIL',
            'phones': 'PHONE',
            'urls': 'URL'
        }
        
        for key, matches in regex_results.items():
            label = label_map.get(key, key.upper())
            for match in matches:
                entities.append({
                    'text': match.text,
                    'label': label,
                    'confidence': match.confidence
                })
        
        return entities
    
    def _deduplicate_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen = set()
        unique_entities = []
        
        for entity in entities:
            key = (entity['text'].lower().strip(), entity['label'])
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        return unique_entities
    
    def extract_structured_entities(self, text: str) -> Dict[str, List[str]]:
        entities = self.extract_entities(text)
        
        structured = {
            'PERSON': [],
            'ORG': [],
            'GPE': [],
            'DATE': [],
            'MONEY': [],
            'EMAIL': [],
            'PHONE': [],
            'URL': []
        }
        
        for entity in entities:
            label = entity['label']
            if label in structured:
                structured[label].append(entity['text'])
        
        return structured
''')
    
    # Summary Service
    create_file(f'{base}/app/services/summary_service.py', '''import logging
from typing import Optional, Dict, Any
import os

logger = logging.getLogger(__name__)


class SummaryService:
    
    def __init__(self, llm_provider: str = 'openai', model: str = 'gpt-4-turbo-preview'):
        self.llm_provider = llm_provider
        self.model = model
        self._client = None
    
    def generate_summary(self, text: str, max_length: int = 500) -> str:
        if not text or len(text.strip()) < 50:
            return text
        
        if self.llm_provider == 'openai':
            return self._generate_with_openai(text, max_length)
        elif self.llm_provider == 'anthropic':
            return self._generate_with_anthropic(text, max_length)
        else:
            return self._fallback_summary(text, max_length)
    
    def _generate_with_openai(self, text: str, max_length: int) -> str:
        try:
            from openai import OpenAI
            
            if self._client is None:
                api_key = os.getenv('OPENAI_API_KEY')
                if not api_key:
                    logger.warning("OpenAI API key not found, using fallback summarization")
                    return self._fallback_summary(text, max_length)
                self._client = OpenAI(api_key=api_key)
            
            truncated_text = text[:15000]
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a document summarization assistant. Provide a concise summary of the document in no more than {max_length} words. Focus on the main points, key entities mentioned, and important dates or amounts."
                    },
                    {
                        "role": "user",
                        "content": f"Summarize the following document:\\n\\n{truncated_text}"
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error in OpenAI summarization: {e}")
            return self._fallback_summary(text, max_length)
    
    def _generate_with_anthropic(self, text: str, max_length: int) -> str:
        try:
            from anthropic import Anthropic
            
            if self._client is None:
                api_key = os.getenv('ANTHROPIC_API_KEY')
                if not api_key:
                    logger.warning("Anthropic API key not found, using fallback summarization")
                    return self._fallback_summary(text, max_length)
                self._client = Anthropic(api_key=api_key)
            
            truncated_text = text[:15000]
            
            response = self._client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": f"Summarize the following document concisely in no more than {max_length} words. Focus on main points and key entities:\\n\\n{truncated_text}"
                    }
                ]
            )
            
            return response.content[0].text.strip()
        except Exception as e:
            logger.error(f"Error in Anthropic summarization: {e}")
            return self._fallback_summary(text, max_length)
    
    def _fallback_summary(self, text: str, max_length: int) -> str:
        sentences = text.replace('\\n', ' ').split('. ')
        
        if len(sentences) <= 3:
            return text[:max_length * 6]
        
        first_sentences = sentences[:3]
        summary = '. '.join(first_sentences)
        
        if len(summary) > max_length * 6:
            summary = summary[:max_length * 6]
        
        return summary.strip()
''')
    
    # Sentiment Service
    create_file(f'{base}/app/services/sentiment_service.py', '''import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class SentimentService:
    
    def __init__(self):
        self._vader_analyzer = None
        self._textblob_analyzer = None
    
    def analyze_sentiment(self, text: str, use_llm: bool = False) -> Dict[str, Any]:
        if not text or len(text.strip()) < 10:
            return {
                'label': 'neutral',
                'confidence': 0.5
            }
        
        if use_llm:
            result = self._analyze_with_llm(text)
            if result:
                return result
        
        vader_result = self._analyze_with_vader(text)
        
        if abs(vader_result['compound']) < 0.05:
            return {
                'label': 'neutral',
                'confidence': 0.6
            }
        elif vader_result['compound'] > 0.05:
            return {
                'label': 'positive',
                'confidence': abs(vader_result['compound'])
            }
        else:
            return {
                'label': 'negative',
                'confidence': abs(vader_result['compound'])
            }
    
    def _analyze_with_vader(self, text: str) -> Dict[str, float]:
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            
            if self._vader_analyzer is None:
                self._vader_analyzer = SentimentIntensityAnalyzer()
            
            scores = self._vader_analyzer.polarity_scores(text)
            return scores
        except ImportError:
            logger.warning("VADER not available, using TextBlob")
            return self._analyze_with_textblob(text)
        except Exception as e:
            logger.error(f"Error in VADER sentiment analysis: {e}")
            return {'compound': 0.0}
    
    def _analyze_with_textblob(self, text: str) -> Dict[str, float]:
        try:
            from textblob import TextBlob
            
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            return {
                'compound': polarity,
                'pos': max(0, polarity),
                'neg': max(0, -polarity),
                'neu': 1 - abs(polarity)
            }
        except Exception as e:
            logger.error(f"Error in TextBlob sentiment analysis: {e}")
            return {'compound': 0.0}
    
    def _analyze_with_llm(self, text: str) -> Dict[str, Any]:
        try:
            import os
            
            try:
                from openai import OpenAI
                api_key = os.getenv('OPENAI_API_KEY')
                if api_key:
                    client = OpenAI(api_key=api_key)
                    
                    truncated_text = text[:5000]
                    
                    response = client.chat.completions.create(
                        model="gpt-4-turbo-preview",
                        messages=[
                            {
                                "role": "system",
                                "content": "Analyze the sentiment of the text. Respond with only one word: positive, negative, or neutral."
                            },
                            {
                                "role": "user",
                                "content": truncated_text
                            }
                        ],
                        temperature=0.0,
                        max_tokens=10
                    )
                    
                    label = response.choices[0].message.content.strip().lower()
                    
                    if label not in ['positive', 'negative', 'neutral']:
                        return None
                    
                    return {
                        'label': label,
                        'confidence': 0.85
                    }
            except:
                pass
            
            try:
                from anthropic import Anthropic
                api_key = os.getenv('ANTHROPIC_API_KEY')
                if api_key:
                    client = Anthropic(api_key=api_key)
                    
                    truncated_text = text[:5000]
                    
                    response = client.messages.create(
                        model="claude-3-opus-20240229",
                        max_tokens=10,
                        messages=[
                            {
                                "role": "user",
                                "content": f"Analyze the sentiment of this text. Respond with only one word: positive, negative, or neutral.\\n\\n{truncated_text}"
                            }
                        ]
                    )
                    
                    label = response.content[0].text.strip().lower()
                    
                    if label not in ['positive', 'negative', 'neutral']:
                        return None
                    
                    return {
                        'label': label,
                        'confidence': 0.85
                    }
            except:
                pass
        
        except Exception as e:
            logger.error(f"Error in LLM sentiment analysis: {e}")
        
        return None
''')
    
    print("\\nAll remaining service files created successfully!")

if __name__ == '__main__':
    main()
