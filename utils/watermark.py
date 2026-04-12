import os
import uuid
from PIL import Image, ImageDraw, ImageFont
import fitz  # PyMuPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
import io

class WatermarkProcessor:
    """Add watermarks to documents and images"""
    
    def add_watermark(self, input_file, output_folder, text="CONFIDENTIAL", 
                     opacity=0.3, position="center", angle=45):
        """Add watermark to PDF
        
        Args:
            input_file: Path to input PDF
            output_folder: Output directory
            text: Watermark text
            opacity: Transparency (0-1)
            position: "center", "top-left", "top-right", "bottom-left", "bottom-right"
            angle: Rotation angle in degrees
        """
        output_filename = f"{uuid.uuid4()}_watermarked.pdf"
        output_path = os.path.join(output_folder, output_filename)
        
        try:
            doc = fitz.open(input_file)
            
            for page in doc:
                # Get page dimensions
                rect = page.rect
                width = rect.width
                height = rect.height
                
                # Determine position
                if position == "center":
                    x = width / 2
                    y = height / 2
                elif position == "top-left":
                    x = 100
                    y = 100
                elif position == "top-right":
                    x = width - 100
                    y = 100
                elif position == "bottom-left":
                    x = 100
                    y = height - 100
                elif position == "bottom-right":
                    x = width - 100
                    y = height - 100
                else:
                    x = width / 2
                    y = height / 2
                
                # Calculate text size
                fontsize = min(width, height) / 10
                
                # Add watermark text
                text_point = fitz.Point(x, y)
                
                # RGB color with opacity
                color = (0.5, 0.5, 0.5)  # Gray
                
                page.insert_text(
                    text_point,
                    text,
                    fontsize=fontsize,
                    rotate=angle,
                    color=color,
                    opacity=opacity,
                    overlay=False  # Background watermark
                )
            
            doc.save(output_path)
            doc.close()
        
        except Exception as e:
            print(f"Error adding watermark: {str(e)}")
            return None
        
        return output_path
    
    def add_image_watermark(self, input_file, output_folder, watermark_image, 
                           opacity=0.5, position="center", scale=0.3):
        """Add image watermark to PDF
        
        Args:
            input_file: Path to input PDF
            output_folder: Output directory
            watermark_image: Path to watermark image
            opacity: Transparency (0-1)
            position: "center", "top-left", "top-right", "bottom-left", "bottom-right"
            scale: Size relative to page (0-1)
        """
        output_filename = f"{uuid.uuid4()}_watermarked.pdf"
        output_path = os.path.join(output_folder, output_filename)
        
        try:
            doc = fitz.open(input_file)
            watermark_img = Image.open(watermark_image)
            
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
                    x = 20
                    y = 20
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
        
        except Exception as e:
            print(f"Error adding image watermark: {str(e)}")
            return None
        
        return output_path
    
    def add_watermark_to_image(self, input_file, output_folder, text="© Copyright",
                              opacity=128, position="bottom-right"):
        """Add watermark to image file
        
        Args:
            input_file: Path to input image
            output_folder: Output directory
            text: Watermark text
            opacity: Transparency (0-255)
            position: "center", "top-left", "top-right", "bottom-left", "bottom-right"
        """
        output_filename = f"{uuid.uuid4()}_watermarked{os.path.splitext(input_file)[1]}"
        output_path = os.path.join(output_folder, output_filename)
        
        # Open image
        img = Image.open(input_file)
        
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Create watermark layer
        watermark = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark)
        
        # Font
        try:
            fontsize = int(img.size[0] / 20)
            font = ImageFont.truetype("arial.ttf", fontsize)
        except:
            font = ImageFont.load_default()
        
        # Get text size
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Determine position
        if position == "center":
            x = (img.size[0] - text_width) / 2
            y = (img.size[1] - text_height) / 2
        elif position == "top-left":
            x = 10
            y = 10
        elif position == "top-right":
            x = img.size[0] - text_width - 10
            y = 10
        elif position == "bottom-left":
            x = 10
            y = img.size[1] - text_height - 10
        elif position == "bottom-right":
            x = img.size[0] - text_width - 10
            y = img.size[1] - text_height - 10
        else:
            x = (img.size[0] - text_width) / 2
            y = (img.size[1] - text_height) / 2
        
        # Draw text with opacity
        draw.text((x, y), text, font=font, fill=(255, 255, 255, opacity))
        
        # Composite
        watermarked = Image.alpha_composite(img, watermark)
        
        # Convert back to RGB if saving as JPEG
        if output_path.lower().endswith(('.jpg', '.jpeg')):
            watermarked = watermarked.convert('RGB')
        
        watermarked.save(output_path, quality=95)
        return output_path
    
    def batch_watermark(self, input_files, output_folder, text="CONFIDENTIAL", **kwargs):
        """Add watermark to multiple files"""
        output_files = []
        
        for input_file in input_files:
            ext = os.path.splitext(input_file)[1].lower()
            
            if ext == '.pdf':
                output_file = self.add_watermark(input_file, output_folder, text, **kwargs)
            elif ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                output_file = self.add_watermark_to_image(input_file, output_folder, text, **kwargs)
            else:
                continue
            
            if output_file:
                output_files.append(output_file)
        
        return output_files