"""
Universal File Converter & Editor - Main Application
A production-ready Flask application for file conversion and editing
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import uuid
import logging
from datetime import datetime
import zipfile
from pathlib import Path

# Import custom modules
from utils.file_detector import detect_file_type, get_file_info
from utils.converter import UniversalConverter
from utils.security import validate_file, sanitize_path, check_file_size
from engines.pdf_engine import PDFEngine
from engines.image_engine import ImageEngine
from engines.video_engine import VideoEngine
from engines.document_engine import DocumentEngine
from engines.ocr_engine import OCREngine
from workers.tasks import process_conversion_task, cleanup_old_files

# Configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['TEMP_FOLDER'] = 'temp'
app.config['ALLOWED_EXTENSIONS'] = '*'  # Allow all extensions

CORS(app)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create necessary directories
for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'], app.config['TEMP_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

# Initialize engines
pdf_engine = PDFEngine()
image_engine = ImageEngine()
video_engine = VideoEngine()
document_engine = DocumentEngine()
ocr_engine = OCREngine()
universal_converter = UniversalConverter()


@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    try:
        logger.info("Upload endpoint called")
        
        if 'file' not in request.files:
            logger.error("No file in request")
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            logger.error("Empty filename")
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file
        if not validate_file(file):
            logger.error("File validation failed")
            return jsonify({'error': 'Invalid file type or content'}), 400
        
        # Check file size
        if not check_file_size(file):
            logger.error("File size check failed")
            return jsonify({'error': 'File size exceeds maximum allowed limit'}), 400
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        file_id = str(uuid.uuid4())
        file_ext = os.path.splitext(original_filename)[1]
        filename = f"{file_id}{file_ext}"
        
        # Save file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Detect file type
        file_type_info = detect_file_type(filepath)
        file_info = get_file_info(filepath)
        
        logger.info(f"File uploaded: {original_filename} -> {filename}")
        
        return jsonify({
            'success': True,
            'file_id': file_id,
            'filename': filename,
            'original_filename': original_filename,
            'file_type': file_type_info['type'],
            'mime_type': file_type_info['mime_type'],
            'size': file_info['size'],
            'size_formatted': file_info['size_formatted']
        })
    
    except Exception as e:
        logger.error(f"Upload error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500


@app.route('/api/convert', methods=['POST'])
def convert_file():
    """Universal file conversion endpoint"""
    try:
        data = request.get_json()
        
        if not data or 'filename' not in data or 'target_format' not in data:
            return jsonify({'error': 'Missing required parameters'}), 400
        
        filename = sanitize_path(data['filename'])
        target_format = data['target_format'].lower().replace('.', '')
        options = data.get('options', {})
        options['output_folder'] = app.config['OUTPUT_FOLDER']
        
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(input_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Perform conversion
        result = universal_converter.convert(input_path, target_format, options)
        
        if result['success']:
            output_filename = os.path.basename(result['output_path'])
            return jsonify({
                'success': True,
                'output_filename': output_filename,
                'message': 'Conversion successful'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Conversion failed')
            }), 400
    
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Conversion failed: {str(e)}'}), 500


@app.route('/api/pdf/merge', methods=['POST'])
def merge_pdfs():
    """Merge multiple PDF files"""
    try:
        data = request.get_json()
        filenames = [sanitize_path(f) for f in data.get('filenames', [])]
        
        if len(filenames) < 2:
            return jsonify({'error': 'At least 2 files required for merging'}), 400
        
        input_paths = [os.path.join(app.config['UPLOAD_FOLDER'], f) for f in filenames]
        
        # Validate all files exist
        for path in input_paths:
            if not os.path.exists(path):
                return jsonify({'error': f'File not found: {os.path.basename(path)}'}), 404
        
        result = pdf_engine.merge_pdfs(input_paths, app.config['OUTPUT_FOLDER'])
        
        if result['success']:
            return jsonify({
                'success': True,
                'output_filename': os.path.basename(result['output_path']),
                'message': 'PDFs merged successfully'
            })
        else:
            return jsonify({'error': result.get('error', 'Merge failed')}), 400
    
    except Exception as e:
        logger.error(f"PDF merge error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Merge failed: {str(e)}'}), 500


@app.route('/api/pdf/split', methods=['POST'])
def split_pdf():
    """Split PDF into multiple files"""
    try:
        data = request.get_json()
        filename = sanitize_path(data.get('filename'))
        split_ranges = data.get('ranges', [])
        
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(input_path):
            return jsonify({'error': 'File not found'}), 404
        
        result = pdf_engine.split_pdf(input_path, split_ranges, app.config['OUTPUT_FOLDER'])
        
        if result['success']:
            return jsonify({
                'success': True,
                'output_files': [os.path.basename(f) for f in result['output_paths']],
                'message': 'PDF split successfully'
            })
        else:
            return jsonify({'error': result.get('error', 'Split failed')}), 400
    
    except Exception as e:
        logger.error(f"PDF split error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Split failed: {str(e)}'}), 500


@app.route('/api/pdf/compress', methods=['POST'])
def compress_pdf():
    """Compress PDF file"""
    try:
        data = request.get_json()
        filename = sanitize_path(data.get('filename'))
        quality = data.get('quality', 'medium')
        
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(input_path):
            return jsonify({'error': 'File not found'}), 404
        
        result = pdf_engine.compress_pdf(input_path, quality, app.config['OUTPUT_FOLDER'])
        
        if result['success']:
            return jsonify({
                'success': True,
                'output_filename': os.path.basename(result['output_path']),
                'original_size': result['original_size'],
                'compressed_size': result['compressed_size'],
                'compression_ratio': result['compression_ratio'],
                'message': 'PDF compressed successfully'
            })
        else:
            return jsonify({'error': result.get('error', 'Compression failed')}), 400
    
    except Exception as e:
        logger.error(f"PDF compression error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Compression failed: {str(e)}'}), 500


@app.route('/api/pdf/to-images', methods=['POST'])
def pdf_to_images():
    """Convert PDF to images"""
    try:
        data = request.get_json()
        filename = sanitize_path(data.get('filename'))
        image_format = data.get('format', 'png')
        dpi = data.get('dpi', 200)
        
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(input_path):
            return jsonify({'error': 'File not found'}), 404
        
        result = pdf_engine.pdf_to_images(input_path, image_format, dpi, app.config['OUTPUT_FOLDER'])
        
        if result['success']:
            return jsonify({
                'success': True,
                'output_files': [os.path.basename(f) for f in result['output_paths']],
                'message': 'PDF converted to images successfully'
            })
        else:
            return jsonify({'error': result.get('error', 'Conversion failed')}), 400
    
    except Exception as e:
        logger.error(f"PDF to images error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Conversion failed: {str(e)}'}), 500


@app.route('/api/images/to-pdf', methods=['POST'])
def images_to_pdf():
    """Convert images to PDF"""
    try:
        data = request.get_json()
        filenames = [sanitize_path(f) for f in data.get('filenames', [])]
        
        if len(filenames) < 1:
            return jsonify({'error': 'At least 1 image required'}), 400
        
        input_paths = [os.path.join(app.config['UPLOAD_FOLDER'], f) for f in filenames]
        
        result = image_engine.images_to_pdf(input_paths, app.config['OUTPUT_FOLDER'])
        
        if result['success']:
            return jsonify({
                'success': True,
                'output_filename': os.path.basename(result['output_path']),
                'message': 'Images converted to PDF successfully'
            })
        else:
            return jsonify({'error': result.get('error', 'Conversion failed')}), 400
    
    except Exception as e:
        logger.error(f"Images to PDF error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Conversion failed: {str(e)}'}), 500


@app.route('/api/pdf/watermark', methods=['POST'])
def add_watermark():
    """Add watermark to PDF"""
    try:
        data = request.get_json()
        filename = sanitize_path(data.get('filename'))
        watermark_text = data.get('watermark_text', 'WATERMARK')
        opacity = data.get('opacity', 0.3)
        
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(input_path):
            return jsonify({'error': 'File not found'}), 404
        
        result = pdf_engine.add_watermark(input_path, watermark_text, opacity, app.config['OUTPUT_FOLDER'])
        
        if result['success']:
            return jsonify({
                'success': True,
                'output_filename': os.path.basename(result['output_path']),
                'message': 'Watermark added successfully'
            })
        else:
            return jsonify({'error': result.get('error', 'Watermark failed')}), 400
    
    except Exception as e:
        logger.error(f"Watermark error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Watermark failed: {str(e)}'}), 500


@app.route('/api/pdf/rotate', methods=['POST'])
def rotate_pdf():
    """Rotate PDF pages"""
    try:
        data = request.get_json()
        filename = sanitize_path(data.get('filename'))
        rotation = data.get('rotation', 90)
        pages = data.get('pages', 'all')
        
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(input_path):
            return jsonify({'error': 'File not found'}), 404
        
        result = pdf_engine.rotate_pages(input_path, rotation, pages, app.config['OUTPUT_FOLDER'])
        
        if result['success']:
            return jsonify({
                'success': True,
                'output_filename': os.path.basename(result['output_path']),
                'message': 'PDF rotated successfully'
            })
        else:
            return jsonify({'error': result.get('error', 'Rotation failed')}), 400
    
    except Exception as e:
        logger.error(f"Rotation error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Rotation failed: {str(e)}'}), 500


@app.route('/api/pdf/protect', methods=['POST'])
def protect_pdf():
    """Add password protection to PDF"""
    try:
        data = request.get_json()
        filename = sanitize_path(data.get('filename'))
        password = data.get('password')
        
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(input_path):
            return jsonify({'error': 'File not found'}), 404
        
        result = pdf_engine.protect_pdf(input_path, password, app.config['OUTPUT_FOLDER'])
        
        if result['success']:
            return jsonify({
                'success': True,
                'output_filename': os.path.basename(result['output_path']),
                'message': 'PDF protected successfully'
            })
        else:
            return jsonify({'error': result.get('error', 'Protection failed')}), 400
    
    except Exception as e:
        logger.error(f"PDF protection error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Protection failed: {str(e)}'}), 500


@app.route('/api/pdf/unlock', methods=['POST'])
def unlock_pdf():
    """Remove password protection from PDF"""
    try:
        data = request.get_json()
        filename = sanitize_path(data.get('filename'))
        password = data.get('password')
        
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(input_path):
            return jsonify({'error': 'File not found'}), 404
        
        result = pdf_engine.unlock_pdf(input_path, password, app.config['OUTPUT_FOLDER'])
        
        if result['success']:
            return jsonify({
                'success': True,
                'output_filename': os.path.basename(result['output_path']),
                'message': 'PDF unlocked successfully'
            })
        else:
            return jsonify({'error': result.get('error', 'Unlock failed')}), 400
    
    except Exception as e:
        logger.error(f"PDF unlock error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Unlock failed: {str(e)}'}), 500


@app.route('/api/pdf/add-page-numbers', methods=['POST'])
def add_page_numbers():
    """Add page numbers to PDF"""
    try:
        data = request.get_json()
        filename = sanitize_path(data.get('filename'))
        position = data.get('position', 'bottom-center')
        
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(input_path):
            return jsonify({'error': 'File not found'}), 404
        
        result = pdf_engine.add_page_numbers(input_path, position, app.config['OUTPUT_FOLDER'])
        
        if result['success']:
            return jsonify({
                'success': True,
                'output_filename': os.path.basename(result['output_path']),
                'message': 'Page numbers added successfully'
            })
        else:
            return jsonify({'error': result.get('error', 'Failed to add page numbers')}), 400
    
    except Exception as e:
        logger.error(f"Page numbers error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Failed to add page numbers: {str(e)}'}), 500


@app.route('/api/pdf/extract-text', methods=['POST'])
def extract_text():
    """Extract text from PDF"""
    try:
        data = request.get_json()
        filename = sanitize_path(data.get('filename'))
        
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(input_path):
            return jsonify({'error': 'File not found'}), 404
        
        result = pdf_engine.extract_text(input_path)
        
        if result['success']:
            # Save extracted text to file
            output_filename = f"extracted_text_{uuid.uuid4()}.txt"
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result['text'])
            
            return jsonify({
                'success': True,
                'text': result['text'],
                'output_filename': output_filename,
                'message': 'Text extracted successfully'
            })
        else:
            return jsonify({'error': result.get('error', 'Extraction failed')}), 400
    
    except Exception as e:
        logger.error(f"Text extraction error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Extraction failed: {str(e)}'}), 500


@app.route('/api/ocr', methods=['POST'])
def perform_ocr():
    """Perform OCR on image or PDF"""
    try:
        data = request.get_json()
        filename = sanitize_path(data.get('filename'))
        language = data.get('language', 'eng')
        output_format = data.get('output_format', 'text')
        
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(input_path):
            return jsonify({'error': 'File not found'}), 404
        
        result = ocr_engine.perform_ocr(input_path, language, output_format, app.config['OUTPUT_FOLDER'])
        
        if result['success']:
            response_data = {
                'success': True,
                'message': 'OCR completed successfully'
            }
            
            if output_format == 'text':
                response_data['text'] = result['text']
                response_data['output_filename'] = os.path.basename(result['output_path'])
            else:
                response_data['output_filename'] = os.path.basename(result['output_path'])
            
            return jsonify(response_data)
        else:
            return jsonify({'error': result.get('error', 'OCR failed')}), 400
    
    except Exception as e:
        logger.error(f"OCR error: {str(e)}", exc_info=True)
        return jsonify({'error': f'OCR failed: {str(e)}'}), 500


@app.route('/api/image/convert', methods=['POST'])
def convert_image():
    """Convert image format"""
    try:
        data = request.get_json()
        filename = sanitize_path(data.get('filename'))
        target_format = data.get('target_format', 'png')
        quality = data.get('quality', 85)
        
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(input_path):
            return jsonify({'error': 'File not found'}), 404
        
        result = image_engine.convert_format(input_path, target_format, quality, app.config['OUTPUT_FOLDER'])
        
        if result['success']:
            return jsonify({
                'success': True,
                'output_filename': os.path.basename(result['output_path']),
                'message': 'Image converted successfully'
            })
        else:
            return jsonify({'error': result.get('error', 'Conversion failed')}), 400
    
    except Exception as e:
        logger.error(f"Image conversion error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Conversion failed: {str(e)}'}), 500


@app.route('/api/image/resize', methods=['POST'])
def resize_image():
    """Resize image"""
    try:
        data = request.get_json()
        filename = sanitize_path(data.get('filename'))
        width = data.get('width')
        height = data.get('height')
        maintain_aspect = data.get('maintain_aspect', True)
        
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(input_path):
            return jsonify({'error': 'File not found'}), 404
        
        result = image_engine.resize(input_path, width, height, maintain_aspect, app.config['OUTPUT_FOLDER'])
        
        if result['success']:
            return jsonify({
                'success': True,
                'output_filename': os.path.basename(result['output_path']),
                'message': 'Image resized successfully'
            })
        else:
            return jsonify({'error': result.get('error', 'Resize failed')}), 400
    
    except Exception as e:
        logger.error(f"Image resize error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Resize failed: {str(e)}'}), 500


@app.route('/api/image/compress', methods=['POST'])
def compress_image():
    """Compress image"""
    try:
        data = request.get_json()
        filename = sanitize_path(data.get('filename'))
        quality = data.get('quality', 85)
        
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(input_path):
            return jsonify({'error': 'File not found'}), 404
        
        result = image_engine.compress(input_path, quality, app.config['OUTPUT_FOLDER'])
        
        if result['success']:
            return jsonify({
                'success': True,
                'output_filename': os.path.basename(result['output_path']),
                'original_size': result['original_size'],
                'compressed_size': result['compressed_size'],
                'compression_ratio': result['compression_ratio'],
                'message': 'Image compressed successfully'
            })
        else:
            return jsonify({'error': result.get('error', 'Compression failed')}), 400
    
    except Exception as e:
        logger.error(f"Image compression error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Compression failed: {str(e)}'}), 500


@app.route('/api/video/convert', methods=['POST'])
def convert_video():
    """Convert video format"""
    try:
        data = request.get_json()
        filename = sanitize_path(data.get('filename'))
        target_format = data.get('target_format', 'mp4')
        quality = data.get('quality', 'medium')
        
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(input_path):
            return jsonify({'error': 'File not found'}), 404
        
        result = video_engine.convert_format(input_path, target_format, quality, app.config['OUTPUT_FOLDER'])
        
        if result['success']:
            return jsonify({
                'success': True,
                'output_filename': os.path.basename(result['output_path']),
                'message': 'Video converted successfully'
            })
        else:
            return jsonify({'error': result.get('error', 'Conversion failed')}), 400
    
    except Exception as e:
        logger.error(f"Video conversion error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Conversion failed: {str(e)}'}), 500


@app.route('/api/video/extract-audio', methods=['POST'])
def extract_audio():
    """Extract audio from video"""
    try:
        data = request.get_json()
        filename = sanitize_path(data.get('filename'))
        audio_format = data.get('audio_format', 'mp3')
        
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(input_path):
            return jsonify({'error': 'File not found'}), 404
        
        result = video_engine.extract_audio(input_path, audio_format, app.config['OUTPUT_FOLDER'])
        
        if result['success']:
            return jsonify({
                'success': True,
                'output_filename': os.path.basename(result['output_path']),
                'message': 'Audio extracted successfully'
            })
        else:
            return jsonify({'error': result.get('error', 'Extraction failed')}), 400
    
    except Exception as e:
        logger.error(f"Audio extraction error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Extraction failed: {str(e)}'}), 500


@app.route('/api/document/convert', methods=['POST'])
def convert_document():
    """Convert document format"""
    try:
        data = request.get_json()
        filename = sanitize_path(data.get('filename'))
        target_format = data.get('target_format')
        
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(input_path):
            return jsonify({'error': 'File not found'}), 404
        
        result = document_engine.convert_format(input_path, target_format, app.config['OUTPUT_FOLDER'])
        
        if result['success']:
            return jsonify({
                'success': True,
                'output_filename': os.path.basename(result['output_path']),
                'message': 'Document converted successfully'
            })
        else:
            return jsonify({'error': result.get('error', 'Conversion failed')}), 400
    
    except Exception as e:
        logger.error(f"Document conversion error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Conversion failed: {str(e)}'}), 500


@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download converted file"""
    try:
        filename = secure_filename(filename)
        filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(filepath, as_attachment=True, download_name=filename)
    
    except Exception as e:
        logger.error(f"Download error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Download failed: {str(e)}'}), 500


@app.route('/api/download-multiple', methods=['POST'])
def download_multiple():
    """Download multiple files as ZIP"""
    try:
        data = request.get_json()
        filenames = [sanitize_path(f) for f in data.get('filenames', [])]
        
        if not filenames:
            return jsonify({'error': 'No files specified'}), 400
        
        # Create ZIP file
        zip_filename = f"converted_files_{uuid.uuid4()}.zip"
        zip_path = os.path.join(app.config['OUTPUT_FOLDER'], zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename in filenames:
                filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
                if os.path.exists(filepath):
                    zipf.write(filepath, filename)
        
        return send_file(zip_path, as_attachment=True, download_name=zip_filename)
    
    except Exception as e:
        logger.error(f"Multiple download error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Download failed: {str(e)}'}), 500


@app.route('/api/cleanup', methods=['POST'])
def cleanup_files():
    """Cleanup uploaded and output files"""
    try:
        data = request.get_json()
        file_type = data.get('type', 'all')
        
        if file_type in ['all', 'uploads']:
            for file in os.listdir(app.config['UPLOAD_FOLDER']):
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file)
                if os.path.isfile(filepath):
                    os.remove(filepath)
        
        if file_type in ['all', 'outputs']:
            for file in os.listdir(app.config['OUTPUT_FOLDER']):
                filepath = os.path.join(app.config['OUTPUT_FOLDER'], file)
                if os.path.isfile(filepath):
                    os.remove(filepath)
        
        return jsonify({
            'success': True,
            'message': 'Files cleaned up successfully'
        })
    
    except Exception as e:
        logger.error(f"Cleanup error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Cleanup failed: {str(e)}'}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}", exc_info=True)
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Run cleanup task periodically
    cleanup_old_files()
    
    # Start Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=os.environ.get('FLASK_ENV') == 'development'
    )