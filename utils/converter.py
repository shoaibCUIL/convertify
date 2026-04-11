"""
Universal File Converter
Routes conversion requests to appropriate engines
"""

import os
from .file_detector import detect_file_type, can_convert
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
    
    def convert(self, input_path, target_format, options=None):
        """
        Convert file to target format
        
        Args:
            input_path: Path to input file
            target_format: Target format (without dot)
            options: Optional conversion options
            
        Returns:
            dict: Conversion result
        """
        if options is None:
            options = {}
        
        # Detect file type
        file_info = detect_file_type(input_path)
        source_type = file_info['type']
        
        # Check if conversion is supported
        if not can_convert(input_path, target_format):
            return {
                'success': False,
                'error': f'Conversion from {source_type} to {target_format} is not supported'
            }
        
        # Route to appropriate conversion method
        try:
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
    
    def _convert_from_pdf(self, input_path, target_format, options):
        """Convert from PDF"""
        output_folder = options.get('output_folder', 'outputs')
        
        if target_format in ['png', 'jpg', 'jpeg']:
            dpi = options.get('dpi', 200)
            return self.pdf_engine.pdf_to_images(input_path, target_format, dpi, output_folder)
        
        elif target_format == 'txt':
            result = self.pdf_engine.extract_text(input_path)
            if result['success']:
                # Save to file
                import uuid
                output_filename = f"converted_{uuid.uuid4()}.txt"
                output_path = os.path.join(output_folder, output_filename)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result['text'])
                
                return {
                    'success': True,
                    'output_path': output_path
                }
            return result
        
        elif target_format == 'docx':
            # Use document engine to convert PDF to DOCX
            return self.document_engine.convert_format(input_path, 'docx', output_folder)
        
        elif target_format == 'html':
            # Convert PDF to HTML
            return self.document_engine.convert_format(input_path, 'html', output_folder)
        
        else:
            return {
                'success': False,
                'error': f'PDF to {target_format} conversion not implemented'
            }
    
    def _convert_from_image(self, input_path, target_format, options):
        """Convert from image"""
        output_folder = options.get('output_folder', 'outputs')
        
        if target_format == 'pdf':
            return self.image_engine.images_to_pdf([input_path], output_folder)
        
        elif target_format in ['png', 'jpg', 'jpeg', 'webp', 'bmp', 'tiff', 'gif']:
            quality = options.get('quality', 85)
            return self.image_engine.convert_format(input_path, target_format, quality, output_folder)
        
        else:
            return {
                'success': False,
                'error': f'Image to {target_format} conversion not implemented'
            }
    
    def _convert_from_video(self, input_path, target_format, options):
        """Convert from video"""
        output_folder = options.get('output_folder', 'outputs')
        
        if target_format in ['mp3', 'wav', 'ogg', 'aac', 'm4a']:
            # Extract audio
            return self.video_engine.extract_audio(input_path, target_format, output_folder)
        
        elif target_format in ['mp4', 'avi', 'mov', 'mkv', 'webm']:
            # Convert video format
            quality = options.get('quality', 'medium')
            return self.video_engine.convert_format(input_path, target_format, quality, output_folder)
        
        else:
            return {
                'success': False,
                'error': f'Video to {target_format} conversion not implemented'
            }
    
    def _convert_from_audio(self, input_path, target_format, options):
        """Convert from audio"""
        output_folder = options.get('output_folder', 'outputs')
        
        if target_format in ['mp3', 'wav', 'ogg', 'aac', 'm4a']:
            # Use video engine for audio conversion (FFmpeg handles both)
            return self.video_engine.convert_audio_format(input_path, target_format, output_folder)
        
        else:
            return {
                'success': False,
                'error': f'Audio to {target_format} conversion not implemented'
            }
    
    def _convert_from_document(self, input_path, target_format, options):
        """Convert from document (Word, Excel, PowerPoint, etc.)"""
        output_folder = options.get('output_folder', 'outputs')
        
        # Use document engine for all document conversions
        return self.document_engine.convert_format(input_path, target_format, output_folder)