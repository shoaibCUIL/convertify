"""
Universal File Converter
Routes conversion requests to appropriate engines
"""

import os
import uuid

from utils.file_detector import detect_file_type, can_convert

from engines.pdf_engine import PDFEngine
from engines.image_engine import ImageEngine
from engines.video_engine import VideoEngine
from engines.document_engine import DocumentEngine
from engines.ocr_engine import OCREngine


class UniversalConverter:
    """Universal file converter that routes to appropriate engines"""

    def __init__(self):
        self.pdf_engine = PDFEngine()
        self.image_engine = ImageEngine()
        self.video_engine = VideoEngine()
        self.document_engine = DocumentEngine()
        self.ocr_engine = OCREngine()

    # =========================
    # MAIN CONVERSION METHOD
    # =========================
    def convert(self, input_path, target_format, options=None):
        if options is None:
            options = {}

        try:
            # Detect file type
            file_info = detect_file_type(input_path)
            source_type = file_info.get('type', 'unknown')

            # Validate conversion
            if not can_convert(input_path, target_format):
                return {
                    'success': False,
                    'error': f'Conversion from {source_type} to {target_format} not supported'
                }

            # Route based on type
            if source_type == 'pdf':
                return self._convert_from_pdf(input_path, target_format, options)

            elif source_type == 'image':
                return self._convert_from_image(input_path, target_format, options)

            elif source_type == 'video':
                return self._convert_from_video(input_path, target_format, options)

            elif source_type == 'audio':
                return self._convert_from_audio(input_path, target_format, options)

            elif source_type in ['document', 'spreadsheet', 'presentation']:
                return self._convert_from_document(input_path, target_format, options)

            else:
                return {
                    'success': False,
                    'error': f'Unsupported file type: {source_type}'
                }

        except Exception as e:
            return {
                'success': False,
                'error': f'Conversion failed: {str(e)}'
            }

    # =========================
    # PDF HANDLING
    # =========================
    def _convert_from_pdf(self, input_path, target_format, options):
        output_folder = options.get('output_folder', 'outputs')
        os.makedirs(output_folder, exist_ok=True)

        if target_format in ['png', 'jpg', 'jpeg']:
            dpi = options.get('dpi', 200)
            return self.pdf_engine.pdf_to_images(input_path, target_format, dpi, output_folder)

        elif target_format == 'txt':
            result = self.pdf_engine.extract_text(input_path)

            if result['success']:
                output_filename = f"{uuid.uuid4()}.txt"
                output_path = os.path.join(output_folder, output_filename)

                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result['text'])

                return {'success': True, 'output_path': output_path}

            return result

        elif target_format == 'docx':
            return self.document_engine.convert(input_path, 'docx', output_folder)

        else:
            return {
                'success': False,
                'error': f'PDF → {target_format} not supported'
            }

    # =========================
    # IMAGE HANDLING
    # =========================
    def _convert_from_image(self, input_path, target_format, options):
        output_folder = options.get('output_folder', 'outputs')
        os.makedirs(output_folder, exist_ok=True)

        if target_format == 'pdf':
            return self.image_engine.images_to_pdf([input_path], output_folder)

        elif target_format in ['png', 'jpg', 'jpeg', 'webp']:
            quality = options.get('quality', 85)
            return self.image_engine.convert_format(input_path, target_format, quality, output_folder)

        else:
            return {
                'success': False,
                'error': f'Image → {target_format} not supported'
            }

    # =========================
    # VIDEO HANDLING (LIMITED ON RENDER)
    # =========================
    def _convert_from_video(self, input_path, target_format, options):
        return {
            'success': False,
            'error': 'Video conversion not supported on Render (FFmpeg required)'
        }

    # =========================
    # AUDIO HANDLING
    # =========================
    def _convert_from_audio(self, input_path, target_format, options):
        return {
            'success': False,
            'error': 'Audio conversion not supported on Render'
        }

    # =========================
    # DOCUMENT HANDLING
    # =========================
    def _convert_from_document(self, input_path, target_format, options):
        output_folder = options.get('output_folder', 'outputs')
        os.makedirs(output_folder, exist_ok=True)

        return self.document_engine.convert(input_path, target_format, output_folder)

    # =========================
    # OCR (OPTIONAL)
    # =========================
    def perform_ocr(self, input_path, language='eng', output_format='text', options=None):
        if options is None:
            options = {}

        output_folder = options.get('output_folder', 'outputs')
        os.makedirs(output_folder, exist_ok=True)

        return self.ocr_engine.perform_ocr(input_path, language, output_format, output_folder)