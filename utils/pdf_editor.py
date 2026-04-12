import os
import uuid
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path
from PIL import Image
import fitz  # PyMuPDF

class PDFEditor:
    """Edit PDF files - rotate, crop, add/remove pages, etc."""
    
    def rotate_pages(self, input_file, output_folder, angle, pages="all"):
        """Rotate PDF pages
        
        Args:
            input_file: Path to input PDF
            output_folder: Output directory
            angle: Rotation angle (90, 180, 270)
            pages: "all" or list of page numbers (1-indexed)
        """
        output_filename = f"{uuid.uuid4()}_rotated.pdf"
        output_path = os.path.join(output_folder, output_filename)
        
        reader = PdfReader(input_file)
        writer = PdfWriter()
        
        total_pages = len(reader.pages)
        
        # Determine which pages to rotate
        if pages == "all":
            pages_to_rotate = list(range(total_pages))
        else:
            # Convert 1-indexed to 0-indexed
            pages_to_rotate = [p - 1 for p in pages if 0 < p <= total_pages]
        
        for i, page in enumerate(reader.pages):
            if i in pages_to_rotate:
                page.rotate(angle)
            writer.add_page(page)
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        return output_path
    
    def delete_pages(self, input_file, output_folder, pages_to_delete):
        """Delete specific pages from PDF
        
        Args:
            input_file: Path to input PDF
            output_folder: Output directory
            pages_to_delete: List of page numbers to delete (1-indexed)
        """
        output_filename = f"{uuid.uuid4()}_deleted.pdf"
        output_path = os.path.join(output_folder, output_filename)
        
        reader = PdfReader(input_file)
        writer = PdfWriter()
        
        total_pages = len(reader.pages)
        
        # Convert to 0-indexed set for fast lookup
        pages_to_delete_set = set(p - 1 for p in pages_to_delete if 0 < p <= total_pages)
        
        for i, page in enumerate(reader.pages):
            if i not in pages_to_delete_set:
                writer.add_page(page)
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        return output_path
    
    def extract_pages(self, input_file, output_folder, pages_to_extract):
        """Extract specific pages to new PDF
        
        Args:
            input_file: Path to input PDF
            output_folder: Output directory
            pages_to_extract: List of page numbers or ranges (1-indexed)
                             e.g., [1, 3, 5] or "1-3,5,7-10"
        """
        output_filename = f"{uuid.uuid4()}_extracted.pdf"
        output_path = os.path.join(output_folder, output_filename)
        
        reader = PdfReader(input_file)
        writer = PdfWriter()
        
        # Parse page ranges
        if isinstance(pages_to_extract, str):
            pages_to_extract = self._parse_page_ranges(pages_to_extract, len(reader.pages))
        
        for page_num in pages_to_extract:
            if 0 < page_num <= len(reader.pages):
                writer.add_page(reader.pages[page_num - 1])
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        return output_path
    
    def reorder_pages(self, input_file, output_folder, new_order):
        """Reorder PDF pages
        
        Args:
            input_file: Path to input PDF
            output_folder: Output directory
            new_order: List of page numbers in desired order (1-indexed)
        """
        output_filename = f"{uuid.uuid4()}_reordered.pdf"
        output_path = os.path.join(output_folder, output_filename)
        
        reader = PdfReader(input_file)
        writer = PdfWriter()
        
        for page_num in new_order:
            if 0 < page_num <= len(reader.pages):
                writer.add_page(reader.pages[page_num - 1])
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        return output_path
    
    def crop_pages(self, input_file, output_folder, crop_box, pages="all"):
        """Crop PDF pages
        
        Args:
            input_file: Path to input PDF
            output_folder: Output directory
            crop_box: Dict with keys: left, top, right, bottom (in points)
            pages: "all" or list of page numbers (1-indexed)
        """
        output_filename = f"{uuid.uuid4()}_cropped.pdf"
        output_path = os.path.join(output_folder, output_filename)
        
        reader = PdfReader(input_file)
        writer = PdfWriter()
        
        total_pages = len(reader.pages)
        
        # Determine which pages to crop
        if pages == "all":
            pages_to_crop = list(range(total_pages))
        else:
            pages_to_crop = [p - 1 for p in pages if 0 < p <= total_pages]
        
        for i, page in enumerate(reader.pages):
            if i in pages_to_crop:
                page.mediabox.lower_left = (crop_box['left'], crop_box['bottom'])
                page.mediabox.upper_right = (crop_box['right'], crop_box['top'])
            writer.add_page(page)
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        return output_path
    
    def add_blank_pages(self, input_file, output_folder, positions):
        """Add blank pages at specified positions
        
        Args:
            input_file: Path to input PDF
            output_folder: Output directory
            positions: List of positions where to insert blank pages (1-indexed)
        """
        output_filename = f"{uuid.uuid4()}_with_blanks.pdf"
        output_path = os.path.join(output_folder, output_filename)
        
        reader = PdfReader(input_file)
        writer = PdfWriter()
        
        # Get page size from first page
        first_page = reader.pages[0]
        width = first_page.mediabox.width
        height = first_page.mediabox.height
        
        positions_set = set(positions)
        current_position = 1
        
        for i, page in enumerate(reader.pages):
            # Add blank pages before this page if needed
            while current_position in positions_set:
                writer.add_blank_page(width=float(width), height=float(height))
                current_position += 1
            
            writer.add_page(page)
            current_position += 1
        
        # Add any remaining blank pages at the end
        while current_position in positions_set:
            writer.add_blank_page(width=float(width), height=float(height))
            current_position += 1
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        return output_path
    
    def grayscale_pdf(self, input_file, output_folder):
        """Convert PDF to grayscale"""
        output_filename = f"{uuid.uuid4()}_grayscale.pdf"
        output_path = os.path.join(output_folder, output_filename)
        
        doc = fitz.open(input_file)
        
        for page in doc:
            # Convert to grayscale
            pix = page.get_pixmap(colorspace=fitz.csGRAY)
            
            # Replace page with grayscale version
            page.clean_contents()
        
        doc.save(output_path)
        doc.close()
        
        return output_path
    
    def add_page_numbers(self, input_file, output_folder, position="bottom-right", 
                         start_number=1, format_string="{page}"):
        """Add page numbers to PDF
        
        Args:
            input_file: Path to input PDF
            output_folder: Output directory
            position: "bottom-left", "bottom-center", "bottom-right", 
                     "top-left", "top-center", "top-right"
            start_number: Starting page number
            format_string: Format for page number (e.g., "Page {page}", "{page} of {total}")
        """
        output_filename = f"{uuid.uuid4()}_numbered.pdf"
        output_path = os.path.join(output_folder, output_filename)
        
        doc = fitz.open(input_file)
        total_pages = len(doc)
        
        for page_num, page in enumerate(doc, start=start_number):
            # Format page number text
            page_text = format_string.format(page=page_num, total=total_pages)
            
            # Get page dimensions
            rect = page.rect
            width = rect.width
            height = rect.height
            
            # Determine position
            if "bottom" in position:
                y = height - 30
            else:  # top
                y = 30
            
            if "left" in position:
                x = 30
            elif "right" in position:
                x = width - 80
            else:  # center
                x = width / 2 - 20
            
            # Add text
            page.insert_text((x, y), page_text, fontsize=10, color=(0, 0, 0))
        
        doc.save(output_path)
        doc.close()
        
        return output_path
    
    def _parse_page_ranges(self, ranges_str, total_pages):
        """Parse page range string like '1-3,5,7-10' into list of page numbers"""
        pages = []
        
        for part in ranges_str.split(','):
            part = part.strip()
            if '-' in part:
                start, end = part.split('-')
                start = int(start.strip())
                end = int(end.strip())
                pages.extend(range(start, min(end + 1, total_pages + 1)))
            else:
                page = int(part)
                if 0 < page <= total_pages:
                    pages.append(page)
        
        return sorted(set(pages))
    
    def resize_pdf(self, input_file, output_folder, page_size="A4"):
        """Resize PDF to standard page size
        
        Args:
            input_file: Path to input PDF
            output_folder: Output directory
            page_size: "A4", "Letter", "Legal", "A3", "A5"
        """
        output_filename = f"{uuid.uuid4()}_resized.pdf"
        output_path = os.path.join(output_folder, output_filename)
        
        # Page sizes in points (1 inch = 72 points)
        sizes = {
            "A4": (595, 842),
            "Letter": (612, 792),
            "Legal": (612, 1008),
            "A3": (842, 1191),
            "A5": (420, 595)
        }
        
        target_width, target_height = sizes.get(page_size, sizes["A4"])
        
        doc = fitz.open(input_file)
        new_doc = fitz.open()
        
        for page in doc:
            # Create new page with target size
            new_page = new_doc.new_page(width=target_width, height=target_height)
            
            # Get original page as image
            pix = page.get_pixmap()
            
            # Calculate scaling to fit
            scale_x = target_width / page.rect.width
            scale_y = target_height / page.rect.height
            scale = min(scale_x, scale_y)
            
            # Insert scaled page
            new_page.show_pdf_page(
                new_page.rect,
                doc,
                page.number,
                clip=page.rect
            )
        
        new_doc.save(output_path)
        new_doc.close()
        doc.close()
        
        return output_path