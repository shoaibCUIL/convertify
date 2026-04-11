# Universal File Converter & Editor

A production-ready web application for converting and editing files across 50+ formats. Built with Flask (Python backend) and vanilla JavaScript (frontend).

## 🚀 Features

### Universal File Conversion
- **Documents**: DOCX, XLSX, PPTX, TXT, RTF, ODT, ODS, ODP ↔ PDF, HTML, CSV
- **Images**: PNG, JPG, WEBP, GIF, BMP, TIFF, SVG ↔ All formats + PDF
- **Video**: MP4, AVI, MOV, MKV, WEBM ↔ All formats
- **Audio**: MP3, WAV, OGG, AAC, M4A ↔ All formats
- **PDF Operations**: Merge, Split, Compress, Watermark, Protect, Extract Text

### Editing Features
- **PDF**: Rotate pages, add page numbers, remove pages, compress
- **Images**: Resize, compress, convert format, grayscale
- **Video**: Extract audio, change resolution, convert format
- **OCR**: Extract text from images and scanned PDFs (10+ languages)

### User Interface
- Drag-and-drop file upload
- Multi-file processing
- Real-time progress tracking
- File preview and management
- Batch download as ZIP

## 📋 Requirements

### System Dependencies
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    libreoffice \
    ffmpeg \
    imagemagick \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libmagic1

# Additional Tesseract languages (optional)
sudo apt-get install tesseract-ocr-spa tesseract-ocr-fra tesseract-ocr-deu

# macOS
brew install python3 libreoffice ffmpeg imagemagick tesseract poppler libmagic
```

### Python Dependencies
All Python packages are listed in `requirements.txt`

## 🛠️ Installation

### 1. Clone or Extract
```bash
# If you have the files in a directory
cd file-converter-app
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Verify System Tools
```bash
# Check if all tools are installed
libreoffice --version
ffmpeg -version
convert -version  # ImageMagick
tesseract --version
pdfinfo -v  # Poppler
```

### 5. Set Environment Variables (Optional)
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key-here
```

## 🏃 Running Locally

### Development Mode
```bash
python app.py
```

The application will be available at: `http://localhost:5000`

### Production Mode with Gunicorn
```bash
# Install Gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🌐 Deployment

### Deploy on Linux VPS (Ubuntu/Debian)

#### 1. Setup Server
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y python3 python3-pip python3-venv \
    libreoffice ffmpeg imagemagick tesseract-ocr poppler-utils \
    libmagic1 nginx supervisor

# Create application user
sudo useradd -m -s /bin/bash fileconv
sudo su - fileconv
```

#### 2. Deploy Application
```bash
# Clone/upload your application
cd /home/fileconv
# Upload files here

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn
```

#### 3. Configure Gunicorn with Supervisor
```bash
# Create supervisor config
sudo nano /etc/supervisor/conf.d/fileconverter.conf
```

Add this configuration:
```ini
[program:fileconverter]
directory=/home/fileconv/file-converter-app
command=/home/fileconv/file-converter-app/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
user=fileconv
autostart=true
autorestart=true
stderr_logfile=/var/log/fileconverter.err.log
stdout_logfile=/var/log/fileconverter.out.log
environment=SECRET_KEY="your-secret-key-here"
```

#### 4. Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/fileconverter
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;  # or IP address
    
    client_max_body_size 500M;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # Timeouts for large file uploads
        proxy_connect_timeout 600;
        proxy_send_timeout 600;
        proxy_read_timeout 600;
        send_timeout 600;
    }
    
    location /static {
        alias /home/fileconv/file-converter-app/static;
        expires 30d;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/fileconverter /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 5. Start Services
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start fileconverter
```

#### 6. Enable SSL (Optional but Recommended)
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Deploy with Docker (Alternative)

Create `Dockerfile`:
```dockerfile
FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    libreoffice ffmpeg imagemagick tesseract-ocr \
    poppler-utils libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy application
COPY . /app

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Expose port
EXPOSE 5000

# Run application
CMD ["python3", "app.py"]
```

Build and run:
```bash
docker build -t file-converter .
docker run -p 5000:5000 -v $(pwd)/uploads:/app/uploads -v $(pwd)/outputs:/app/outputs file-converter
```

## 🧪 Testing

### Test API Endpoints

#### Upload File
```bash
curl -X POST -F "file=@test.pdf" http://localhost:5000/api/upload
```

#### Convert File
```bash
curl -X POST http://localhost:5000/api/convert \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "uploaded_filename.pdf",
    "target_format": "docx"
  }'
