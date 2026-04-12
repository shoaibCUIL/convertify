import os

from utils.file_detector import detect_file_type, can_convert
from engines.pdf_engine import PDFEngine
from engines.document_engine import DocumentEngine


class UniversalConverter:
    """Main conversion controller"""

    def __init__(self):
        self.pdf_engine = PDFEngine()
        self.document_engine = DocumentEngine()

    # =========================
    # MAIN CONVERT METHOD
    # =========================
    def convert(self, input_path, target_format, options=None):
        try:
            if options is None:
                options = {}

            output_folder = options.get("output_folder", "outputs")
            os.makedirs(output_folder, exist_ok=True)

            # Detect file type
            file_info = detect_file_type(input_path)
            source_type = file_info.get("type")

            # Validate conversion
            if not can_convert(input_path, target_format):
                return {
                    "success": False,
                    "error": f"Conversion not allowed"
                }

            # =========================
            # PDF ROUTING
            # =========================
            if source_type == "pdf":

                if target_format == "txt":
                    return self.pdf_engine.pdf_to_text(input_path, output_folder)

                elif target_format == "html":
                    return self.pdf_engine.pdf_to_html(input_path, output_folder)

                elif target_format == "docx":
                    return self.pdf_engine.pdf_to_docx(input_path, output_folder)

                else:
                    return {
                        "success": False,
                        "error": f"PDF → {target_format} not supported"
                    }

            # =========================
            # DOCUMENT ROUTING
            # =========================
            elif source_type in ["document", "text"]:
                return self.document_engine.convert(
                    input_path,
                    target_format,
                    output_folder
                )

            # =========================
            # UNKNOWN
            # =========================
            else:
                return {
                    "success": False,
                    "error": f"Unsupported file type"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }