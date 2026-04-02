import logging
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
