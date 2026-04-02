# Document AI - Quick Start Guide

## What's Been Built

A complete AI-powered document analysis and extraction system with:
- Multi-format support (PDF, DOCX, images with OCR)
- AI-powered summarization and entity extraction
- Sentiment analysis
- Async processing with Celery
- RESTful API with authentication

## Quick Start

### 1. Navigate to the Project
```powershell
cd E:\document_ai
```

### 2. Install Dependencies (if not already installed)
```powershell
pip install -r requirements.txt
```

### 3. Start Redis (Required for async tasks)
Make sure Redis is running. You can:
- Install Redis locally, or
- Use Docker: `docker run -d -p 6379:6379 redis:alpine`

### 4. Start the API Server
```powershell
# Set PYTHONPATH
$env:PYTHONPATH = "E:\document_ai"

# Or use the startup script
python start.py
```

The API will start at: **http://127.0.0.1:8000**

### 5. Access the API Documentation
Open your browser to: **http://127.0.0.1:8000/docs**

## Testing the API

### Using the Interactive Documentation
1. Go to http://127.0.0.1:8000/docs
2. Click on the `/api/document-analyze` endpoint
3. Click "Try it out"
4. Enter the required information:
   - `file_name`: "test.pdf"
   - `file_data_base64`: (base64 encoded file content)
   - `mime_type`: "application/pdf"
5. Add header: `x-api-key`: `sk_track2_987654321`
6. Click "Execute"

### Using curl

```powershell
# Test health endpoint
curl http://127.0.0.1:8000/api/health

# Analyze a document (example with base64 encoded file)
curl -X POST http://127.0.0.1:8000/api/document-analyze `
  -H "Content-Type: application/json" `
  -H "x-api-key: sk_track2_987654321" `
  -d '{
    "file_name": "sample.pdf",
    "file_data_base64": "BASE64_ENCODED_CONTENT_HERE",
    "mime_type": "application/pdf",
    "options": {
      "ocr_provider": "tesseract",
      "include_layout": true
    }
  }'
```

### Using Python
```python
import requests
import base64

# Read and encode file
with open("your_file.pdf", "rb") as f:
    file_data = base64.b64encode(f.read()).decode()

# Send request
response = requests.post(
    "http://127.0.0.1:8000/api/document-analyze",
    json={
        "file_name": "document.pdf",
        "file_data_base64": file_data,
        "mime_type": "application/pdf",
        "options": {"include_layout": True}
    },
    headers={"x-api-key": "sk_track2_987654321"}
)

print(response.json())
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root endpoint with API info |
| `/api/health` | GET | Health check |
| `/api/document-analyze` | POST | Analyze document (sync) |
| `/api/document-analyze-async` | POST | Analyze document (async, returns task ID) |
| `/api/task/{task_id}` | GET | Get async task status |
| `/docs` | GET | Interactive API documentation (Swagger UI) |

## Configuration

Edit the `.env` file to customize:

```env
# API Security
API_KEY=sk_track2_987654321

# LLM Settings (for better summarization)
OPENAI_API_KEY=your_openai_key_here
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview

# OCR Settings
OCR_PROVIDER=tesseract
```

## Optional: Start Celery Worker

For async processing, start a worker in a separate terminal:

```powershell
$env:PYTHONPATH = "E:\document_ai"
celery -A app.workers.tasks worker --loglevel=info
```

## Troubleshooting

### "Module not found" errors
```powershell
pip install -r requirements.txt
```

### Redis connection errors
- Make sure Redis is running: `redis-cli ping`
- Or start Redis: `docker run -d -p 6379:6379 redis:alpine`

### Port already in use
```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

### spaCy model not found
```powershell
python -m spacy download en_core_web_sm
```

## Project Structure

```
document_ai/
├── app/
│   ├── main.py                 # FastAPI app
│   ├── api/routes.py          # API endpoints
│   ├── core/                 # Config, schemas, logger
│   ├── services/             # Business logic (11 services)
│   ├── workers/              # Celery tasks
│   └── utils/                # Utilities
├── tests/                    # Test files
├── start.py                 # Startup script
├── test_installation.py      # Installation test
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Features

### Document Parsing
- PDF with layout preservation
- DOCX with structure extraction
- Images via OCR (Tesseract/EasyOCR/Google Vision)

### AI Analysis
- **Summarization**: LLM-powered or fallback extractive
- **Entity Extraction**: Names, dates, money, emails, phones
- **Sentiment Analysis**: VADER/TextBlob/LLM

### API Security
- API key authentication
- Request validation
- Error handling

## Next Steps

1. **Set up Redis** - Required for async processing
2. **Get API keys** - For LLM features (OpenAI/Anthropic)
3. **Test with documents** - Upload real documents
4. **Deploy** - Use Docker Compose for production

## Docker Deployment

```powershell
docker-compose up -d
```

The API will be available at http://localhost:8000

## Support

- Check `/docs` for interactive API documentation
- Review README.md for detailed documentation
- Test with `python test_installation.py`

---

**Your Document AI system is ready!** 🚀
