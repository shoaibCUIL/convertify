# File Converter & Editor Pro - Complete Documentation

## 🎯 Overview

A comprehensive web-based file processing application with 100+ features including:
- **File Conversion** (PDF, DOCX, XLSX, PPTX, Images, etc.)
- **PDF Editing** (Rotate, Split, Merge, Crop, Delete pages, Add page numbers)
- **Image Editing** (Resize, Crop, Rotate, Flip, Filters, Effects)
- **Compression** (PDF & Image compression)
- **Watermarking** (Text & Image watermarks)
- **Security** (Password protect/unlock PDFs)
- **Content Extraction** (Text, Images, Tables, Metadata)
- **OCR** (Extract text from images and scanned PDFs)
- **Merging** (PDFs, Word docs, Excel files, Images)
- **Digital Signatures** (Sign and verify documents)

## 📁 Project Structure

```
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── utils/
│   ├── converter.py       # Universal file converter
│   ├── pdf_editor.py      # PDF editing operations
│   ├── image_editor.py    # Image editing operations
│   ├── merger.py          # File merging operations
│   ├── splitter.py        # File splitting operations
│   ├── compressor.py      # File compression
│   ├── extractor.py       # Content extraction
│   ├── ocr_processor.py   # OCR functionality
│   ├── watermark.py       # Watermark processing
│   ├── protector.py       # PDF encryption/decryption
│   ├── signer.py          # Digital signatures
│   └── file_detector.py   # File type detection
├── templates/
│   └── index.html         # Main web interface
├── static/
│   ├── css/
│   │   └── style.css      # Styling
│   └── js/
│       └── app.js         # Client-side JavaScript
├── uploads/               # Temporary upload storage
└── outputs/               # Processed files output
```

## 🚀 Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install System Dependencies

#### For OCR (Tesseract):
- **Windows**: Download from https://github.com/UB-Mannheim/tesseract/wiki
- **Linux**: `sudo apt-get install tesseract-ocr`
- **Mac**: `brew install tesseract`

#### For PDF to Image conversion:
- **Linux**: `sudo apt-get install poppler-utils`
- **Mac**: `brew install poppler`
- **Windows**: Download from http://blog.alivate.com.au/poppler-windows/

### 3. Additional Optional Dependencies

For advanced features:
```bash
# For better document conversion
pip install docx2pdf  # Windows only
pip install pandoc    # Cross-platform

# For table extraction
pip install pdfplumber camelot-py tabula-py
```

## 🎮 Usage

### Start the Server

```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Web Interface

1. Open your browser to `http://localhost:5000`
2. Select the operation tab (Convert, Edit, Merge, etc.)
3. Upload your file(s)
4. Configure options
5. Click the action button
6. Download the processed file(s)

### API Usage

All features are available via REST API:

#### Convert File
```bash
# Upload file first
curl -X POST -F "file=@document.pdf" http://localhost:5000/api/upload

# Convert
curl -X POST http://localhost:5000/api/convert \
  -H "Content-Type: application/json" \
  -d '{"filename": "uploaded_file.pdf", "target_format": "docx"}'
```

#### Merge PDFs
```bash
curl -X POST http://localhost:5000/api/pdf/merge \
  -H "Content-Type: application/json" \
  -d '{"files": ["file1.pdf", "file2.pdf", "file3.pdf"]}'
```

#### Add Watermark
```bash
curl -X POST http://localhost:5000/api/pdf/watermark \
  -H "Content-Type: application/json" \
  -d '{"filename": "document.pdf", "text": "CONFIDENTIAL", "opacity": 0.3}'
```

#### Compress PDF
```bash
curl -X POST http://localhost:5000/api/pdf/compress \
  -H "Content-Type: application/json" \
  -d '{"filename": "document.pdf", "quality": "medium"}'
```

#### Extract Text (OCR)
```bash
curl -X POST http://localhost:5000/api/ocr \
  -H "Content-Type: application/json" \
  -d '{"filename": "scanned.pdf", "language": "eng"}'
```

## 📋 Features List

### File Conversion
- **PDF to**: DOCX, JPG, PNG, TXT, HTML
- **DOCX to**: PDF, TXT, HTML
- **Images to**: PDF, JPG, PNG, GIF, BMP, WebP
- **XLSX to**: PDF, CSV
- **PPTX to**: PDF, JPG, PNG

