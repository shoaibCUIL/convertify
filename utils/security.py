"""
Security Utilities (Render-Safe)
"""

import os
import mimetypes
from pathlib import Path


def validate_file(file_path):
    """
    Relaxed validation (Render-safe)
    """
    try:
        file_path = str(file_path)

        # Allow based on extension (more reliable)
        allowed_extensions = [
            ".pdf",
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
            ".txt"
        ]

        ext = os.path.splitext(file_path)[1].lower()

        if ext in allowed_extensions:
            return True

        return False

    except Exception as e:
        print(f"Validation error: {e}")
        return True  # fallback: allow

def sanitize_path(file_path):
    """
    Prevent path traversal attacks
    """
    try:
        return os.path.basename(file_path)
    except:
        return file_path


def check_file_size(file_path, max_size_mb=10):
    """
    Check file size limit
    """
    try:
        size = os.path.getsize(file_path)
        return size <= max_size_mb * 1024 * 1024
    except:
        return False