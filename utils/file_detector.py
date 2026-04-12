import os
import mimetypes
from pathlib import Path


def detect_file_type(file_path):
    """
    Detect file type using mimetypes (Render-safe)
    """
    try:
        file_path = str(file_path)
        file_type, _ = mimetypes.guess_type(file_path)

        if file_type:
            return file_type

        # Fallback using extension
        ext = Path(file_path).suffix.lower()

        extension_map = {
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".txt": "text/plain",
            ".csv": "text/csv",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".bmp": "image/bmp",
            ".tiff": "image/tiff",
            ".mp4": "video/mp4",
            ".avi": "video/x-msvideo",
            ".mov": "video/quicktime",
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
        }

        return extension_map.get(ext, "application/octet-stream")

    except Exception as e:
        print(f"Error detecting file type: {e}")
        return "application/octet-stream"


def get_file_info(file_path):
    """
    Get basic file information
    """
    try:
        file_path = Path(file_path)

        info = {
            "name": file_path.name,
            "size": file_path.stat().st_size if file_path.exists() else 0,
            "type": detect_file_type(file_path),
            "extension": file_path.suffix.lower(),
        }

        return info

    except Exception as e:
        print(f"Error getting file info: {e}")
        return {
            "name": "unknown",
            "size": 0,
            "type": "unknown",
            "extension": "",
        }
    
def can_convert(input_type, output_type):
    """
    Basic conversion validation (you can expand later)
    """
    if not input_type or not output_type:
        return False

    # Simple rules (customize if needed)
    supported_conversions = {
        "application/pdf": [
            "image/png",
            "image/jpeg",
            "text/plain",
        ],
        "image/jpeg": ["application/pdf"],
        "image/png": ["application/pdf"],
        "text/plain": ["application/pdf"],
    }

    return output_type in supported_conversions.get(input_type, [])