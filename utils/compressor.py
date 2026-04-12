import os
import uuid
from PIL import Image
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
import fitz  # PyMuPDF

class FileCompressor:
    """Compress files to reduce size"""
    
    def compress_pdf(self, input_file, output_folder, quality="medium"):
        """Compress PDF file
        
        Args:
            input_file: Path to input PDF
            output_folder: Output directory
            quality: "low", "medium", "high" (affects compression level)
        """
        output_filename = f"{uuid.uuid4()}_compressed.pdf"
        output_path = os.path.join(output_folder, output_filename)
        
        # Quality settings
        dpi_settings = {
            "low": 72,
            "medium": 150,
            "high": 200
        }
        
        dpi = dpi_settings.get(quality, 150)
        
        try:
            # Use PyMuPDF for better compression
            doc = fitz.open(input_file)
            
            for page in doc:
                # Get images on page
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    
                    # Extract image
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    
                    # Load with PIL and compress
                    from io import BytesIO
                    pil_image = Image.open(BytesIO(image_bytes))
                    
                    # Resize if too large
                    max_dimension = dpi * 11  # Roughly letter size
                    if max(pil_image.size) > max_dimension:
                        ratio = max_dimension / max(pil_image.size)
                        new_size = tuple(int(dim * ratio) for dim in pil_image.size)
                        pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)
                    
                    # Compress and replace
                    output_buffer = BytesIO()
                    
                    if pil_image.mode == 'RGBA':
                        pil_image = pil_image.convert('RGB')
                    
                    quality_val = {"low": 50, "medium": 75, "high": 85}.get(quality, 75)
                    pil_image.save(output_buffer, format='JPEG', quality=quality_val, optimize=True)
                    
                    # Replace image in PDF
                    page.replace_image(xref, stream=output_buffer.getvalue())
            
            # Save with compression
            doc.save(output_path, garbage=4, deflate=True, clean=True)
            doc.close()
        
        except Exception as e:
            # Fallback to basic PyPDF2 compression
            reader = PdfReader(input_file)
            writer = PdfWriter()
            
            for page in reader.pages:
                page.compress_content_streams()
                writer.add_page(page)
            
            with open(output_path, 'wb') as f:
                writer.write(f)
        
        return output_path
    
    def compress_image(self, input_file, output_folder, quality=85, resize_percent=None):
        """Compress image file
        
        Args:
            input_file: Path to input image
            output_folder: Output directory
            quality: JPEG quality (1-100)
            resize_percent: Optional percentage to resize (e.g., 50 for half size)
        """
        output_filename = f"{uuid.uuid4()}_compressed{os.path.splitext(input_file)[1]}"
        output_path = os.path.join(output_folder, output_filename)
        
        img = Image.open(input_file)
        
        # Resize if requested
        if resize_percent and resize_percent < 100:
            ratio = resize_percent / 100
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Convert RGBA to RGB for JPEG
        if img.mode in ('RGBA', 'LA', 'P'):
            if output_path.lower().endswith(('.jpg', '.jpeg')):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if img.mode in ('RGBA', 'LA'):
                    background.paste(img, mask=img.split()[-1])
                    img = background
        
        # Save with compression
        save_kwargs = {'optimize': True}
        
        if output_path.lower().endswith(('.jpg', '.jpeg')):
            save_kwargs['quality'] = quality
            save_kwargs['progressive'] = True
        elif output_path.lower().endswith('.png'):
            save_kwargs['compress_level'] = 9
        elif output_path.lower().endswith('.webp'):
            save_kwargs['quality'] = quality
            save_kwargs['method'] = 6
        
        img.save(output_path, **save_kwargs)
        return output_path
    
    def compress_images_batch(self, input_files, output_folder, quality=85):
        """Compress multiple images"""
        output_files = []
        
        for input_file in input_files:
            output_file = self.compress_image(input_file, output_folder, quality)
            output_files.append(output_file)
        
        return output_files
    
    def optimize_pdf_size(self, input_file, output_folder, target_size_mb=None):
        """Optimize PDF to target file size
        
        Args:
            input_file: Path to input PDF
            output_folder: Output directory
            target_size_mb: Target size in MB (will try to get close)
        """
        original_size = os.path.getsize(input_file) / (1024 * 1024)
        
        if target_size_mb and original_size <= target_size_mb:
            # Already small enough
            output_filename = f"{uuid.uuid4()}_optimized.pdf"
            output_path = os.path.join(output_folder, output_filename)
            
            import shutil
            shutil.copy(input_file, output_path)
            return output_path
        
        # Try progressively lower quality
        qualities = ["high", "medium", "low"]
        
        for quality in qualities:
            output_path = self.compress_pdf(input_file, output_folder, quality)
            
            if not target_size_mb:
                return output_path
            
            compressed_size = os.path.getsize(output_path) / (1024 * 1024)
            
            if compressed_size <= target_size_mb:
                return output_path
            
            # Clean up and try next quality
            os.remove(output_path)
        
        # If still too large, return the last attempt
        return self.compress_pdf(input_file, output_folder, "low")