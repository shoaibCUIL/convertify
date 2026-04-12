"""
Image Engine
Handles all image-related operations: convert, resize, compress, etc.
"""

import os
import uuid

# Pillow (SAFE — always works)
from PIL import Image

# Optional: img2pdf (may not work on Render)
try:
    import img2pdf
    IMG2PDF_AVAILABLE = True
except:
    IMG2PDF_AVAILABLE = False

# Optional: Wand (NOT supported on Render)
try:
    from wand.image import Image as WandImage
    WAND_AVAILABLE = True
except:
    WAND_AVAILABLE = False

class ImageEngine:
    """Engine for image operations"""
    
    def convert_format(self, input_path, target_format, quality, output_folder):
        """
        Convert image to different format
        
        Args:
            input_path: Image file path
            target_format: Target format (png, jpg, webp, etc.)
            quality: Image quality (1-100)
            output_folder: Output directory
            
        Returns:
            dict: Result with output path
        """
        try:
            with Image.open(input_path) as img:
                # Convert RGBA to RGB if saving as JPEG
                if target_format.lower() in ['jpg', 'jpeg'] and img.mode == 'RGBA':
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[3])
                    img = rgb_img
                
                output_filename = f"converted_{uuid.uuid4()}.{target_format}"
                output_path = os.path.join(output_folder, output_filename)
                
                # Save with appropriate quality
                if target_format.lower() in ['jpg', 'jpeg', 'webp']:
                    img.save(output_path, quality=quality, optimize=True)
                else:
                    img.save(output_path, optimize=True)
                
                return {
                    'success': True,
                    'output_path': output_path
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def resize(self, input_path, width, height, maintain_aspect, output_folder):
        """
        Resize image
        
        Args:
            input_path: Image file path
            width: Target width (None to auto-calculate)
            height: Target height (None to auto-calculate)
            maintain_aspect: Whether to maintain aspect ratio
            output_folder: Output directory
            
        Returns:
            dict: Result with output path
        """
        try:
            with Image.open(input_path) as img:
                original_width, original_height = img.size
                
                # Calculate dimensions
                if maintain_aspect:
                    if width and not height:
                        height = int(original_height * (width / original_width))
                    elif height and not width:
                        width = int(original_width * (height / original_height))
                    elif width and height:
                        # Fit within bounds while maintaining aspect
                        img.thumbnail((width, height), Image.Resampling.LANCZOS)
                        new_width, new_height = img.size
                    else:
                        return {
                            'success': False,
                            'error': 'Must specify at least width or height'
                        }
                else:
                    if not width or not height:
                        return {
                            'success': False,
                            'error': 'Must specify both width and height when not maintaining aspect'
                        }
                
                # Resize if not already done by thumbnail
                if not (maintain_aspect and width and height):
                    img = img.resize((width, height), Image.Resampling.LANCZOS)
                
                # Save resized image
                ext = os.path.splitext(input_path)[1]
                output_filename = f"resized_{uuid.uuid4()}{ext}"
                output_path = os.path.join(output_folder, output_filename)
                
                img.save(output_path, quality=95, optimize=True)
                
                return {
                    'success': True,
                    'output_path': output_path
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def compress(self, input_path, quality, output_folder):
        """
        Compress image
        
        Args:
            input_path: Image file path
            quality: Compression quality (1-100)
            output_folder: Output directory
            
        Returns:
            dict: Result with compression stats
        """
        try:
            with Image.open(input_path) as img:
                ext = os.path.splitext(input_path)[1]
                output_filename = f"compressed_{uuid.uuid4()}{ext}"
                output_path = os.path.join(output_folder, output_filename)
                
                # Convert RGBA to RGB if needed
                if img.mode == 'RGBA' and ext.lower() in ['.jpg', '.jpeg']:
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[3])
                    img = rgb_img
                
                # Save with compression
                if ext.lower() in ['.jpg', '.jpeg', '.webp']:
                    img.save(output_path, quality=quality, optimize=True)
                else:
                    img.save(output_path, optimize=True)
                
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
    
    def images_to_pdf(self, input_paths, output_folder):
        """
        Convert multiple images to PDF (Render-safe)
        """
        try:
            output_filename = f"images_to_pdf_{uuid.uuid4()}.pdf"
            output_path = os.path.join(output_folder, output_filename)

            # ✅ If img2pdf available (local / VPS)
            if IMG2PDF_AVAILABLE:
                image_list = []

                for img_path in input_paths:
                    with Image.open(img_path) as img:
                        if img.mode != "RGB":
                            img = img.convert("RGB")

                        temp_path = os.path.join(output_folder, f"temp_{uuid.uuid4()}.jpg")
                        img.save(temp_path, "JPEG")
                        image_list.append(temp_path)

                with open(output_path, "wb") as f:
                    f.write(img2pdf.convert(image_list))

                # cleanup temp files
                for path in image_list:
                    if "temp_" in path:
                        try:
                            os.remove(path)
                        except:
                            pass

            # ✅ Fallback (Render-safe using Pillow)
            else:
                images = []

                for img_path in input_paths:
                    img = Image.open(img_path)
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    images.append(img)

                if not images:
                    return {"success": False, "error": "No valid images"}

                images[0].save(
                    output_path,
                    save_all=True,
                    append_images=images[1:]
                )

            return {
                "success": True,
                "output_path": output_path
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def crop(self, input_path, left, top, right, bottom, output_folder):
        """
        Crop image
        
        Args:
            input_path: Image file path
            left, top, right, bottom: Crop coordinates
            output_folder: Output directory
            
        Returns:
            dict: Result with output path
        """
        try:
            with Image.open(input_path) as img:
                cropped = img.crop((left, top, right, bottom))
                
                ext = os.path.splitext(input_path)[1]
                output_filename = f"cropped_{uuid.uuid4()}{ext}"
                output_path = os.path.join(output_folder, output_filename)
                
                cropped.save(output_path, quality=95, optimize=True)
                
                return {
                    'success': True,
                    'output_path': output_path
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def rotate(self, input_path, angle, output_folder):
        """
        Rotate image
        
        Args:
            input_path: Image file path
            angle: Rotation angle in degrees
            output_folder: Output directory
            
        Returns:
            dict: Result with output path
        """
        try:
            with Image.open(input_path) as img:
                rotated = img.rotate(angle, expand=True)
                
                ext = os.path.splitext(input_path)[1]
                output_filename = f"rotated_{uuid.uuid4()}{ext}"
                output_path = os.path.join(output_folder, output_filename)
                
                rotated.save(output_path, quality=95, optimize=True)
                
                return {
                    'success': True,
                    'output_path': output_path
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def flip(self, input_path, direction, output_folder):
        """
        Flip image
        
        Args:
            input_path: Image file path
            direction: 'horizontal' or 'vertical'
            output_folder: Output directory
            
        Returns:
            dict: Result with output path
        """
        try:
            with Image.open(input_path) as img:
                if direction == 'horizontal':
                    flipped = img.transpose(Image.FLIP_LEFT_RIGHT)
                elif direction == 'vertical':
                    flipped = img.transpose(Image.FLIP_TOP_BOTTOM)
                else:
                    return {
                        'success': False,
                        'error': 'Invalid flip direction'
                    }
                
                ext = os.path.splitext(input_path)[1]
                output_filename = f"flipped_{uuid.uuid4()}{ext}"
                output_path = os.path.join(output_folder, output_filename)
                
                flipped.save(output_path, quality=95, optimize=True)
                
                return {
                    'success': True,
                    'output_path': output_path
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def convert_to_grayscale(self, input_path, output_folder):
        """
        Convert image to grayscale
        
        Args:
            input_path: Image file path
            output_folder: Output directory
            
        Returns:
            dict: Result with output path
        """
        try:
            with Image.open(input_path) as img:
                grayscale = img.convert('L')
                
                ext = os.path.splitext(input_path)[1]
                output_filename = f"grayscale_{uuid.uuid4()}{ext}"
                output_path = os.path.join(output_folder, output_filename)
                
                grayscale.save(output_path, quality=95, optimize=True)
                
                return {
                    'success': True,
                    'output_path': output_path
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }