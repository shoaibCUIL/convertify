"""
OCR Engine (Render-Safe Version)
"""

import os
import uuid

from PIL import Image
from PyPDF2 import PdfReader, PdfWriter

# Optional imports (NOT supported on Render)
try:
    import pytesseract
    OCR_AVAILABLE = True
except:
    OCR_AVAILABLE = False

try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except:
    PDF2IMAGE_AVAILABLE = False


class OCREngine:
    """Engine for OCR operations"""

    def perform_ocr(self, input_path, language, output_format, output_folder):
        """
        Perform OCR on image or PDF
        """
        if not OCR_AVAILABLE:
            return {
                'success': False,
                'error': 'OCR not supported on this server'
            }

        try:
            ext = os.path.splitext(input_path)[1].lower()

            if ext == '.pdf':
                return self._ocr_pdf(input_path, language, output_format, output_folder)
            else:
                return self._ocr_image(input_path, language, output_format, output_folder)

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _ocr_image(self, input_path, language, output_format, output_folder):
        """Perform OCR on image file"""
        if not OCR_AVAILABLE:
            return {'success': False, 'error': 'OCR not supported'}

        try:
            image = Image.open(input_path)
            text = pytesseract.image_to_string(image, lang=language)

            if output_format == 'text':
                output_filename = f"ocr_text_{uuid.uuid4()}.txt"
                output_path = os.path.join(output_folder, output_filename)

                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(text)

                return {
                    'success': True,
                    'text': text,
                    'output_path': output_path
                }

            elif output_format == 'pdf':
                output_filename = f"ocr_pdf_{uuid.uuid4()}.pdf"
                output_path = os.path.join(output_folder, output_filename)

                pdf_bytes = pytesseract.image_to_pdf_or_hocr(
                    image, lang=language, extension='pdf'
                )

                with open(output_path, 'wb') as f:
                    f.write(pdf_bytes)

                return {
                    'success': True,
                    'output_path': output_path
                }

            else:
                return {'success': False, 'error': 'Unsupported format'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _ocr_pdf(self, input_path, language, output_format, output_folder):
        """Perform OCR on PDF"""
        if not OCR_AVAILABLE or not PDF2IMAGE_AVAILABLE:
            return {
                'success': False,
                'error': 'OCR for PDF not supported on this server'
            }

        try:
            images = convert_from_path(input_path, dpi=300)

            all_text = []

            for i, image in enumerate(images):
                text = pytesseract.image_to_string(image, lang=language)
                all_text.append(f"--- Page {i+1} ---\n{text}\n")

            combined_text = "\n".join(all_text)

            if output_format == 'text':
                output_filename = f"ocr_text_{uuid.uuid4()}.txt"
                output_path = os.path.join(output_folder, output_filename)

                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(combined_text)

                return {
                    'success': True,
                    'text': combined_text,
                    'output_path': output_path
                }

            else:
                return {
                    'success': False,
                    'error': 'PDF OCR output not supported'
                }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def make_pdf_searchable(self, input_path, language, output_folder):
        return self.perform_ocr(input_path, language, 'searchable_pdf', output_folder)

    def extract_text_from_image(self, input_path, language, output_folder):
        return self.perform_ocr(input_path, language, 'text', output_folder)

    def get_supported_languages(self):
        if not OCR_AVAILABLE:
            return {
                'success': True,
                'languages': ['eng'],
                'note': 'Limited support (OCR disabled)'
            }

        try:
            languages = pytesseract.get_languages()
            return {
                'success': True,
                'languages': languages
            }
        except:
            return {
                'success': True,
                'languages': ['eng']
            }