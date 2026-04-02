#!/usr/bin/env python3
"""
Check if required dependencies are installed
"""
import sys
import subprocess

def check_package(package_name, import_name=None):
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✓ {package_name}")
        return True
    except ImportError:
        print(f"✗ {package_name} - NOT INSTALLED")
        return False

def main():
    print("Checking required packages...")
    print()
    
    packages = [
        ("FastAPI", "fastapi"),
        ("Uvicorn", "uvicorn"),
        ("Pydantic", "pydantic"),
        ("Pillow", "PIL"),
        ("Celery", "celery"),
        ("Redis", "redis"),
        ("pytesseract", "pytesseract"),
        ("pdf2image", "pdf2image"),
        ("easyocr", "easyocr"),
        ("OpenAI", "openai"),
        ("spaCy", "spacy"),
        ("VADER", "vaderSentiment"),
        ("TextBlob", "textblob"),
        ("python-docx", "docx"),
    ]
    
    missing = []
    for pkg_name, import_name in packages:
        if not check_package(pkg_name, import_name):
            missing.append((pkg_name, import_name))
    
    print()
    if missing:
        print("Missing packages:")
        for pkg_name, import_name in missing:
            print(f"  pip install {pkg_name.lower()}")
        
        print()
        print("To install all missing packages:")
        install_cmd = "pip install " + " ".join([pkg.lower() for pkg, _ in missing])
        print(f"  {install_cmd}")
        return 1
    else:
        print("All required packages are installed!")
        print()
        print("Next steps:")
        print("  1. Install Tesseract OCR (Windows): https://github.com/UB-Mannheim/tesseract/wiki")
        print("  2. Download spaCy model: python -m spacy download en_core_web_sm")
        print("  3. Start Redis: docker run -d -p 6379:6379 redis:alpine")
        print("  4. Run: python start.py")
        return 0

if __name__ == '__main__':
    sys.exit(main())