### PDF Operations
- Rotate pages (90°, 180°, 270°)
- Delete specific pages
- Extract page ranges
- Reorder pages
- Crop pages
- Add blank pages
- Add page numbers
- Convert to grayscale
- Resize to standard page sizes

### Image Operations
- Resize (with aspect ratio)
- Crop
- Rotate (any angle)
- Flip (horizontal/vertical)
- Adjust brightness, contrast, saturation
- Apply filters (blur, sharpen, emboss, etc.)
- Add borders
- Add text
- Apply effects (cartoon, pencil sketch, oil painting)

### Compression
- PDF compression (low/medium/high quality)
- Image compression (JPEG quality control)
- Optimize to target file size

### Merging
- Merge multiple PDFs
- Merge Word documents
- Merge Excel files (as sheets or rows)
- Merge images (vertical/horizontal/grid)

### Splitting
- Split PDF into individual pages
- Split by page ranges
- Split every N pages
- Split in half
- Split by file size

### Watermarking
- Text watermarks (customizable position, opacity, angle)
- Image watermarks
- Batch watermarking

### Security
- Password protect PDFs
- Remove password protection
- Set permissions (print, modify, copy)
- Digital signatures

### Content Extraction
- Extract text from PDFs
- Extract images from PDFs
- Extract tables
- Extract metadata
- Extract hyperlinks
- Extract fonts
- Extract attachments
- Extract form data

### OCR
- Extract text from images
- Extract text from scanned PDFs
- Multi-language support
- Create searchable PDFs

## ⚙️ Configuration

Edit `app.py` to customize:

```python
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # Max file size (100MB)
app.config["ALLOWED_EXTENSIONS"] = {...}  # Allowed file types
```

## 🔧 Troubleshooting

### "Tesseract not found"
- Install Tesseract OCR (see Installation section)
- Set path in `ocr_processor.py` if needed

### "Poppler not found"
- Install poppler-utils (see Installation section)

### "Module not found"
- Install missing dependency: `pip install <module_name>`

### "File too large"
- Increase `MAX_CONTENT_LENGTH` in app.py

## 📝 API Reference

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload` | POST | Upload a file |
| `/api/convert` | POST | Convert file format |
| `/api/pdf/merge` | POST | Merge PDFs |
| `/api/pdf/split` | POST | Split PDF |
| `/api/pdf/rotate` | POST | Rotate PDF pages |
| `/api/pdf/compress` | POST | Compress PDF |
| `/api/pdf/watermark` | POST | Add watermark |
| `/api/pdf/protect` | POST | Password protect |
| `/api/pdf/unlock` | POST | Remove password |
| `/api/pdf/extract-text` | POST | Extract text |
| `/api/pdf/extract-images` | POST | Extract images |
| `/api/image/resize` | POST | Resize image |
| `/api/image/crop` | POST | Crop image |
| `/api/image/compress` | POST | Compress image |
| `/api/ocr` | POST | Perform OCR |
| `/api/download/<filename>` | GET | Download file |
| `/api/info/<filename>` | GET | Get file info |

## 🎨 Customization

### Add New Conversion Format

Edit `utils/converter.py`:

```python
def _sourceformat_to_targetformat(self, input_file, output_path):
    # Your conversion logic here
    pass
```

Update `supported_conversions` dict.

### Add New PDF Operation

Edit `utils/pdf_editor.py` and add method, then create route in `app.py`.

## 📄 License

This project is open source and available for modification.

## 🤝 Contributing

Feel free to add new features, fix bugs, or improve documentation!

## 🔗 Useful Links

- Flask Documentation: https://flask.palletsprojects.com/
- PyPDF2 Documentation: https://pypdf2.readthedocs.io/
- Pillow Documentation: https://pillow.readthedocs.io/
- Tesseract OCR: https://github.com/tesseract-ocr/tesseract

## ⚡ Performance Tips

1. **For large files**: Increase server timeout
2. **For batch processing**: Use API directly
3. **For production**: Use gunicorn or uWSGI
4. **For scaling**: Add task queue (Celery)

## 🐛 Known Issues

- DOCX to PDF conversion requires MS Word or LibreOffice on Windows
- Some advanced PDF features require PyMuPDF
- OCR accuracy depends on image quality

## 📞 Support

For issues or questions, check the code comments or create an issue in your repository.

---

**Happy Converting! 🚀**