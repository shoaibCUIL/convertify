import os
import uuid
import logging
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename

from utils.converter import UniversalConverter
from utils.file_detector import detect_file_type
from utils.pdf_editor import PDFEditor
from utils.image_editor import ImageEditor
from utils.merger import FileMerger
from utils.splitter import FileSplitter
from utils.compressor import FileCompressor
from utils.extractor import ContentExtractor
from utils.ocr_processor import OCRProcessor
from utils.watermark import WatermarkProcessor
from utils.protector import FileProtector
from utils.signer import DocumentSigner

# =================== CONFIG ===================
app = Flask(__name__)
CORS(app)

app.config["UPLOAD_FOLDER"] = "uploads"
app.config["OUTPUT_FOLDER"] = "outputs"
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100MB
app.config["ALLOWED_EXTENSIONS"] = {
    'pdf', 'docx', 'doc', 'xlsx', 'xls', 'pptx', 'ppt',
    'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp',
    'txt', 'csv', 'json', 'xml', 'html', 'md',
    'zip', 'rar', 'epub', 'mobi'
}

# Create folders
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize processors
converter = UniversalConverter()
pdf_editor = PDFEditor()
image_editor = ImageEditor()
merger = FileMerger()
splitter = FileSplitter()
compressor = FileCompressor()
extractor = ContentExtractor()
ocr_processor = OCRProcessor()
watermark_processor = WatermarkProcessor()
protector = FileProtector()
signer = DocumentSigner()

# =================== ROUTES ===================

@app.route("/")
def index():
    return render_template("index.html")

# =================== UPLOAD ===================
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

