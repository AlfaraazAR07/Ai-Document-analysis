# Quick Test - Document AI

## Test 1: Check Installation
```powershell
python -c "import pytesseract; print('OK: All dependencies installed')"
```

## Test 2: Start Server
```powershell
cd E:\document_ai
python start.py
```

## Test 3: API Test (in browser)
- Open: http://127.0.0.1:8000/api/health
- Should return: `{"status":"healthy","service":"document-ai"}`

## Test 4: Analyze Document
Use the Swagger UI at: http://127.0.0.1:8000/docs

Click "Try it out" on `/api/document-analyze`

**Important:** 
- Set header: `x-api-key: sk_track2_987654321`
- Use `mime_type: "application/pdf"` for PDFs

## If OCR fails:
The system will use fallback methods, but OCR (image-to-text) won't work.

**Install Tesseract**: See TESSERACT_INSTALL.md
