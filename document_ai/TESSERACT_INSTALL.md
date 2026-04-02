# Tesseract OCR Installation Guide

## For Windows

### Option 1: Download Installer (Recommended)
1. Go to: https://github.com/UB-Mannheim/tesseract/wiki
2. Download the latest installer (.exe file)
3. Run the installer
4. Default installation path: `C:\Program Files\Tesseract-OCR\`
5. Add to PATH (optional, the app will find it automatically)

### Option 2: Chocolatey
If you have Chocolatey installed:
```powershell
choco install tesseract
```

### Option 3: Check if already installed
Tesseract might already be installed. Check:
```powershell
tesseract --version
```

## For Linux (if running in WSL or Linux)
```bash
sudo apt-get install tesseract-ocr
```

## After Installation

Restart your terminal and run:
```powershell
python -c "import pytesseract; print('Tesseract OK')"
```

## Troubleshooting

### Tesseract not found
If you installed to a different location, update `.env`:
```
TESSERACT_CMD=C:\path\to\your\tesseract.exe
```

### Permission issues
Run terminal as Administrator if you have installation issues.

---

**Without Tesseract**, the system will still work but OCR for images will use fallback methods.
