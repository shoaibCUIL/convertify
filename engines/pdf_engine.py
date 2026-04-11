"""
PDF Engine
Handles all PDF-related operations: merge, split, compress, convert, etc.
"""

import os
import uuid
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
import pikepdf
import img2pdf
from pdf2image import convert_from_path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pdfplumber
from PIL import Image


class PDFEngine:
    """Engine for PDF operations"""
    
    def merge_pdfs(self, input_paths, output_folder):
        """
        Merge multiple PDF files
        
        Args:
            input_paths: List of PDF file paths
            output_folder: Output directory
            
        Returns:
            dict: Result with output path
        """
        try:
            merger = PdfMerger()
            
            for pdf_path in input_paths:
                merger.append(pdf_path)
            
            output_filename = f"merged_{uuid.uuid4()}.pdf"
            output_path = os.path.join(output_folder, output_filename)
            
            merger.write(output_path)
            merger.close()
            
            return {
                'success': True,
                'output_path': output_path
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def split_pdf(self, input_path, ranges, output_folder):
        """
        Split PDF into multiple files
        
        Args:
            input_path: PDF file path
            ranges: List of page ranges [[1,3], [4,6]] or empty for single pages
            output_folder: Output directory
            
        Returns:
            dict: Result with output paths
        """
        try:
            reader = PdfReader(input_path)
            total_pages = len(reader.pages)
            output_paths = []
            
            # If no ranges specified, split each page
            if not ranges:
                ranges = [[i, i] for i in range(1, total_pages + 1)]
            
            for idx, page_range in enumerate(ranges):
                writer = PdfWriter()
                start_page = page_range[0] - 1  # Convert to 0-indexed
                end_page = page_range[1]
                
                for page_num in range(start_page, min(end_page, total_pages)):
                    writer.add_page(reader.pages[page_num])
                
                output_filename = f"split_{idx + 1}_{uuid.uuid4()}.pdf"
                output_path = os.path.join(output_folder, output_filename)
                
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                output_paths.append(output_path)
            
            return {
                'success': True,
                'output_paths': output_paths
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def compress_pdf(self, input_path, quality, output_folder):
        """
        Compress PDF file
        
        Args:
            input_path: PDF file path
            quality: Quality level (low, medium, high)
            output_folder: Output directory
            
        Returns:
            dict: Result with compression stats
        """
        try:
            # Quality settings for pikepdf
            quality_settings = {
                'low': {'jpeg_quality': 50, 'image_dpi': 72},
                'medium': {'jpeg_quality': 75, 'image_dpi': 150},
                'high': {'jpeg_quality': 85, 'image_dpi': 200}
            }
            
            settings = quality_settings.get(quality, quality_settings['medium'])
            
            output_filename = f"compressed_{uuid.uuid4()}.pdf"
            output_path = os.path.join(output_folder, output_filename)
            
            # Open and optimize PDF
            with pikepdf.open(input_path) as pdf:
                # Compress images in PDF
                for page in pdf.pages:
                    for image_key in page.images.keys():
                        try:
                            image = page.images[image_key]
                            # Image compression logic would go here
                            # This is simplified - actual implementation would decompress,
                            # resize, and recompress images
                        except:
                            pass
                
                pdf.save(output_path, compress_streams=True, 
                        object_stream_mode=pikepdf.ObjectStreamMode.generate)
            
            # Get file sizes
            original_size = os.path.getsize(input_path)
            compressed_size = os.path.getsize(output_path)
            compression_ratio = (1 - compressed_size / original_size) * 100
            
            return {
                'success': True,
                'output_path': output_path,
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_ratio': f"{compression_ratio:.1f}%"
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def pdf_to_images(self, input_path, image_format, dpi, output_folder):
        """
        Convert PDF pages to images
        
        Args:
            input_path: PDF file path
            image_format: Output format (png, jpg, jpeg)
            dpi: Resolution (dots per inch)
            output_folder: Output directory
            
        Returns:
            dict: Result with image paths
        """
        try:
            images = convert_from_path(input_path, dpi=dpi)
            output_paths = []
            
            for i, image in enumerate(images):
                output_filename = f"page_{i + 1}_{uuid.uuid4()}.{image_format}"
                output_path = os.path.join(output_folder, output_filename)
                
                if image_format.lower() in ['jpg', 'jpeg']:
                    image.save(output_path, 'JPEG', quality=95)
                else:
                    image.save(output_path, image_format.upper())
                
                output_paths.append(output_path)
            
            return {
                'success': True,
                'output_paths': output_paths
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def add_watermark(self, input_path, watermark_text, opacity, output_folder):
        """
        Add text watermark to PDF
        
        Args:
            input_path: PDF file path
            watermark_text: Text to use as watermark
            opacity: Watermark opacity (0-1)
            output_folder: Output directory
            
        Returns:
            dict: Result with output path
        """
        try:
            from reportlab.lib.colors import Color
            
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            # Create watermark PDF for each page
            for page in reader.pages:
                # Get page dimensions
                page_width = float(page.mediabox.width)
                page_height = float(page.mediabox.height)
                
                # Create watermark
                watermark_path = os.path.join(output_folder, f"temp_watermark_{uuid.uuid4()}.pdf")
                c = canvas.Canvas(watermark_path, pagesize=(page_width, page_height))
                
                # Set watermark properties
                c.setFont("Helvetica", 60)
                c.setFillColor(Color(0.5, 0.5, 0.5, alpha=opacity))
                c.saveState()
                c.translate(page_width / 2, page_height / 2)
                c.rotate(45)
                c.drawCentredString(0, 0, watermark_text)
                c.restoreState()
                c.save()
                
                # Merge watermark with page
                watermark_reader = PdfReader(watermark_path)
                page.merge_page(watermark_reader.pages[0])
                writer.add_page(page)
                
                # Clean up temp watermark
                os.remove(watermark_path)
            
            output_filename = f"watermarked_{uuid.uuid4()}.pdf"
            output_path = os.path.join(output_folder, output_filename)
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            return {
                'success': True,
                'output_path': output_path
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def rotate_pages(self, input_path, rotation, pages, output_folder):
        """
        Rotate PDF pages
        
        Args:
            input_path: PDF file path
            rotation: Rotation angle (90, 180, 270)
            pages: 'all' or list of page numbers
            output_folder: Output directory
            
        Returns:
            dict: Result with output path
        """
        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            total_pages = len(reader.pages)
            pages_to_rotate = range(total_pages) if pages == 'all' else [p - 1 for p in pages]
            
            for i, page in enumerate(reader.pages):
                if i in pages_to_rotate:
                    page.rotate(rotation)
                writer.add_page(page)
            
            output_filename = f"rotated_{uuid.uuid4()}.pdf"
            output_path = os.path.join(output_folder, output_filename)
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            return {
                'success': True,
                'output_path': output_path
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def protect_pdf(self, input_path, password, output_folder):
        """
        Add password protection to PDF
        
        Args:
            input_path: PDF file path
            password: Password to set
            output_folder: Output directory
            
        Returns:
            dict: Result with output path
        """
        try:
            output_filename = f"protected_{uuid.uuid4()}.pdf"
            output_path = os.path.join(output_folder, output_filename)
            
            with pikepdf.open(input_path) as pdf:
                pdf.save(output_path, encryption=pikepdf.Encryption(
                    user=password,
                    owner=password,
                    allow=pikepdf.Permissions(
                        accessibility=True,
                        extract=False,
                        modify_annotation=False,
                        modify_assembly=False,
                        modify_form=False,
                        modify_other=False,
                        print_lowres=True,
                        print_highres=True
                    )
                ))
            
            return {
                'success': True,
                'output_path': output_path
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def unlock_pdf(self, input_path, password, output_folder):
        """
        Remove password protection from PDF
        
        Args:
            input_path: PDF file path
            password: Current password
            output_folder: Output directory
            
        Returns:
            dict: Result with output path
        """
        try:
            output_filename = f"unlocked_{uuid.uuid4()}.pdf"
            output_path = os.path.join(output_folder, output_filename)
            
            with pikepdf.open(input_path, password=password) as pdf:
                pdf.save(output_path)
            
            return {
                'success': True,
                'output_path': output_path
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': 'Incorrect password or unable to unlock PDF'
            }
    
    def add_page_numbers(self, input_path, position, output_folder):
        """
        Add page numbers to PDF
        
        Args:
            input_path: PDF file path
            position: Position of page numbers
            output_folder: Output directory
            
        Returns:
            dict: Result with output path
        """
        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            total_pages = len(reader.pages)
            
            for page_num, page in enumerate(reader.pages):
                # Get page dimensions
                page_width = float(page.mediabox.width)
                page_height = float(page.mediabox.height)
                
                # Create page number overlay
                overlay_path = os.path.join(output_folder, f"temp_pagenum_{uuid.uuid4()}.pdf")
                c = canvas.Canvas(overlay_path, pagesize=(page_width, page_height))
                
                # Position the page number
                positions = {
                    'bottom-center': (page_width / 2, 30),
                    'bottom-right': (page_width - 50, 30),
                    'bottom-left': (50, 30),
                    'top-center': (page_width / 2, page_height - 30),
                    'top-right': (page_width - 50, page_height - 30),
                    'top-left': (50, page_height - 30)
                }
                
                x, y = positions.get(position, positions['bottom-center'])
                
                c.setFont("Helvetica", 12)
                c.drawCentredString(x, y, f"{page_num + 1}")
                c.save()
                
                # Merge with page
                overlay_reader = PdfReader(overlay_path)
                page.merge_page(overlay_reader.pages[0])
                writer.add_page(page)
                
                # Clean up
                os.remove(overlay_path)
            
            output_filename = f"numbered_{uuid.uuid4()}.pdf"
            output_path = os.path.join(output_folder, output_filename)
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            return {
                'success': True,
                'output_path': output_path
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_text(self, input_path):
        """
        Extract text from PDF
        
        Args:
            input_path: PDF file path
            
        Returns:
            dict: Result with extracted text
        """
        try:
            text = ""
            
            with pdfplumber.open(input_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
            
            return {
                'success': True,
                'text': text.strip()
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }