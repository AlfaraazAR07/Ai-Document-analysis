#!/usr/bin/env python3
"""
Quick test script to verify the Document AI API installation
"""
import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import fastapi
        print("✓ FastAPI")
    except ImportError as e:
        print(f"✗ FastAPI: {e}")
        return False
    
    try:
        import uvicorn
        print("✓ Uvicorn")
    except ImportError as e:
        print(f"✗ Uvicorn: {e}")
        return False
    
    try:
        import celery
        print("✓ Celery")
    except ImportError as e:
        print(f"✗ Celery: {e}")
        return False
    
    try:
        from PIL import Image
        print("✓ Pillow")
    except ImportError as e:
        print(f"✗ Pillow: {e}")
        return False
    
    try:
        import pydantic
        import pydantic_settings
        print("✓ Pydantic")
    except ImportError as e:
        print(f"✗ Pydantic: {e}")
        return False
    
    return True

def test_app_structure():
    """Test if app structure exists"""
    print("\nTesting app structure...")
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(base_path, 'app')
    
    required_files = [
        'app/main.py',
        'app/api/routes.py',
        'app/core/config.py',
        'app/core/schemas.py',
        'app/services/orchestration_service.py',
        'app/services/parser_service.py',
        'app/services/pdf_service.py',
        'app/services/docx_service.py',
        'app/services/image_service.py',
        'app/services/ocr_service.py',
        'app/services/entity_service.py',
        'app/services/summary_service.py',
        'app/services/sentiment_service.py',
        'app/services/cleaning_service.py',
        'app/workers/tasks.py',
        'app/utils/base64_utils.py',
        'app/utils/regex_extractors.py',
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = os.path.join(base_path, file_path)
        if os.path.exists(full_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def test_config():
    """Test if configuration can be loaded"""
    print("\nTesting configuration...")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from app.core.config import get_settings
        settings = get_settings()
        print(f"✓ Configuration loaded")
        print(f"  - API Key: {'Set' if settings.API_KEY else 'Not set'}")
        print(f"  - LLM Provider: {settings.LLM_PROVIDER}")
        print(f"  - OCR Provider: {settings.OCR_PROVIDER}")
        return True
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False

def main():
    print("=" * 60)
    print("Document AI - Installation Test")
    print("=" * 60)
    
    success = True
    
    if not test_imports():
        success = False
        print("\n✗ Some imports failed. Please install missing dependencies:")
        print("  pip install -r requirements.txt")
    
    if not test_app_structure():
        success = False
        print("\n✗ Some app files are missing!")
        print("  Run the setup scripts to create missing files.")
    
    if not test_config():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✓ All tests passed!")
        print("\nTo start the API:")
        print("  1. Make sure Redis is running")
        print("  2. Set PYTHONPATH environment variable:")
        print("     Windows: $env:PYTHONPATH = 'E:\\document_ai'")
        print("     Linux/Mac: export PYTHONPATH=/path/to/document_ai")
        print("  3. Run: uvicorn app.main:app --reload --host 127.0.0.1 --port 8000")
    else:
        print("✗ Some tests failed. Please fix the issues above.")
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