@app.route("/api/upload", methods=["POST"])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "Empty filename"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed"}), 400
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
        
        file.save(filepath)
        
        # Detect file type
        file_type = detect_file_type(filepath)
        
        return jsonify({
            "success": True,
            "filename": unique_filename,
            "original_name": filename,
            "file_type": file_type,
            "size": os.path.getsize(filepath)
        })
    
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# =================== CONVERT ===================
@app.route("/api/convert", methods=["POST"])
def convert_file():
    try:
        data = request.json
        input_file = os.path.join(app.config["UPLOAD_FOLDER"], data["filename"])
        target_format = data["target_format"]
        
        output_file = converter.convert(input_file, target_format, app.config["OUTPUT_FOLDER"])
        
        return jsonify({
            "success": True,
            "output_file": os.path.basename(output_file),
            "message": f"Converted to {target_format.upper()}"
        })
    
    except Exception as e:
        logger.error(f"Convert error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# =================== PDF OPERATIONS ===================
@app.route("/api/pdf/merge", methods=["POST"])
def merge_pdfs():
    try:
        data = request.json
        input_files = [os.path.join(app.config["UPLOAD_FOLDER"], f) for f in data["files"]]
        
        output_file = merger.merge_pdfs(input_files, app.config["OUTPUT_FOLDER"])
        
        return jsonify({
            "success": True,
            "output_file": os.path.basename(output_file)
        })
    
    except Exception as e:
        logger.error(f"Merge error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/pdf/split", methods=["POST"])
def split_pdf():
    try:
        data = request.json
        input_file = os.path.join(app.config["UPLOAD_FOLDER"], data["filename"])
        
        output_files = splitter.split_pdf(
            input_file,
            app.config["OUTPUT_FOLDER"],
            data.get("ranges"),  # e.g., "1-3,5,7-10"
            data.get("split_type", "all")  # "all", "range", "every_n"
        )
        
        return jsonify({
            "success": True,
            "output_files": [os.path.basename(f) for f in output_files]
        })
    
    except Exception as e:
        logger.error(f"Split error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/pdf/rotate", methods=["POST"])
def rotate_pdf():
    try:
        data = request.json
        input_file = os.path.join(app.config["UPLOAD_FOLDER"], data["filename"])
        
        output_file = pdf_editor.rotate_pages(
            input_file,
            app.config["OUTPUT_FOLDER"],
            data.get("angle", 90),
            data.get("pages", "all")
        )
        
        return jsonify({
            "success": True,
            "output_file": os.path.basename(output_file)
        })
    
    except Exception as e:
        logger.error(f"Rotate error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/pdf/compress", methods=["POST"])
def compress_pdf():
    try:
        data = request.json
        input_file = os.path.join(app.config["UPLOAD_FOLDER"], data["filename"])
        
        output_file = compressor.compress_pdf(
            input_file,
            app.config["OUTPUT_FOLDER"],
            data.get("quality", "medium")
        )
        
        original_size = os.path.getsize(input_file)
        compressed_size = os.path.getsize(output_file)
        reduction = ((original_size - compressed_size) / original_size) * 100
        
        return jsonify({
            "success": True,
            "output_file": os.path.basename(output_file),
            "original_size": original_size,
            "compressed_size": compressed_size,
            "reduction_percent": round(reduction, 2)
        })
    
    except Exception as e:
        logger.error(f"Compress error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/pdf/watermark", methods=["POST"])
def add_watermark():
    try:
        data = request.json
        input_file = os.path.join(app.config["UPLOAD_FOLDER"], data["filename"])
        
        output_file = watermark_processor.add_watermark(
            input_file,
            app.config["OUTPUT_FOLDER"],
            data.get("text", "CONFIDENTIAL"),
            data.get("opacity", 0.3),
            data.get("position", "center"),
            data.get("angle", 45)
        )
        
        return jsonify({
            "success": True,
            "output_file": os.path.basename(output_file)
        })
    
    except Exception as e:
        logger.error(f"Watermark error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/pdf/protect", methods=["POST"])
def protect_pdf():
    try:
        data = request.json
        input_file = os.path.join(app.config["UPLOAD_FOLDER"], data["filename"])
        
        output_file = protector.protect_pdf(
            input_file,
            app.config["OUTPUT_FOLDER"],
            data["password"],
            data.get("permissions", {})
        )
        
        return jsonify({
            "success": True,
            "output_file": os.path.basename(output_file)
        })
    
    except Exception as e:
        logger.error(f"Protect error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/pdf/unlock", methods=["POST"])
def unlock_pdf():
    try:
        data = request.json
        input_file = os.path.join(app.config["UPLOAD_FOLDER"], data["filename"])
        
        output_file = protector.unlock_pdf(
            input_file,
            app.config["OUTPUT_FOLDER"],
            data["password"]
        )
        
        return jsonify({
            "success": True,
            "output_file": os.path.basename(output_file)
        })
    
    except Exception as e:
        logger.error(f"Unlock error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/pdf/extract-images", methods=["POST"])
def extract_images():
    try:
        data = request.json
        input_file = os.path.join(app.config["UPLOAD_FOLDER"], data["filename"])
        
        output_files = extractor.extract_images_from_pdf(
            input_file,
            app.config["OUTPUT_FOLDER"]
        )
        
        return jsonify({
            "success": True,
            "output_files": [os.path.basename(f) for f in output_files],
            "count": len(output_files)
        })
    
    except Exception as e:
        logger.error(f"Extract images error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/pdf/extract-text", methods=["POST"])
def extract_text():
    try:
        data = request.json
        input_file = os.path.join(app.config["UPLOAD_FOLDER"], data["filename"])
        
        text = extractor.extract_text_from_pdf(input_file)
        
        return jsonify({
            "success": True,
            "text": text,
            "length": len(text)
        })
    
    except Exception as e:
        logger.error(f"Extract text error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# =================== IMAGE OPERATIONS ===================
@app.route("/api/image/edit", methods=["POST"])
def edit_image():
    try:
        data = request.json
        input_file = os.path.join(app.config["UPLOAD_FOLDER"], data["filename"])
        
        output_file = image_editor.edit_image(
            input_file,
            app.config["OUTPUT_FOLDER"],
            data.get("operations", {})
        )
        
        return jsonify({
            "success": True,
            "output_file": os.path.basename(output_file)
        })
    
    except Exception as e:
        logger.error(f"Image edit error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/image/compress", methods=["POST"])
def compress_image():
    try:
        data = request.json
        input_file = os.path.join(app.config["UPLOAD_FOLDER"], data["filename"])
        
        output_file = compressor.compress_image(
            input_file,
            app.config["OUTPUT_FOLDER"],
            data.get("quality", 85)
        )
        
        original_size = os.path.getsize(input_file)
        compressed_size = os.path.getsize(output_file)
        reduction = ((original_size - compressed_size) / original_size) * 100
        
        return jsonify({
            "success": True,
            "output_file": os.path.basename(output_file),
            "reduction_percent": round(reduction, 2)
        })
    
    except Exception as e:
        logger.error(f"Image compress error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/image/resize", methods=["POST"])
def resize_image():
    try:
        data = request.json
        input_file = os.path.join(app.config["UPLOAD_FOLDER"], data["filename"])
        
        output_file = image_editor.resize_image(
            input_file,
            app.config["OUTPUT_FOLDER"],
            data.get("width"),
            data.get("height"),
            data.get("maintain_aspect", True)
        )
        
        return jsonify({
            "success": True,
            "output_file": os.path.basename(output_file)
        })
    
    except Exception as e:
        logger.error(f"Resize error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/image/crop", methods=["POST"])
def crop_image():
    try:
        data = request.json
        input_file = os.path.join(app.config["UPLOAD_FOLDER"], data["filename"])
        
        output_file = image_editor.crop_image(
            input_file,
            app.config["OUTPUT_FOLDER"],
            data["x"],
            data["y"],
            data["width"],
            data["height"]
        )
        
        return jsonify({
            "success": True,
            "output_file": os.path.basename(output_file)
        })
    
    except Exception as e:
        logger.error(f"Crop error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# =================== OCR ===================
@app.route("/api/ocr", methods=["POST"])
def perform_ocr():
    try:
        data = request.json
        input_file = os.path.join(app.config["UPLOAD_FOLDER"], data["filename"])
        
        text = ocr_processor.extract_text(
            input_file,
            data.get("language", "eng")
        )
        
        return jsonify({
            "success": True,
            "text": text,
            "length": len(text)
        })
    
    except Exception as e:
        logger.error(f"OCR error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# =================== DOCUMENT MERGE ===================
@app.route("/api/merge", methods=["POST"])
def merge_documents():
    try:
        data = request.json
        input_files = [os.path.join(app.config["UPLOAD_FOLDER"], f) for f in data["files"]]
        file_type = data["file_type"]
        
        if file_type == "pdf":
            output_file = merger.merge_pdfs(input_files, app.config["OUTPUT_FOLDER"])
        elif file_type in ["docx", "doc"]:
            output_file = merger.merge_word_docs(input_files, app.config["OUTPUT_FOLDER"])
        elif file_type in ["xlsx", "xls"]:
            output_file = merger.merge_excel_files(input_files, app.config["OUTPUT_FOLDER"])
        elif file_type in ["jpg", "jpeg", "png", "gif", "bmp"]:
            output_file = merger.merge_images(input_files, app.config["OUTPUT_FOLDER"])
        else:
            return jsonify({"error": "Unsupported file type for merging"}), 400
        
        return jsonify({
            "success": True,
            "output_file": os.path.basename(output_file)
        })
    
    except Exception as e:
        logger.error(f"Merge error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# =================== DOWNLOAD ===================
@app.route("/api/download/<filename>", methods=["GET"])
def download_file(filename):
    try:
        filepath = os.path.join(app.config["OUTPUT_FOLDER"], filename)
        if not os.path.exists(filepath):
            return jsonify({"error": "File not found"}), 404
        
        return send_file(filepath, as_attachment=True)
    
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# =================== INFO ===================
@app.route("/api/info/<filename>", methods=["GET"])
def get_file_info(filename):
    try:
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        if not os.path.exists(filepath):
            return jsonify({"error": "File not found"}), 404
        
        file_type = detect_file_type(filepath)
        size = os.path.getsize(filepath)
        
        info = {
            "filename": filename,
            "file_type": file_type,
            "size": size,
            "size_formatted": format_file_size(size)
        }
        
        # Get additional info based on file type
        if file_type == "pdf":
            import PyPDF2
            with open(filepath, 'rb') as f:
                pdf = PyPDF2.PdfReader(f)
                info["pages"] = len(pdf.pages)
                info["encrypted"] = pdf.is_encrypted
        
        elif file_type in ["jpg", "jpeg", "png", "gif", "bmp"]:
            from PIL import Image
            with Image.open(filepath) as img:
                info["dimensions"] = img.size
                info["format"] = img.format
                info["mode"] = img.mode
        
        return jsonify(info)
    
    except Exception as e:
        logger.error(f"Info error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# =================== UTILITIES ===================
def format_file_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

# =================== ERROR HANDLERS ===================
@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "File too large. Maximum size is 100MB"}), 413

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)