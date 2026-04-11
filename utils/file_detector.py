"""
File Type Detection Utility
Automatically detect file types and MIME types
"""

import os
import magic
import mimetypes
from pathlib import Path


def detect_file_type(filepath):
    """
    Detect file type using magic bytes and extension
    
    Args:
        filepath: Path to the file
        
    Returns:
        dict: File type information
    """
    try:
        # Use python-magic for accurate detection
        mime = magic.Magic(mime=True)
        mime_type = mime.from_file(filepath)
        
        # Get file extension
        ext = os.path.splitext(filepath)[1].lower()
        
        # Categorize file type
        file_category = categorize_file_type(mime_type, ext)
        
        return {
            'type': file_category,
            'mime_type': mime_type,
            'extension': ext
        }
    
    except Exception as e:
        # Fallback to extension-based detection
        ext = os.path.splitext(filepath)[1].lower()
        mime_type = mimetypes.guess_type(filepath)[0] or 'application/octet-stream'
        
        return {
            'type': categorize_file_type(mime_type, ext),
            'mime_type': mime_type,
            'extension': ext
        }


def categorize_file_type(mime_type, extension):
    """
    Categorize file into broad types
    
    Args:
        mime_type: MIME type string
        extension: File extension
        
    Returns:
        str: File category
    """
    # PDF
    if 'pdf' in mime_type or extension == '.pdf':
        return 'pdf'
    
    # Images
    if mime_type.startswith('image/'):
        return 'image'
    
    # Videos
    if mime_type.startswith('video/'):
        return 'video'
    
    # Audio
    if mime_type.startswith('audio/'):
        return 'audio'
    
    # Documents
    document_types = [
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml',
        'application/vnd.oasis.opendocument.text',
        'application/rtf',
        'text/plain',
        'text/markdown'
    ]
    
    if any(dt in mime_type for dt in document_types):
        return 'document'
    
    # Spreadsheets
    spreadsheet_types = [
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml',
        'application/vnd.oasis.opendocument.spreadsheet',
        'text/csv'
    ]
    
    if any(st in mime_type for st in spreadsheet_types):
        return 'spreadsheet'
    
    # Presentations
    presentation_types = [
        'application/vnd.ms-powerpoint',
        'application/vnd.openxmlformats-officedocument.presentationml',
        'application/vnd.oasis.opendocument.presentation'
    ]
    
    if any(pt in mime_type for pt in presentation_types):
        return 'presentation'
    
    # Archives
    if mime_type.startswith('application/zip') or extension in ['.zip', '.rar', '.7z', '.tar', '.gz']:
        return 'archive'
    
    # Text files
    if mime_type.startswith('text/'):
        return 'text'
    
    return 'other'


def get_file_info(filepath):
    """
    Get detailed file information
    
    Args:
        filepath: Path to the file
        
    Returns:
        dict: File information
    """
    stat = os.stat(filepath)
    
    return {
        'name': os.path.basename(filepath),
        'size': stat.st_size,
        'size_formatted': format_file_size(stat.st_size),
        'created': stat.st_ctime,
        'modified': stat.st_mtime
    }


def format_file_size(size_bytes):
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Formatted size
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def is_supported_format(filepath, category=None):
    """
    Check if file format is supported
    
    Args:
        filepath: Path to the file
        category: Optional category to check against
        
    Returns:
        bool: True if supported
    """
    file_info = detect_file_type(filepath)
    
    if category:
        return file_info['type'] == category
    
    # All detected types are supported
    return file_info['type'] != 'other'


# Supported conversion mappings
CONVERSION_SUPPORT = {
    'pdf': ['txt', 'docx', 'html', 'png', 'jpg', 'jpeg'],
    'image': ['pdf', 'png', 'jpg', 'jpeg', 'webp', 'bmp', 'tiff', 'gif'],
    'document': ['pdf', 'docx', 'txt', 'html', 'odt', 'rtf'],
    'spreadsheet': ['pdf', 'xlsx', 'csv', 'ods', 'html'],
    'presentation': ['pdf', 'pptx', 'odp', 'html'],
    'video': ['mp4', 'avi', 'mov', 'mkv', 'webm', 'mp3', 'wav'],
    'audio': ['mp3', 'wav', 'ogg', 'aac', 'm4a']
}


def get_supported_conversions(filepath):
    """
    Get list of supported conversion formats for a file
    
    Args:
        filepath: Path to the file
        
    Returns:
        list: Supported output formats
    """
    file_info = detect_file_type(filepath)
    file_type = file_info['type']
    
    return CONVERSION_SUPPORT.get(file_type, [])


def can_convert(filepath, target_format):
    """
    Check if conversion is supported
    
    Args:
        filepath: Path to the source file
        target_format: Target format extension
        
    Returns:
        bool: True if conversion is supported
    """
    supported = get_supported_conversions(filepath)
    return target_format.lower().replace('.', '') in supported