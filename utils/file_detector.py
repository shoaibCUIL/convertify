import os


def detect_file_type(file_path):
    """
    Detect file type based on extension only (stable for Render)
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext in ['.pdf']:
        return {"type": "pdf"}

    elif ext in ['.docx', '.doc']:
        return {"type": "document"}

    elif ext in ['.txt']:
        return {"type": "text"}

    else:
        return {"type": "unknown"}


# =========================
# CONVERSION RULES
# =========================
def can_convert(input_path, target_format):
    ext = os.path.splitext(input_path)[1].lower()

    allowed = {
        ".pdf": ["txt", "docx", "html"],
        ".docx": ["pdf", "txt", "html", "xml", "csv"],
        ".txt": ["docx"]
    }

    return target_format in allowed.get(ext, [])


# =========================
# FILE INFO
# =========================
def get_file_info(file_path):
    try:
        return {
            "size": os.path.getsize(file_path),
            "extension": os.path.splitext(file_path)[1]
        }
    except:
        return {}