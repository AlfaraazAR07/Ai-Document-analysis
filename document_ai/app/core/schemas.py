from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class FileType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    IMAGE = "image"


class OCRProvider(str, Enum):
    TESSERACT = "tesseract"
    EASYOCR = "easyocr"
    GOOGLE_VISION = "google_vision"


class RequestOptions(BaseModel):
    ocr_provider: Optional[OCRProvider] = OCRProvider.TESSERACT
    include_layout: bool = True


class DocumentRequest(BaseModel):
    file_name: str = Field(..., description="Name of the uploaded file")
    file_data_base64: str = Field(..., description="Base64-encoded file content")
    mime_type: str = Field(..., description="MIME type of the file")
    options: Optional[RequestOptions] = Field(default_factory=RequestOptions)


class EntityInfo(BaseModel):
    text: str
    label: str
    confidence: float = Field(ge=0.0, le=1.0)


class SentimentInfo(BaseModel):
    label: str
    confidence: float = Field(ge=0.0, le=1.0)


class LayoutElement(BaseModel):
    type: str
    text: str
    page: int


class DocumentMetadata(BaseModel):
    pages: int
    language: str
    processing_time_ms: int
    ocr_used: bool


class DocumentResponse(BaseModel):
    success: bool
    document_type: Optional[str] = None
    source_type: Optional[str] = None
    summary: Optional[str] = None
    sentiment: Optional[SentimentInfo] = None
    entities: List[EntityInfo] = []
    layout_elements: List[LayoutElement] = []
    metadata: Optional[DocumentMetadata] = None
    error: Optional[str] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    status_code: int
