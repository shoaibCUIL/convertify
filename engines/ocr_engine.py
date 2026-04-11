"""
OCR Engine
Handles OCR (Optical Character Recognition) using Tesseract
"""

import os
import uuid
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
import pikepdf


class OCREngine:
    """Engine for OCR operations"""
    
    def perform_ocr(self, input_path, language, output_format, output_folder):
        """
        Perform OCR on image or PDF
        
        Args:
            input_path: Image or PDF file path
            language: OCR language (eng, spa, fra, etc.)
            output_format: Output format (text, pdf, searchable_pdf)
            output_folder: Output directory
            
        Returns:
            dict: Result with extracted text or output path
        """
        try:
            # Detect file type
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
        try:
            image = Image.open(input_path)
            
            # Perform OCR
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
                
                # Create searchable PDF
                pdf_bytes = pytesseract.image_to_pdf_or_hocr(image, lang=language, extension='pdf')
                
                with open(output_path, 'wb') as f:
                    f.write(pdf_bytes)
                
                return {
                    'success': True,
                    'output_path': output_path
                }
            
            else:
                return {
                    'success': False,
                    'error': f'Unsupported output format: {output_format}'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _ocr_pdf(self, input_path, language, output_format, output_folder):
        """Perform OCR on PDF file"""
        try:
            # Convert PDF pages to images
            images = convert_from_path(input_path, dpi=300)
            
            all_text = []
            
            # Process each page
            for i, image in enumerate(images):
                text = pytesseract.image_to_string(image, lang=language)
                all_text.append(f"--- Page {i + 1} ---\n{text}\n")
            
            combined_text = '\n'.join(all_text)
            
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
            
            elif output_format in ['pdf', 'searchable_pdf']:
                output_filename = f"ocr_searchable_{uuid.uuid4()}.pdf"
                output_path = os.path.join(output_folder, output_filename)
                
                # Create searchable PDF
                temp_pdfs = []
                
                for i, image in enumerate(images):
                    pdf_bytes = pytesseract.image_to_pdf_or_hocr(image, lang=language, extension='pdf')
                    temp_path = os.path.join(output_folder, f"temp_page_{i}_{uuid.uuid4()}.pdf")
                    
                    with open(temp_path, 'wb') as f:
                        f.write(pdf_bytes)
                    
                    temp_pdfs.append(temp_path)
                
                # Merge all pages
                merger = PdfWriter()
                for pdf_path in temp_pdfs:
                    reader = PdfReader(pdf_path)
                    for page in reader.pages:
                        merger.add_page(page)
                
                with open(output_path, 'wb') as output_file:
                    merger.write(output_file)
                
                # Clean up temp files
                for temp_pdf in temp_pdfs:
                    try:
                        os.remove(temp_pdf)
                    except:
                        pass
                
                return {
                    'success': True,
                    'output_path': output_path
                }
            
            else:
                return {
                    'success': False,
                    'error': f'Unsupported output format: {output_format}'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def make_pdf_searchable(self, input_path, language, output_folder):
        """
        Convert scanned PDF to searchable PDF
        
        Args:
            input_path: PDF file path
            language: OCR language
            output_folder: Output directory
            
        Returns:
            dict: Result with output path
        """
        return self.perform_ocr(input_path, language, 'searchable_pdf', output_folder)
    
    def extract_text_from_image(self, input_path, language, output_folder):
        """
        Extract text from image
        
        Args:
            input_path: Image file path
            language: OCR language
            output_folder: Output directory
            
        Returns:
            dict: Result with extracted text
        """
        return self.perform_ocr(input_path, language, 'text', output_folder)
    
    def get_supported_languages(self):
        """
        Get list of supported OCR languages
        
        Returns:
            list: Language codes
        """
        try:
            languages = pytesseract.get_languages()
            return {
                'success': True,
                'languages': languages
            }
        except:
            # Return common languages as fallback
            return {
                'success': True,
                'languages': ['eng', 'spa', 'fra', 'deu', 'ita', 'por', 'rus', 'chi_sim', 'jpn', 'kor']
            }