from celery import Celery
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
