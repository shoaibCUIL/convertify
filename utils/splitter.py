import os
import uuid
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
from docx import Document
from PIL import Image

class FileSplitter:
    """Split files into multiple parts"""
    
    def split_pdf(self, input_file, output_folder, ranges=None, split_type="all"):
        """Split PDF into multiple files
        
        Args:
            input_file: Path to input PDF
            output_folder: Output directory
            ranges: Page ranges (e.g., "1-3,5,7-10") - used when split_type="range"
            split_type: "all" (one page per file), "range" (custom ranges),
                       "every_n" (split every N pages), "half" (split in half)
        """
        reader = PdfReader(input_file)
        total_pages = len(reader.pages)
        output_files = []
        
        if split_type == "all":
            # One page per file
            for page_num in range(total_pages):
                writer = PdfWriter()
                writer.add_page(reader.pages[page_num])
                
                output_filename = f"{uuid.uuid4()}_page_{page_num + 1}.pdf"
                output_path = os.path.join(output_folder, output_filename)
                
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                output_files.append(output_path)
        
        elif split_type == "range" and ranges:
            # Split by specified ranges
            page_groups = self._parse_ranges(ranges, total_pages)
            
            for group_idx, pages in enumerate(page_groups):
                writer = PdfWriter()
                
                for page_num in pages:
                    if 0 < page_num <= total_pages:
                        writer.add_page(reader.pages[page_num - 1])
                
                output_filename = f"{uuid.uuid4()}_part_{group_idx + 1}.pdf"
                output_path = os.path.join(output_folder, output_filename)
                
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                output_files.append(output_path)
        
        elif split_type == "half":
            # Split into two equal parts
            midpoint = total_pages // 2
            
            # First half
            writer1 = PdfWriter()
            for i in range(midpoint):
                writer1.add_page(reader.pages[i])
            
            output_filename1 = f"{uuid.uuid4()}_part_1.pdf"
            output_path1 = os.path.join(output_folder, output_filename1)
            with open(output_path1, 'wb') as f:
                writer1.write(f)
            output_files.append(output_path1)
            
            # Second half
            writer2 = PdfWriter()
            for i in range(midpoint, total_pages):
                writer2.add_page(reader.pages[i])
            
            output_filename2 = f"{uuid.uuid4()}_part_2.pdf"
            output_path2 = os.path.join(output_folder, output_filename2)
            with open(output_path2, 'wb') as f:
                writer2.write(f)
            output_files.append(output_path2)
        
        elif split_type.startswith("every_"):
            # Split every N pages
            try:
                n = int(split_type.split("_")[1])
            except:
                n = 1
            
            for start in range(0, total_pages, n):
                writer = PdfWriter()
                end = min(start + n, total_pages)
                
                for i in range(start, end):
                    writer.add_page(reader.pages[i])
                
                output_filename = f"{uuid.uuid4()}_pages_{start + 1}_{end}.pdf"
                output_path = os.path.join(output_folder, output_filename)
                
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                output_files.append(output_path)
        
        return output_files
    
    def split_pdf_by_size(self, input_file, output_folder, max_size_mb=5):
        """Split PDF into parts not exceeding specified size"""
        reader = PdfReader(input_file)
        total_pages = len(reader.pages)
        output_files = []
        
        current_writer = PdfWriter()
        current_size = 0
        part_num = 1
        
        for page_num in range(total_pages):
            # Add page to current writer
            current_writer.add_page(reader.pages[page_num])
            
            # Estimate size (rough approximation)
            current_size += len(reader.pages[page_num].compress_content_streams())
            
            # Check if we've exceeded size limit
            if current_size / (1024 * 1024) > max_size_mb:
                # Save current part
                output_filename = f"{uuid.uuid4()}_part_{part_num}.pdf"
                output_path = os.path.join(output_folder, output_filename)
                
                with open(output_path, 'wb') as output_file:
                    current_writer.write(output_file)
                
                output_files.append(output_path)
                
                # Start new part
                current_writer = PdfWriter()
                current_size = 0
                part_num += 1
        
        # Save last part if it has pages
        if len(current_writer.pages) > 0:
            output_filename = f"{uuid.uuid4()}_part_{part_num}.pdf"
            output_path = os.path.join(output_folder, output_filename)
            
            with open(output_path, 'wb') as output_file:
                current_writer.write(output_file)
            
            output_files.append(output_path)
        
        return output_files
    
    def split_pdf_by_bookmarks(self, input_file, output_folder):
        """Split PDF at bookmark/outline points"""
        reader = PdfReader(input_file)
        
        # This is a simplified version - full implementation would need
        # proper bookmark parsing
        output_files = []
        
        try:
            outlines = reader.outline
            if not outlines:
                # No bookmarks, fall back to splitting by page
                return self.split_pdf(input_file, output_folder, split_type="all")
            
            # Process bookmarks (simplified)
            # Full implementation would require recursive bookmark traversal
            # and page range extraction
            
        except:
            # If bookmark processing fails, split by pages
            return self.split_pdf(input_file, output_folder, split_type="all")
        
        return output_files
    
    def split_image(self, input_file, output_folder, rows=2, cols=2):
        """Split image into grid of smaller images"""
        img = Image.open(input_file)
        width, height = img.size
        
        piece_width = width // cols
        piece_height = height // rows
        
        output_files = []
        
        for row in range(rows):
            for col in range(cols):
                left = col * piece_width
                top = row * piece_height
                right = left + piece_width if col < cols - 1 else width
                bottom = top + piece_height if row < rows - 1 else height
                
                piece = img.crop((left, top, right, bottom))
                
                ext = os.path.splitext(input_file)[1]
                output_filename = f"{uuid.uuid4()}_piece_r{row}_c{col}{ext}"
                output_path = os.path.join(output_folder, output_filename)
                
                piece.save(output_path, quality=95)
                output_files.append(output_path)
        
        return output_files
    
    def _parse_ranges(self, ranges_str, total_pages):
        """Parse range string like '1-3,5,7-10' into list of page groups"""
        groups = []
        
        for part in ranges_str.split(','):
            part = part.strip()
            pages = []
            
            if '-' in part:
                start, end = part.split('-')
                start = int(start.strip())
                end = int(end.strip())
                pages = list(range(start, min(end + 1, total_pages + 1)))
            else:
                page = int(part)
                if 0 < page <= total_pages:
                    pages = [page]
            
            if pages:
                groups.append(pages)
        
        return groups