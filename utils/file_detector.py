import os
import filetype

def detect_file_type(filepath):
    """Detect file type from file path
    
    Returns:
        String representing file type (pdf, docx, jpg, etc.)
    """
    try:
        # First try filetype library (magic number based)
        kind = filetype.guess(filepath)
        if kind is not None:
            return kind.extension
        
        # Fallback to file extension
        ext = os.path.splitext(filepath)[1][1:].lower()
        if ext:
            return ext
        
        # Last resort: try python-magic if available
        try:
            import magic
            mime = magic.from_file(filepath, mime=True)
            mime_to_ext = {
                'application/pdf': 'pdf',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
                'application/msword': 'doc',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
                'application/vnd.ms-excel': 'xls',
                'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'pptx',
                'application/vnd.ms-powerpoint': 'ppt',
                'image/jpeg': 'jpg',
                'image/png': 'png',
                'image/gif': 'gif',
                'image/bmp': 'bmp',
                'image/tiff': 'tiff',
                'text/plain': 'txt',
                'text/html': 'html',
                'application/json': 'json',
                'text/csv': 'csv'
            }
            return mime_to_ext.get(mime, 'unknown')
        except ImportError:
            # python-magic not installed, continue
            pass
        except Exception:
            # Error using magic, continue
            pass
        
        return 'unknown'
    
    except Exception as e:
        print(f"Error detecting file type: {str(e)}")
        # Fallback to extension
        ext = os.path.splitext(filepath)[1][1:].lower()
        return ext if ext else 'unknown'