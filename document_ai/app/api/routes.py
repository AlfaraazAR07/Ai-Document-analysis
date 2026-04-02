from fastapi import APIRouter, HTTPException, Header, status
from typing import Optional
import asyncio

from app.core.schemas import DocumentRequest, DocumentResponse, ErrorResponse
from app.core.config import get_settings
from app.services.orchestration_service import OrchestrationService
from app.workers.tasks import process_document_async

router = APIRouter(prefix="/api")
settings = get_settings()
orchestrator = OrchestrationService()


async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required. Provide x-api-key header."
        )
    
    if x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key."
        )
    
    return x_api_key


@router.post("/document-analyze", response_model=DocumentResponse)
async def analyze_document(
    request: DocumentRequest,
    api_key: str = verify_api_key
):
    try:
        result = await orchestrator.process_document(
            file_name=request.file_name,
            file_data_base64=request.file_data_base64,
            mime_type=request.mime_type,
            options=request.options.model_dump() if request.options else None
        )
        
        if result.get('success'):
            return DocumentResponse(**result)
        else:
            return DocumentResponse(
                success=False,
                error=result.get('error', 'Processing failed')
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/document-analyze-async")
async def analyze_document_async(
    request: DocumentRequest,
    api_key: str = verify_api_key
):
    try:
        task = process_document_async.delay(
            file_name=request.file_name,
            file_data_base64=request.file_data_base64,
            mime_type=request.mime_type,
            options=request.options.model_dump() if request.options else None
        )
        
        return {
            "success": True,
            "task_id": str(task.id),
            "status": "processing"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start async processing: {str(e)}"
        )


@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    from celery.result import AsyncResult
    from app.workers.tasks import celery_app
    
    result = AsyncResult(task_id, app=celery_app)
    
    if result.ready():
        if result.successful():
            return {
                "success": True,
                "task_id": task_id,
                "status": "completed",
                "result": result.get()
            }
        else:
            return {
                "success": False,
                "task_id": task_id,
                "status": "failed",
                "error": str(result.result)
            }
    else:
        return {
            "success": True,
            "task_id": task_id,
            "status": "processing"
        }


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "document-ai"}
