import logging
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
                                "content": f"Analyze the sentiment of this text. Respond with only one word: positive, negative, or neutral.\n\n{truncated_text}"
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
