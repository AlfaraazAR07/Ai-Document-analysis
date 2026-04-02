import os
from typing import Dict, Any
from PIL import Image


class ImageService:
    
    def __init__(self):
        pass
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Image file not found: {file_path}")
        
        try:
            with Image.open(file_path) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode,
                    'has_transparency': img.mode in ('RGBA', 'LA', 'P')
                }
        except Exception as e:
            return {
                'error': str(e)
            }
    
    def is_likely_scanned(self, file_path: str) -> bool:
        try:
            with Image.open(file_path) as img:
                if img.mode == 'RGB':
                    pixels = list(img.getdata())
                    unique_colors = len(set(pixels[:1000]))
                    return unique_colors < 50
        except Exception:
            pass
        return False