```

#### Merge PDFs
```bash
curl -X POST http://localhost:5000/api/pdf/merge \
  -H "Content-Type: application/json" \
  -d '{
    "filenames": ["file1.pdf", "file2.pdf"]
  }'
```

#### Perform OCR
```bash
curl -X POST http://localhost:5000/api/ocr \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "scanned.pdf",
    "language": "eng",
    "output_format": "text"
  }'
```

## 📁 Project Structure

```
file-converter-app/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
│
├── engines/              # Conversion engines
│   ├── __init__.py
│   ├── pdf_engine.py     # PDF operations
│   ├── image_engine.py   # Image operations
│   ├── video_engine.py   # Video/audio operations
│   ├── document_engine.py # Document conversion
│   └── ocr_engine.py     # OCR operations
│
├── utils/                # Utility modules
│   ├── __init__.py
│   ├── file_detector.py  # File type detection
│   ├── converter.py      # Universal converter
│   └── security.py       # Security & validation
│
├── workers/              # Background tasks
│   ├── __init__.py
│   └── tasks.py          # Cleanup & async tasks
│
├── templates/            # HTML templates
│   └── index.html
│
├── static/               # Static assets
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
│
├── uploads/              # Uploaded files (auto-created)
├── outputs/              # Converted files (auto-created)
└── temp/                 # Temporary files (auto-created)
```

## 🔧 Configuration

### Environment Variables
- `FLASK_ENV`: Set to `production` or `development`
- `SECRET_KEY`: Secret key for Flask sessions
- `MAX_CONTENT_LENGTH`: Maximum file size (default: 500MB)

### File Cleanup
By default, files older than 24 hours are automatically deleted. Adjust in `workers/tasks.py`:
```python
cleanup_old_files(max_age_hours=24)
```

## 🛡️ Security Features

- File type validation using magic bytes
- Path sanitization to prevent directory traversal
- File size limits (500MB default)
- Blocked executable file extensions
- MIME type verification
- Secure filename handling

## 🐛 Troubleshooting

### LibreOffice Not Found
```bash
# Find LibreOffice path
which libreoffice

# Add to PATH if needed
export PATH=$PATH:/path/to/libreoffice
```

### FFmpeg Not Working
```bash
# Verify installation
ffmpeg -version

# Reinstall if needed
sudo apt-get install --reinstall ffmpeg
```

### Tesseract Language Missing
```bash
# List installed languages
tesseract --list-langs

# Install missing language
sudo apt-get install tesseract-ocr-<lang>
```

### Permission Errors
```bash
# Fix permissions
sudo chown -R fileconv:fileconv /home/fileconv/file-converter-app
chmod -R 755 /home/fileconv/file-converter-app
```

## 📊 Performance

- Handles files up to 500MB
- Multi-threaded processing
- Automatic cleanup of old files
- Optimized for concurrent requests

## 🔄 Supported Conversions

### From PDF
- PDF → DOCX, TXT, HTML, PNG, JPG

### From Images
- PNG, JPG, WEBP, GIF → PDF, all image formats

### From Documents
- DOCX, XLSX, PPTX → PDF, HTML, TXT, CSV

### From Video
- MP4, AVI, MOV → All video formats, MP3, WAV

### From Audio
- MP3, WAV, OGG → All audio formats

## 📝 API Documentation

### Endpoints

#### POST /api/upload
Upload a file
- Body: multipart/form-data with 'file'
- Returns: File metadata and unique ID

#### POST /api/convert
Universal file conversion
- Body: `{"filename": "...", "target_format": "..."}`
- Returns: Converted file information

#### POST /api/pdf/merge
Merge multiple PDFs
- Body: `{"filenames": ["file1.pdf", "file2.pdf"]}`

#### POST /api/pdf/compress
Compress PDF
- Body: `{"filename": "...", "quality": "low|medium|high"}`

#### POST /api/ocr
Perform OCR
- Body: `{"filename": "...", "language": "eng", "output_format": "text|pdf"}`

See `app.py` for complete API documentation.

## 📄 License

This project is provided as-is for educational and commercial use.

## 🤝 Contributing

Contributions welcome! Please feel free to submit pull requests or open issues.

## 📧 Support

For issues or questions, please open a GitHub issue.

---

Built with ❤️ using Flask, Python, LibreOffice, FFmpeg, and modern web technologies.