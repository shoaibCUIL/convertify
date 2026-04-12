"""
Security Utilities (Render-Safe)
"""

import os
import mimetypes
from pathlib import Path


def validate_file(file_path):
    """
    Validate file type safely (no magic dependency)
    """
    try:
        file_path = str(file_path)

        # Use mimetypes instead of magic
        file_type, _ = mimetypes.guess_type(file_path)

        if not file_type:
            return False

        allowed_types = [
            "application/pdf",
            "image/jpeg",
            "image/png",
            "image/webp",
            "text/plain"
        ]

        return file_type in allowed_types

    except Exception as e:
        print(f"Validation error: {e}")
        return False


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