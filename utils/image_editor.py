import os
import uuid
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import cv2
import numpy as np

class ImageEditor:
    """Edit images - resize, crop, rotate, filters, effects, etc."""
    
    def edit_image(self, input_file, output_folder, operations):
        """Apply multiple operations to an image
        
        Args:
            input_file: Path to input image
            output_folder: Output directory
            operations: Dict of operations to perform
        """
        img = Image.open(input_file)
        
        # Apply operations in order
        if 'resize' in operations:
            img = self._apply_resize(img, operations['resize'])
        
        if 'crop' in operations:
            img = self._apply_crop(img, operations['crop'])
        
        if 'rotate' in operations:
            img = self._apply_rotate(img, operations['rotate'])
        
        if 'flip' in operations:
            img = self._apply_flip(img, operations['flip'])
        
        if 'brightness' in operations:
            img = self._apply_brightness(img, operations['brightness'])
        
        if 'contrast' in operations:
            img = self._apply_contrast(img, operations['contrast'])
        
        if 'saturation' in operations:
            img = self._apply_saturation(img, operations['saturation'])
        
        if 'sharpness' in operations:
            img = self._apply_sharpness(img, operations['sharpness'])
        
        if 'blur' in operations:
            img = self._apply_blur(img, operations['blur'])
        
        if 'grayscale' in operations:
            img = img.convert('L')
        
        if 'sepia' in operations:
            img = self._apply_sepia(img)
        
        if 'filter' in operations:
            img = self._apply_filter(img, operations['filter'])
        
        if 'border' in operations:
            img = self._apply_border(img, operations['border'])
        
        if 'text' in operations:
            img = self._apply_text(img, operations['text'])
        
        # Save result
        ext = os.path.splitext(input_file)[1]
        output_filename = f"{uuid.uuid4()}_edited{ext}"
        output_path = os.path.join(output_folder, output_filename)
        
        # Handle transparency for JPEG
        if ext.lower() in ['.jpg', '.jpeg'] and img.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background
        
        img.save(output_path, quality=95)
        return output_path
    
    def resize_image(self, input_file, output_folder, width=None, height=None, maintain_aspect=True):
        """Resize image"""
        output_filename = f"{uuid.uuid4()}_resized{os.path.splitext(input_file)[1]}"
        output_path = os.path.join(output_folder, output_filename)
        
        img = Image.open(input_file)
        original_width, original_height = img.size
        
        if maintain_aspect:
            if width and not height:
                height = int(original_height * (width / original_width))
            elif height and not width:
                width = int(original_width * (height / original_height))
            elif width and height:
                # Maintain aspect ratio, fit within bounds
                ratio = min(width / original_width, height / original_height)
                width = int(original_width * ratio)
                height = int(original_height * ratio)
        
        img = img.resize((width, height), Image.Resampling.LANCZOS)
        img.save(output_path, quality=95)
        return output_path
    
    def crop_image(self, input_file, output_folder, x, y, width, height):
        """Crop image"""
        output_filename = f"{uuid.uuid4()}_cropped{os.path.splitext(input_file)[1]}"
        output_path = os.path.join(output_folder, output_filename)
        
        img = Image.open(input_file)
        img = img.crop((x, y, x + width, y + height))
        img.save(output_path, quality=95)
        return output_path
    
    def rotate_image(self, input_file, output_folder, angle, expand=True):
        """Rotate image"""
        output_filename = f"{uuid.uuid4()}_rotated{os.path.splitext(input_file)[1]}"
        output_path = os.path.join(output_folder, output_filename)
        
        img = Image.open(input_file)
        img = img.rotate(angle, expand=expand, fillcolor='white')
        img.save(output_path, quality=95)
        return output_path
    
    def flip_image(self, input_file, output_folder, direction='horizontal'):
        """Flip image"""
        output_filename = f"{uuid.uuid4()}_flipped{os.path.splitext(input_file)[1]}"
        output_path = os.path.join(output_folder, output_filename)
        
        img = Image.open(input_file)
        
        if direction == 'horizontal':
            img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        elif direction == 'vertical':
            img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        
        img.save(output_path, quality=95)
        return output_path
    
    # =================== PRIVATE HELPER METHODS ===================
    
    def _apply_resize(self, img, params):
        width = params.get('width')
        height = params.get('height')
        maintain_aspect = params.get('maintain_aspect', True)
        
        original_width, original_height = img.size
        
        if maintain_aspect:
            if width and not height:
                height = int(original_height * (width / original_width))
            elif height and not width:
                width = int(original_width * (height / original_height))
        
        return img.resize((width, height), Image.Resampling.LANCZOS)
    
    def _apply_crop(self, img, params):
        x = params.get('x', 0)
        y = params.get('y', 0)
        width = params.get('width')
        height = params.get('height')
        return img.crop((x, y, x + width, y + height))
    
    def _apply_rotate(self, img, params):
        angle = params.get('angle', 0)
        expand = params.get('expand', True)
        return img.rotate(angle, expand=expand, fillcolor='white')
    
    def _apply_flip(self, img, params):
        direction = params.get('direction', 'horizontal')
        if direction == 'horizontal':
            return img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        elif direction == 'vertical':
            return img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        return img
    
    def _apply_brightness(self, img, params):
        factor = params.get('factor', 1.0)  # 1.0 = no change, <1 = darker, >1 = brighter
        enhancer = ImageEnhance.Brightness(img)
        return enhancer.enhance(factor)
    
    def _apply_contrast(self, img, params):
        factor = params.get('factor', 1.0)  # 1.0 = no change
        enhancer = ImageEnhance.Contrast(img)
        return enhancer.enhance(factor)
    
    def _apply_saturation(self, img, params):
        factor = params.get('factor', 1.0)  # 1.0 = no change, 0 = grayscale
        enhancer = ImageEnhance.Color(img)
        return enhancer.enhance(factor)
    
    def _apply_sharpness(self, img, params):
        factor = params.get('factor', 1.0)  # 1.0 = no change
        enhancer = ImageEnhance.Sharpness(img)
        return enhancer.enhance(factor)
    
    def _apply_blur(self, img, params):
        radius = params.get('radius', 2)
        return img.filter(ImageFilter.GaussianBlur(radius))
    
    def _apply_sepia(self, img):
        """Apply sepia tone effect"""
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        pixels = img.load()
        width, height = img.size
        
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                
                tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                
                pixels[x, y] = (
                    min(255, tr),
                    min(255, tg),
                    min(255, tb)
                )
        
        return img
    
    def _apply_filter(self, img, params):
        """Apply various filters"""
        filter_type = params.get('type', 'none')
        
        if filter_type == 'blur':
            return img.filter(ImageFilter.BLUR)
        elif filter_type == 'contour':
            return img.filter(ImageFilter.CONTOUR)
        elif filter_type == 'detail':
            return img.filter(ImageFilter.DETAIL)
        elif filter_type == 'edge_enhance':
            return img.filter(ImageFilter.EDGE_ENHANCE)
        elif filter_type == 'emboss':
            return img.filter(ImageFilter.EMBOSS)
        elif filter_type == 'sharpen':
            return img.filter(ImageFilter.SHARPEN)
        elif filter_type == 'smooth':
            return img.filter(ImageFilter.SMOOTH)
        
        return img
    
    def _apply_border(self, img, params):
        """Add border to image"""
        width = params.get('width', 10)
        color = params.get('color', 'black')
        
        # Create new image with border
        new_width = img.size[0] + 2 * width
        new_height = img.size[1] + 2 * width
        
        bordered = Image.new(img.mode, (new_width, new_height), color)
        bordered.paste(img, (width, width))
        
        return bordered
    
    def _apply_text(self, img, params):
        """Add text to image"""
        text = params.get('text', '')
        position = params.get('position', (10, 10))
        color = params.get('color', 'black')
        size = params.get('size', 20)
        
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", size)
        except:
            font = ImageFont.load_default()
        
        draw.text(position, text, fill=color, font=font)
        
        return img
    
    def apply_advanced_filters(self, input_file, output_folder, filter_type):
        """Apply advanced CV2 filters"""
        output_filename = f"{uuid.uuid4()}_filtered{os.path.splitext(input_file)[1]}"
        output_path = os.path.join(output_folder, output_filename)
        
        # Read image with OpenCV
        img = cv2.imread(input_file)
        
        if filter_type == 'cartoon':
            img = self._cartoonify(img)
        elif filter_type == 'pencil_sketch':
            img = self._pencil_sketch(img)
        elif filter_type == 'edge_detection':
            img = self._edge_detection(img)
        elif filter_type == 'oil_painting':
            img = self._oil_painting(img)
        
        cv2.imwrite(output_path, img)
        return output_path
    
    def _cartoonify(self, img):
        """Create cartoon effect"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                      cv2.THRESH_BINARY, 9, 9)
        
        color = cv2.bilateralFilter(img, 9, 300, 300)
        cartoon = cv2.bitwise_and(color, color, mask=edges)
        
        return cartoon
    
    def _pencil_sketch(self, img):
        """Create pencil sketch effect"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        inv_gray = 255 - gray
        blur = cv2.GaussianBlur(inv_gray, (21, 21), 0)
        sketch = cv2.divide(gray, 255 - blur, scale=256)
        
        return cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
    
    def _edge_detection(self, img):
        """Detect edges using Canny"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    
    def _oil_painting(self, img):
        """Create oil painting effect"""
        return cv2.xphoto.oilPainting(img, 7, 1)