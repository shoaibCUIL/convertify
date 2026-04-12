import os
import uuid
from PIL import Image
import pytesseract
import fitz  # PyMuPDF

class OCRProcessor:
    """Optical Character Recognition processor"""
    
    def __init__(self):
        # Try to set Tesseract path (Windows compatibility)
        try:
            # Common Windows installation path
            if os.name == 'nt':
                pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        except:
            pass
    
    def extract_text(self, input_file, language='eng'):
        """Extract text from image or PDF using OCR
        
        Args:
            input_file: Path to image or PDF file
            language: Language code (eng, spa, fra, deu, etc.)
        """
        file_ext = os.path.splitext(input_file)[1].lower()
        
        if file_ext == '.pdf':
            return self._extract_from_pdf(input_file, language)
        else:
            return self._extract_from_image(input_file, language)
    
    def _extract_from_image(self, image_file, language='eng'):
        """Extract text from image file"""
        try:
            img = Image.open(image_file)
            
            # Preprocess image for better OCR
            img = self._preprocess_image(img)
            
            # Extract text
            text = pytesseract.image_to_string(img, lang=language)
            
            return text.strip()
        
        except Exception as e:
            return f"OCR Error: {str(e)}"
    
    def _extract_from_pdf(self, pdf_file, language='eng'):
        """Extract text from scanned PDF"""
        text = ""
        
        try:
            doc = fitz.open(pdf_file)
            
            for page_num, page in enumerate(doc):
                # Convert page to image
                zoom = 2  # Increase resolution for better OCR
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                
                # Convert to PIL Image
                img_data = pix.tobytes("png")
                from io import BytesIO
                img = Image.open(BytesIO(img_data))
                
                # Preprocess
                img = self._preprocess_image(img)
                
                # OCR
                page_text = pytesseract.image_to_string(img, lang=language)
                text += f"\n\n--- Page {page_num + 1} ---\n\n{page_text}"
            
            doc.close()
        
        except Exception as e:
            text = f"OCR Error: {str(e)}"
        
        return text.strip()
    
    def _preprocess_image(self, img):
        """Preprocess image for better OCR accuracy"""
        # Convert to grayscale
        if img.mode != 'L':
            img = img.convert('L')
        
        # Optional: Add more preprocessing steps
        # - Thresholding
        # - Noise removal
        # - Deskewing
        
        return img
    
    def extract_with_confidence(self, input_file, language='eng'):
        """Extract text with confidence scores"""
        try:
            img = Image.open(input_file)
            img = self._preprocess_image(img)
            
            # Get detailed data
            data = pytesseract.image_to_data(img, lang=language, output_type=pytesseract.Output.DICT)
            
            result = {
                'text': '',
                'words': [],
                'avg_confidence': 0
            }
            
            total_conf = 0
            word_count = 0
            
            for i in range(len(data['text'])):
                if data['text'][i].strip():
                    word_info = {
                        'text': data['text'][i],
                        'confidence': float(data['conf'][i]),
                        'position': {
                            'x': data['left'][i],
                            'y': data['top'][i],
                            'width': data['width'][i],
                            'height': data['height'][i]
                        }
                    }
                    
                    result['words'].append(word_info)
                    result['text'] += data['text'][i] + ' '
                    
                    total_conf += float(data['conf'][i])
                    word_count += 1
            
            if word_count > 0:
                result['avg_confidence'] = total_conf / word_count
            
            result['text'] = result['text'].strip()
            
            return result
        
        except Exception as e:
            return {'error': str(e)}
    
    def create_searchable_pdf(self, input_file, output_folder, language='eng'):
        """Convert scanned PDF to searchable PDF with OCR text layer"""
        output_filename = f"{uuid.uuid4()}_searchable.pdf"
        output_path = os.path.join(output_folder, output_filename)
        
        try:
            # This is a simplified version
            # Full implementation would overlay OCR text on original PDF
            
            doc = fitz.open(input_file)
            new_doc = fitz.open()
            
            for page_num, page in enumerate(doc):
                # Get page as image
                zoom = 2
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                
                # OCR
                img_data = pix.tobytes("png")
                from io import BytesIO
                img = Image.open(BytesIO(img_data))
                img = self._preprocess_image(img)
                text = pytesseract.image_to_string(img, lang=language)
                
                # Create new page
                new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
                
                # Insert original page as image
                new_page.insert_image(new_page.rect, stream=pix.tobytes("png"))
                
                # Add invisible text layer (simplified - real implementation more complex)
                # new_page.insert_text((0, 0), text, fontsize=1, color=(1, 1, 1))
            
            new_doc.save(output_path)
            new_doc.close()
            doc.close()
        
        except Exception as e:
            print(f"Error creating searchable PDF: {str(e)}")
            return None
        
        return output_path
    
    def detect_language(self, input_file):
        """Detect language of text in image"""
        try:
            img = Image.open(input_file)
            img = self._preprocess_image(img)
            
            # Get OSD (Orientation and Script Detection)
            osd = pytesseract.image_to_osd(img)
            
            # Parse OSD output
            lang_info = {}
            for line in osd.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    lang_info[key.strip()] = value.strip()
            
            return lang_info
        
        except Exception as e:
            return {'error': str(e)}
    
    def extract_structured_data(self, input_file, data_type='table'):
        """Extract structured data (tables, forms) from image
        
        Args:
            input_file: Path to image
            data_type: 'table', 'form', 'receipt', etc.
        """
        try:
            img = Image.open(input_file)
            img = self._preprocess_image(img)
            
            if data_type == 'table':
                # Use TSV output for table structure
                tsv_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.STRING)
                return {'type': 'table', 'data': tsv_data}
            
            else:
                # General text extraction
                text = pytesseract.image_to_string(img)
                return {'type': data_type, 'text': text}
        
        except Exception as e:
            return {'error': str(e)}