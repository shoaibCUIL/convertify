import os
import uuid
import io
from typing import List, Dict, Tuple, Optional, Union
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
import fitz  # PyMuPDF
from pdf2image import convert_from_path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4, legal
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import img2pdf

class PDFEngine:
    """
    Advanced PDF processing engine with comprehensive features:
    - Creation, Reading, Writing
    - Merging, Splitting, Rearranging
    - Watermarking, Annotations
    - Encryption, Security
    - Form Filling
    - OCR Integration
    - Optimization
    - Metadata Management
    - Page Manipulation
    - Content Extraction
    """
    
    def __init__(self):
        self.temp_dir = "temp_pdf"
        os.makedirs(self.temp_dir, exist_ok=True)
    
    # =================== PDF CREATION ===================
    
    def create_pdf_from_text(self, text: str, output_path: str, 
                            page_size=letter, font_size=12, 
                            margins=(50, 50, 50, 50)):
        """
        Create PDF from plain text
        
        Args:
            text: Text content
            output_path: Output PDF path
            page_size: Page size (letter, A4, legal)
            font_size: Font size in points
            margins: (left, top, right, bottom) in points
        """
        c = canvas.Canvas(output_path, pagesize=page_size)
        width, height = page_size
        left_margin, top_margin, right_margin, bottom_margin = margins
        
        # Calculate text area
        text_width = width - left_margin - right_margin
        text_height = height - top_margin - bottom_margin
        
        # Split text into lines
        lines = text.split('\n')
        
        y = height - top_margin
        line_height = font_size + 4
        
        for line in lines:
            # Check if we need a new page
            if y < bottom_margin:
                c.showPage()
                y = height - top_margin
            
            # Wrap long lines
            if len(line) > 0:
                # Simple word wrap
                words = line.split()
                current_line = ""
                
                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    # Estimate if line fits (rough calculation)
                    if len(test_line) * (font_size * 0.5) < text_width:
                        current_line = test_line
                    else:
                        # Draw current line and start new one
                        if current_line:
                            c.drawString(left_margin, y, current_line)
                            y -= line_height
                            if y < bottom_margin:
                                c.showPage()
                                y = height - top_margin
                        current_line = word
                
                # Draw remaining text
                if current_line:
                    c.drawString(left_margin, y, current_line)
                    y -= line_height
            else:
                # Empty line
                y -= line_height
        
        c.save()
        return output_path
    
    def create_pdf_from_images(self, image_paths: List[str], output_path: str,
                              page_size: Optional[Tuple[int, int]] = None):
        """
        Create PDF from multiple images
        
        Args:
            image_paths: List of image file paths
            output_path: Output PDF path
            page_size: Optional page size (width, height), None for auto
        """
        if page_size:
            # Use img2pdf with specific page size
            layout_fun = img2pdf.get_layout_fun(page_size)
            with open(output_path, "wb") as f:
                f.write(img2pdf.convert(image_paths, layout_fun=layout_fun))
        else:
            # Auto size to fit images
            with open(output_path, "wb") as f:
                f.write(img2pdf.convert(image_paths))
        
        return output_path
    
    def create_blank_pdf(self, output_path: str, num_pages: int = 1,
                        page_size=letter):
        """Create blank PDF with specified number of pages"""
        c = canvas.Canvas(output_path, pagesize=page_size)
        
        for _ in range(num_pages):
            c.showPage()
        
        c.save()
        return output_path
    
    # =================== PDF READING ===================
    
    def get_pdf_info(self, pdf_path: str) -> Dict:
        """Get comprehensive PDF information"""
        info = {}
        
        try:
            # PyPDF2 for basic info
            with open(pdf_path, 'rb') as f:
                reader = PdfReader(f)
                
                info['pages'] = len(reader.pages)
                info['encrypted'] = reader.is_encrypted
                
                if reader.metadata:
                    info['metadata'] = {
                        key.lstrip('/'): value 
                        for key, value in reader.metadata.items()
                    }
                else:
                    info['metadata'] = {}
            
            # PyMuPDF for additional info
            doc = fitz.open(pdf_path)
            
            info['file_size'] = os.path.getsize(pdf_path)
            info['page_sizes'] = []
            
            for page in doc:
                rect = page.rect
                info['page_sizes'].append({
                    'width': rect.width,
                    'height': rect.height
                })
            
            # Count images and text
            total_images = 0
            has_text = False
            
            for page in doc:
                total_images += len(page.get_images())
                if page.get_text().strip():
                    has_text = True
            
            info['total_images'] = total_images
            info['has_text'] = has_text
            info['is_scanned'] = total_images > 0 and not has_text
            
            doc.close()
            
        except Exception as e:
            info['error'] = str(e)
        
        return info
    
    def read_pdf_text(self, pdf_path: str, page_numbers: Optional[List[int]] = None) -> str:
        """
        Extract text from PDF
        
        Args:
            pdf_path: PDF file path
            page_numbers: Specific pages to extract (1-indexed), None for all
        """
        doc = fitz.open(pdf_path)
        text = ""
        
        if page_numbers:
            pages_to_read = [p - 1 for p in page_numbers if 0 < p <= len(doc)]
        else:
            pages_to_read = range(len(doc))
        
        for page_num in pages_to_read:
            page = doc[page_num]
            text += f"\n--- Page {page_num + 1} ---\n\n"
            text += page.get_text()
        
        doc.close()
        return text
    
    # =================== PDF MERGING ===================
    
    def merge_pdfs(self, pdf_paths: List[str], output_path: str,
                   bookmarks: bool = True) -> str:
        """
        Merge multiple PDFs
        
        Args:
            pdf_paths: List of PDF file paths
            output_path: Output PDF path
            bookmarks: Add bookmarks for each source PDF
        """
        merger = PdfMerger()
        
        for i, pdf_path in enumerate(pdf_paths):
            bookmark_name = os.path.basename(pdf_path) if bookmarks else None
            merger.append(pdf_path, import_outline=False)
            
            if bookmark_name:
                # Add bookmark at the start of this PDF
                merger.add_outline_item(bookmark_name, i)
        
        merger.write(output_path)
        merger.close()
        
        return output_path
    
    def merge_pdfs_with_pages(self, sources: List[Dict], output_path: str) -> str:
        """
        Merge PDFs with specific page selections
        
        Args:
            sources: List of dicts with 'path' and optional 'pages' (e.g., "1-3,5,7-10")
            output_path: Output PDF path
        
        Example:
            sources = [
                {'path': 'doc1.pdf', 'pages': '1-3'},
                {'path': 'doc2.pdf', 'pages': '1,5,10-12'},
                {'path': 'doc3.pdf'}  # All pages
            ]
        """
        merger = PdfMerger()
        
        for source in sources:
            pdf_path = source['path']
            pages = source.get('pages')
            
            if pages:
                # Parse page ranges
                page_ranges = self._parse_page_ranges(pages)
                for page in page_ranges:
                    merger.append(pdf_path, pages=(page - 1, page))
            else:
                # All pages
                merger.append(pdf_path)
        
        merger.write(output_path)
        merger.close()
        
        return output_path
    
    # =================== PDF SPLITTING ===================
    
    def split_pdf(self, pdf_path: str, output_dir: str,
                  split_type: str = "pages", **kwargs) -> List[str]:
        """
        Split PDF using various methods
        
        Args:
            pdf_path: Input PDF path
            output_dir: Output directory
            split_type: "pages" (each page), "chunks" (every N pages), 
                       "ranges" (custom ranges), "size" (by file size)
            **kwargs: Additional arguments depending on split_type
        
        Returns:
            List of output file paths
        """
        os.makedirs(output_dir, exist_ok=True)
        
        if split_type == "pages":
            return self._split_by_pages(pdf_path, output_dir)
        elif split_type == "chunks":
            chunk_size = kwargs.get('chunk_size', 1)
            return self._split_by_chunks(pdf_path, output_dir, chunk_size)
        elif split_type == "ranges":
            ranges = kwargs.get('ranges', [])
            return self._split_by_ranges(pdf_path, output_dir, ranges)
        elif split_type == "size":
            max_size_mb = kwargs.get('max_size_mb', 5)
            return self._split_by_size(pdf_path, output_dir, max_size_mb)
        else:
            raise ValueError(f"Unknown split_type: {split_type}")
    
    def _split_by_pages(self, pdf_path: str, output_dir: str) -> List[str]:
        """Split PDF into individual pages"""
        reader = PdfReader(pdf_path)
        output_files = []
        
        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)
            
            output_path = os.path.join(output_dir, f"page_{i + 1}.pdf")
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            output_files.append(output_path)
        
        return output_files
    
    def _split_by_chunks(self, pdf_path: str, output_dir: str, 
                        chunk_size: int) -> List[str]:
        """Split PDF into chunks of N pages"""
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        output_files = []
        
        for start in range(0, total_pages, chunk_size):
            writer = PdfWriter()
            end = min(start + chunk_size, total_pages)
            
            for i in range(start, end):
                writer.add_page(reader.pages[i])
            
            output_path = os.path.join(output_dir, 
                                      f"chunk_{start + 1}-{end}.pdf")
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            output_files.append(output_path)
        
        return output_files
    
    def _split_by_ranges(self, pdf_path: str, output_dir: str,
                        ranges: List[str]) -> List[str]:
        """Split PDF by custom page ranges"""
        reader = PdfReader(pdf_path)
        output_files = []
        
        for i, range_str in enumerate(ranges):
            pages = self._parse_page_ranges(range_str)
            writer = PdfWriter()
            
            for page_num in pages:
                if 0 < page_num <= len(reader.pages):
                    writer.add_page(reader.pages[page_num - 1])
            
            output_path = os.path.join(output_dir, f"range_{i + 1}.pdf")
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            output_files.append(output_path)
        
        return output_files
    
    def _split_by_size(self, pdf_path: str, output_dir: str,
                      max_size_mb: float) -> List[str]:
        """Split PDF to not exceed specified file size"""
        reader = PdfReader(pdf_path)
        output_files = []
        
        current_writer = PdfWriter()
        current_pages = 0
        part_num = 1
        
        for i, page in enumerate(reader.pages):
            current_writer.add_page(page)
            current_pages += 1
            
            # Check size (write to temp buffer)
            temp_buffer = io.BytesIO()
            current_writer.write(temp_buffer)
            size_mb = len(temp_buffer.getvalue()) / (1024 * 1024)
            
            if size_mb >= max_size_mb or i == len(reader.pages) - 1:
                # Save current part
                output_path = os.path.join(output_dir, f"part_{part_num}.pdf")
                with open(output_path, 'wb') as f:
                    current_writer.write(f)
                
                output_files.append(output_path)
                
                # Start new part
                current_writer = PdfWriter()
                current_pages = 0
                part_num += 1
        
        return output_files
    
    # =================== PAGE MANIPULATION ===================
    
    def rotate_pages(self, pdf_path: str, output_path: str,
                    rotation: int, pages: Union[str, List[int]] = "all") -> str:
        """
        Rotate PDF pages
        
        Args:
            pdf_path: Input PDF path
            output_path: Output PDF path
            rotation: Degrees (90, 180, 270, -90)
            pages: "all" or list of page numbers (1-indexed) or "1,3-5,7"
        """
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        
        # Parse pages
        if pages == "all":
            pages_to_rotate = set(range(len(reader.pages)))
        elif isinstance(pages, str):
            pages_to_rotate = set(p - 1 for p in self._parse_page_ranges(pages))
        else:
            pages_to_rotate = set(p - 1 for p in pages)
        
        for i, page in enumerate(reader.pages):
            if i in pages_to_rotate:
                page.rotate(rotation)
            writer.add_page(page)
        
        with open(output_path, 'wb') as f:
            writer.write(f)
        
        return output_path
    
    def reorder_pages(self, pdf_path: str, output_path: str,
                     new_order: List[int]) -> str:
        """
        Reorder PDF pages
        
        Args:
            pdf_path: Input PDF path
            output_path: Output PDF path
            new_order: List of page numbers in desired order (1-indexed)
        """
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        
        for page_num in new_order:
            if 0 < page_num <= len(reader.pages):
                writer.add_page(reader.pages[page_num - 1])
        
        with open(output_path, 'wb') as f:
            writer.write(f)
        
        return output_path
    
    def delete_pages(self, pdf_path: str, output_path: str,
                    pages_to_delete: Union[str, List[int]]) -> str:
        """
        Delete specific pages from PDF
        
        Args:
            pdf_path: Input PDF path
            output_path: Output PDF path
            pages_to_delete: Page numbers to delete (1-indexed) or "1,3-5,7"
        """
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        
        # Parse pages to delete
        if isinstance(pages_to_delete, str):
            delete_set = set(p - 1 for p in self._parse_page_ranges(pages_to_delete))
        else:
            delete_set = set(p - 1 for p in pages_to_delete)
        
        for i, page in enumerate(reader.pages):
            if i not in delete_set:
                writer.add_page(page)
        
        with open(output_path, 'wb') as f:
            writer.write(f)
        
        return output_path
    
    def insert_pages(self, pdf_path: str, output_path: str,
                    insert_pdf: str, position: int) -> str:
        """
        Insert pages from another PDF at specific position
        
        Args:
            pdf_path: Main PDF path
            output_path: Output PDF path
            insert_pdf: PDF to insert
            position: Position to insert (1-indexed, 0 for beginning)
        """
        merger = PdfMerger()
        
        if position == 0:
            merger.append(insert_pdf)
            merger.append(pdf_path)
        else:
            reader = PdfReader(pdf_path)
            writer = PdfWriter()
            
            # Add pages before insertion point
            for i in range(min(position, len(reader.pages))):
                writer.add_page(reader.pages[i])
            
            # Write first part
            temp_file = os.path.join(self.temp_dir, f"temp_{uuid.uuid4()}.pdf")
            with open(temp_file, 'wb') as f:
                writer.write(f)
            
            # Merge all parts
            merger.append(temp_file)
            merger.append(insert_pdf)
            
            # Add remaining pages
            if position < len(reader.pages):
                writer2 = PdfWriter()
                for i in range(position, len(reader.pages)):
                    writer2.add_page(reader.pages[i])
                
                temp_file2 = os.path.join(self.temp_dir, f"temp2_{uuid.uuid4()}.pdf")
                with open(temp_file2, 'wb') as f:
                    writer2.write(f)
                
                merger.append(temp_file2)
            
            merger.write(output_path)
            merger.close()
            
            # Cleanup temp files
            try:
                os.remove(temp_file)
                if position < len(reader.pages):
                    os.remove(temp_file2)
            except:
                pass
            
            return output_path
        
        merger.write(output_path)
        merger.close()
        return output_path
    
    # =================== WATERMARKING ===================
    
    def add_text_watermark(self, pdf_path: str, output_path: str,
                          text: str, opacity: float = 0.3,
                          position: str = "center", angle: int = 45,
                          font_size: int = 60, color: Tuple[float, float, float] = (0.5, 0.5, 0.5)) -> str:
        """
        Add text watermark to all pages
        
        Args:
            pdf_path: Input PDF path
            output_path: Output PDF path
            text: Watermark text
            opacity: Transparency (0-1)
            position: "center", "top-left", "top-right", "bottom-left", "bottom-right"
            angle: Rotation angle
            font_size: Font size in points
            color: RGB color tuple (0-1 range)
        """
        doc = fitz.open(pdf_path)
        
        for page in doc:
            rect = page.rect
            width = rect.width
            height = rect.height
            
            # Determine position
            if position == "center":
                x, y = width / 2, height / 2
            elif position == "top-left":
                x, y = 100, 100
            elif position == "top-right":
                x, y = width - 100, 100
            elif position == "bottom-left":
                x, y = 100, height - 100
            elif position == "bottom-right":
                x, y = width - 100, height - 100
            else:
                x, y = width / 2, height / 2
            
            # Add watermark
            page.insert_text(
                fitz.Point(x, y),
                text,
                fontsize=font_size,
                rotate=angle,
                color=color,
                opacity=opacity,
                overlay=False
            )
        
        doc.save(output_path)
        doc.close()
        
        return output_path
    
    def add_image_watermark(self, pdf_path: str, output_path: str,
                           image_path: str, opacity: float = 0.5,
                           position: str = "center", scale: float = 0.3) -> str:
        """
        Add image watermark to all pages
        
        Args:
            pdf_path: Input PDF path
            output_path: Output PDF path
            image_path: Watermark image path
            opacity: Transparency (0-1)
            position: "center", "top-left", "top-right", "bottom-left", "bottom-right"
            scale: Size relative to page (0-1)
        """
        doc = fitz.open(pdf_path)
        watermark_img = Image.open(image_path)
        
        for page in doc:
            rect = page.rect
            width = rect.width
            height = rect.height
            
            # Calculate watermark size
            wm_width = int(width * scale)
            wm_height = int(wm_width * watermark_img.height / watermark_img.width)
            
            # Determine position
            if position == "center":
                x = (width - wm_width) / 2
                y = (height - wm_height) / 2
            elif position == "top-left":
                x, y = 20, 20
            elif position == "top-right":
                x = width - wm_width - 20
                y = 20
            elif position == "bottom-left":
                x = 20
                y = height - wm_height - 20
            elif position == "bottom-right":
                x = width - wm_width - 20
                y = height - wm_height - 20
            else:
                x = (width - wm_width) / 2
                y = (height - wm_height) / 2
            
            # Resize watermark
            wm_resized = watermark_img.resize((wm_width, wm_height), Image.Resampling.LANCZOS)
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            wm_resized.save(img_bytes, format='PNG')
            img_bytes = img_bytes.getvalue()
            
            # Add to page
            img_rect = fitz.Rect(x, y, x + wm_width, y + wm_height)
            page.insert_image(img_rect, stream=img_bytes, overlay=False, opacity=opacity)
        
        doc.save(output_path)
        doc.close()
        
        return output_path
    
    # =================== SECURITY & ENCRYPTION ===================
    
    def encrypt_pdf(self, pdf_path: str, output_path: str,
                   user_password: str, owner_password: Optional[str] = None,
                   allow_printing: bool = True,
                   allow_copying: bool = False,
                   allow_modifying: bool = False,
                   allow_annotating: bool = False) -> str:
        """
        Encrypt PDF with password and permissions
        
        Args:
            pdf_path: Input PDF path
            output_path: Output PDF path
            user_password: Password to open PDF
            owner_password: Password for full permissions (defaults to user_password)
            allow_printing: Allow printing
            allow_copying: Allow copying text
            allow_modifying: Allow modifying content
            allow_annotating: Allow adding annotations
        """
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        
        # Copy all pages
        for page in reader.pages:
            writer.add_page(page)
        
        # Set permissions
        if owner_password is None:
            owner_password = user_password
        
        # Build permissions flag
        permissions = 0
        if allow_printing:
            permissions |= 4
        if allow_modifying:
            permissions |= 8
        if allow_copying:
            permissions |= 16
        if allow_annotating:
            permissions |= 32
        
        writer.encrypt(
            user_pwd=user_password,
            owner_pwd=owner_password,
            permissions_flag=permissions
        )
        
        with open(output_path, 'wb') as f:
            writer.write(f)
        
        return output_path
    
    def decrypt_pdf(self, pdf_path: str, output_path: str, password: str) -> str:
        """
        Remove password protection from PDF
        
        Args:
            pdf_path: Encrypted PDF path
            output_path: Output PDF path
            password: PDF password
        """
        reader = PdfReader(pdf_path)
        
        if reader.is_encrypted:
            if not reader.decrypt(password):
                raise ValueError("Incorrect password")
        
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
        
        with open(output_path, 'wb') as f:
            writer.write(f)
        
        return output_path
    
    # =================== OPTIMIZATION ===================
    
    def optimize_pdf(self, pdf_path: str, output_path: str,
                    quality: str = "medium", 
                    remove_duplicates: bool = True,
                    compress_images: bool = True) -> str:
        """
        Optimize PDF file size
        
        Args:
            pdf_path: Input PDF path
            output_path: Output PDF path
            quality: "low", "medium", "high"
            remove_duplicates: Remove duplicate objects
            compress_images: Compress embedded images
        """
        doc = fitz.open(pdf_path)
        
        # Image compression settings
        quality_settings = {
            "low": 50,
            "medium": 75,
            "high": 85
        }
        
        jpeg_quality = quality_settings.get(quality, 75)
        
        if compress_images:
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Get images
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    
                    try:
                        # Extract image
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        
                        # Load with PIL
                        pil_image = Image.open(io.BytesIO(image_bytes))
                        
                        # Convert RGBA to RGB
                        if pil_image.mode == 'RGBA':
                            pil_image = pil_image.convert('RGB')
                        
                        # Compress
                        output_buffer = io.BytesIO()
                        pil_image.save(output_buffer, format='JPEG', 
                                     quality=jpeg_quality, optimize=True)
                        
                        # Replace image
                        page.replace_image(xref, stream=output_buffer.getvalue())
                    
                    except Exception as e:
                        # Skip problematic images
                        continue
        
        # Save with optimization options
        doc.save(output_path, 
                garbage=4,  # Full garbage collection
                deflate=True,  # Deflate compression
                clean=True)  # Clean content streams
        doc.close()
        
        return output_path
    
    # =================== METADATA ===================
    
    def set_metadata(self, pdf_path: str, output_path: str, metadata: Dict) -> str:
        """
        Set PDF metadata
        
        Args:
            pdf_path: Input PDF path
            output_path: Output PDF path
            metadata: Dict with keys: title, author, subject, keywords, creator, producer
        """
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
        
        # Set metadata
        writer.add_metadata({
            f'/{key.capitalize()}': value
            for key, value in metadata.items()
        })
        
        with open(output_path, 'wb') as f:
            writer.write(f)
        
        return output_path
    
    def get_metadata(self, pdf_path: str) -> Dict:
        """Get PDF metadata"""
        reader = PdfReader(pdf_path)
        
        if reader.metadata:
            return {
                key.lstrip('/'): value
                for key, value in reader.metadata.items()
            }
        else:
            return {}
    
    # =================== FORM FILLING ===================
    
    def fill_form(self, pdf_path: str, output_path: str, form_data: Dict) -> str:
        """
        Fill PDF form fields
        
        Args:
            pdf_path: Input PDF with form fields
            output_path: Output PDF path
            form_data: Dict mapping field names to values
        """
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        
        # Copy pages
        for page in reader.pages:
            writer.add_page(page)
        
        # Update form fields
        if writer.get_fields():
            writer.update_page_form_field_values(
                writer.pages[0], 
                form_data
            )
        
        with open(output_path, 'wb') as f:
            writer.write(f)
        
        return output_path
    
    def get_form_fields(self, pdf_path: str) -> Dict:
        """Get all form fields from PDF"""
        reader = PdfReader(pdf_path)
        
        fields = reader.get_fields()
        
        if fields:
            return {
                name: {
                    'value': field.get('/V', ''),
                    'type': field.get('/FT', ''),
                    'flags': field.get('/Ff', 0)
                }
                for name, field in fields.items()
            }
        else:
            return {}
    
    # =================== HELPER METHODS ===================
    
    def _parse_page_ranges(self, ranges_str: str) -> List[int]:
        """Parse page range string like '1,3-5,7-10' into list of page numbers"""
        pages = []
        
        for part in ranges_str.split(','):
            part = part.strip()
            
            if '-' in part:
                start, end = part.split('-')
                start = int(start.strip())
                end = int(end.strip())
                pages.extend(range(start, end + 1))
            else:
                pages.append(int(part))
        
        return sorted(set(pages))
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            os.makedirs(self.temp_dir, exist_ok=True)