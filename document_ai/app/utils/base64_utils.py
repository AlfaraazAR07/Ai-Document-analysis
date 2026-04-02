import base64
import os
import tempfile
from typing import Tuple, Optional
from pathlib import Path


def decode_base64_to_bytes(base64_string: str) -> bytes:
    try:
        return base64.b64decode(base64_string)
    except Exception as e:
        raise ValueError(f"Failed to decode base64 string: {str(e)}")


def decode_base64_to_file(base64_string: str, file_name: str, output_dir: Optional[str] = None) -> Tuple[str, str]:
    if output_dir is None:
        output_dir = tempfile.gettempdir()
    
    os.makedirs(output_dir, exist_ok=True)
    
    file_extension = Path(file_name).suffix.lower()
    safe_name = Path(file_name).stem
    temp_file_path = os.path.join(output_dir, f"{safe_name}_{os.urandom(8).hex()}{file_extension}")
    
    file_bytes = decode_base64_to_bytes(base64_string)
    
    with open(temp_file_path, 'wb') as f:
        f.write(file_bytes)
    
    return temp_file_path, file_extension


def encode_file_to_base64(file_path: str) -> str:
    with open(file_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


def get_mime_type(file_extension: str) -> str:
    mime_types = {
        '.pdf': 'application/pdf',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.doc': 'application/msword',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.tiff': 'image/tiff',
        '.tif': 'image/tiff',
    }
    return mime_types.get(file_extension.lower(), 'application/octet-stream')


def is_supported_format(file_extension: str) -> bool:
    supported_extensions = {'.pdf', '.docx', '.doc', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif'}
    return file_extension.lower() in supported_extensions


def cleanup_temp_file(file_path: str) -> None:
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception:
        pass
