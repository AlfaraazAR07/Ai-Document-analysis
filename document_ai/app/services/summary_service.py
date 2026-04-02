import logging
from typing import Optional, Dict, Any
import os

logger = logging.getLogger(__name__)


class SummaryService:
    
    def __init__(self, llm_provider: str = 'openai', model: str = 'gpt-4-turbo-preview'):
        self.llm_provider = llm_provider
        self.model = model
        self._client = None
    
    def generate_summary(self, text: str, max_length: int = 500) -> str:
        if not text or not isinstance(text, str) or len(text.strip()) < 50:
            if not text:
                return "No text content available for summarization."
            return text
        
        try:
            if self.llm_provider == 'openai':
                return self._generate_with_openai(text, max_length)
            elif self.llm_provider == 'anthropic':
                return self._generate_with_anthropic(text, max_length)
            else:
                return self._fallback_summary(text, max_length)
        except Exception as e:
            logger.error(f"Error in summary generation: {e}")
            return self._fallback_summary(text, max_length)
    
    def _generate_with_openai(self, text: str, max_length: int) -> str:
        try:
            from openai import OpenAI
            
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                logger.warning("OpenAI API key not found, using fallback summarization")
                return self._fallback_summary(text, max_length)
            
            if self._client is None:
                self._client = OpenAI(api_key=api_key)
            
            truncated_text = str(text)[:15000]
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a document summarization assistant. Provide a concise summary of the document in no more than {max_length} words. Focus on the main points, key entities mentioned, and important dates or amounts."
                    },
                    {
                        "role": "user",
                        "content": f"Summarize the following document:\n\n{truncated_text}"
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
            
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                logger.warning("Anthropic API key not found, using fallback summarization")
                return self._fallback_summary(text, max_length)
            
            if self._client is None:
                self._client = Anthropic(api_key=api_key)
            
            truncated_text = str(text)[:15000]
            
            response = self._client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": f"Summarize the following document concisely in no more than {max_length} words. Focus on main points and key entities:\n\n{truncated_text}"
                    }
                ]
            )
            
            return response.content[0].text.strip()
        except Exception as e:
            logger.error(f"Error in Anthropic summarization: {e}")
            return self._fallback_summary(text, max_length)
    
    def _fallback_summary(self, text: str, max_length: int) -> str:
        text = str(text).strip()
        
        if len(text) < 50:
            return text
        
        sentences = text.replace('\n', ' ').split('. ')
        
        if len(sentences) <= 3:
            return text[:max_length * 6]
        
        first_sentences = sentences[:3]
        summary = '. '.join(first_sentences)
        
        if len(summary) > max_length * 6:
            summary = summary[:max_length * 6]
        
        if not summary.endswith('.'):
            summary += '.'
        
        return summary.strip()
