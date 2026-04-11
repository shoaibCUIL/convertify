"""
Security Utilities
File validation, sanitization, and security checks
"""

import os
import re
from werkzeug.utils import secure_filename
import magic


# Maximum file size (500MB)
MAX_FILE_SIZE = 500 * 1024 * 1024

# Blocked file extensions for security
BLOCKED_EXTENSIONS = [
    '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js', '.jar',
    '.dll', '.sh', '.bash', '.zsh', '.app', '.deb', '.rpm'
]

# Allowed MIME types for additional security
ALLOWED_MIME_CATEGORIES = [
    'application/pdf',
    'image/',
    'video/',
    'audio/',
    'text/',
    'application/msword',
    'application/vnd.openxmlformats',
    'application/vnd.oasis.opendocument',
    'application/vnd.ms-excel',
    'application/vnd.ms-powerpoint',
    'application/rtf',
    'application/zip'
]


def validate_file(file):
    """
    Validate uploaded file for security
    
    Args:
        file: FileStorage object from Flask
        
    Returns:
        bool: True if file is valid and safe
    """
    if not file or not file.filename:
        return False
    
    # Check file extension
    if not is_safe_extension(file.filename):
        return False
    
    # Read first chunk to check MIME type
    file.seek(0)
    chunk = file.read(8192)
    file.seek(0)
    
    # Check MIME type
    try:
        mime = magic.Magic(mime=True)
        mime_type = mime.from_buffer(chunk)
        
        if not is_allowed_mime_type(mime_type):
            return False
    except:
        # If magic fails, rely on extension check
        pass
    
    return True


def is_safe_extension(filename):
    """
    Check if file extension is safe
    
    Args:
        filename: Name of the file
        
    Returns:
        bool: True if extension is safe
    """
    ext = os.path.splitext(filename)[1].lower()
    return ext not in BLOCKED_EXTENSIONS


def is_allowed_mime_type(mime_type):
    """
    Check if MIME type is allowed
    
    Args:
        mime_type: MIME type string
        
    Returns:
        bool: True if MIME type is allowed
    """
    # Check exact matches
    if mime_type in ALLOWED_MIME_CATEGORIES:
        return True
    
    # Check category matches (e.g., image/*)
    for allowed in ALLOWED_MIME_CATEGORIES:
        if allowed.endswith('/') and mime_type.startswith(allowed):
            return True
        if allowed in mime_type:
            return True
    
    return False


def sanitize_path(path):
    """
    Sanitize file path to prevent directory traversal
    
    Args:
        path: File path or filename
        
    Returns:
        str: Sanitized filename
    """
    # Remove directory separators
    filename = os.path.basename(path)
    
    # Use werkzeug's secure_filename
    filename = secure_filename(filename)
    
    # Remove any remaining problematic characters
    filename = re.sub(r'[^\w\s\.-]', '', filename)
    
    return filename


def check_file_size(file):
    """
    Check if file size is within limits
    
    Args:
        file: FileStorage object
        
    Returns:
        bool: True if size is acceptable
    """
    try:
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        
        return size <= MAX_FILE_SIZE
    except:
        return False


def is_path_safe(path, base_directory):
    """
    Check if path is within base directory (prevent directory traversal)
    
    Args:
        path: File path to check
        base_directory: Base directory path
        
    Returns:
        bool: True if path is safe
    """
    # Resolve to absolute paths
    abs_path = os.path.abspath(path)
    abs_base = os.path.abspath(base_directory)
    
    # Check if path starts with base directory
    return abs_path.startswith(abs_base)


def sanitize_filename_for_download(filename):
    """
    Sanitize filename for safe download
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Remove or replace problematic characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Limit length
    name, ext = os.path.splitext(filename)
    if len(name) > 200:
        name = name[:200]
    
    return name + ext


def validate_password(password):
    """
    Validate password strength for PDF protection
    
    Args:
        password: Password string
        
    Returns:
        tuple: (is_valid, message)
    """
    if not password:
        return False, "Password cannot be empty"
    
    if len(password) < 4:
        return False, "Password must be at least 4 characters"
    
    if len(password) > 128:
        return False, "Password is too long"
    
    return True, "Password is valid"


def sanitize_watermark_text(text):
    """
    Sanitize watermark text
    
    Args:
        text: Watermark text
        
    Returns:
        str: Sanitized text
    """
    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Limit length
    if len(text) > 200:
        text = text[:200]
    
    return text


def validate_page_range(page_range, max_pages):
    """
    Validate page range for PDF operations
    
    Args:
        page_range: List of page numbers or ranges
        max_pages: Maximum number of pages in document
        
    Returns:
        tuple: (is_valid, message)
    """
    try:
        if isinstance(page_range, str):
            if page_range.lower() == 'all':
                return True, "Valid range"
            
            # Parse range string (e.g., "1-5,7,9-12")
            ranges = page_range.split(',')
            for r in ranges:
                if '-' in r:
                    start, end = map(int, r.split('-'))
                    if start < 1 or end > max_pages or start > end:
                        return False, f"Invalid range: {r}"
                else:
                    page = int(r)
                    if page < 1 or page > max_pages:
                        return False, f"Invalid page number: {page}"
        
        elif isinstance(page_range, list):
            for item in page_range:
                if isinstance(item, int):
                    if item < 1 or item > max_pages:
                        return False, f"Invalid page number: {item}"
                elif isinstance(item, (list, tuple)) and len(item) == 2:
                    start, end = item
                    if start < 1 or end > max_pages or start > end:
                        return False, f"Invalid range: {start}-{end}"
        
        return True, "Valid range"
    
    except Exception as e:
        return False, f"Invalid page range format: {str(e)}"


def check_disk_space(required_space, path='/'):
    """
    Check if sufficient disk space is available
    
    Args:
        required_space: Required space in bytes
        path: Path to check (default: root)
        
    Returns:
        bool: True if sufficient space available
    """
    try:
        stat = os.statvfs(path)
        available = stat.f_bavail * stat.f_frsize
        return available >= required_space
    except:
        # If check fails, assume space is available
        return True