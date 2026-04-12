// Tab Management
function openTab(tabName) {
    const contents = document.getElementsByClassName('tab-content');
    for (let content of contents) {
        content.classList.remove('active');
    }
    
    const buttons = document.getElementsByClassName('tab-button');
    for (let button of buttons) {
        button.classList.remove('active');
    }
    
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
}

// Show/hide loading
function showLoading() {
    document.getElementById('loading').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

// Show results
function showResult(message, isError = false) {
    const resultDiv = document.getElementById('resultContent');
    resultDiv.innerHTML = `<div class="${isError ? 'error' : 'success'}">${message}</div>`;
}

function showDownloadLink(filename, displayName = null) {
    const resultDiv = document.getElementById('resultContent');
    const name = displayName || filename;
    resultDiv.innerHTML += `<a href="/api/download/${filename}" class="download-link" download>📥 Download ${name}</a>`;
}

// Upload file
async function uploadFile(fileInput) {
    const file = fileInput.files[0];
    if (!file) {
        showResult('Please select a file', true);
        return null;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Upload failed');
        }
        
        return data.filename;
    } catch (error) {
        showResult(`Upload error: ${error.message}`, true);
        return null;
    }
}

// Convert File
async function convertFile() {
    const fileInput = document.getElementById('convertFile');
    const targetFormat = document.getElementById('targetFormat').value;
    
    if (!targetFormat) {
        showResult('Please select a target format', true);
        return;
    }
    
    showLoading();
    const filename = await uploadFile(fileInput);
    
    if (!filename) {
        hideLoading();
        return;
    }
    
    try {
        const response = await fetch('/api/convert', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename, target_format: targetFormat })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Conversion failed');
        }
        
        showResult(data.message);
        showDownloadLink(data.output_file);
    } catch (error) {
        showResult(`Conversion error: ${error.message}`, true);
    } finally {
        hideLoading();
    }
}

// Rotate PDF
async function rotatePDF() {
    const fileInput = document.getElementById('editFile');
    const angle = document.getElementById('rotateAngle').value;
    const pages = document.getElementById('rotatePages').value || 'all';
    
    showLoading();
    const filename = await uploadFile(fileInput);
    
    if (!filename) {
        hideLoading();
        return;
    }
    
    try {
        const response = await fetch('/api/pdf/rotate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename, angle: parseInt(angle), pages })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Rotation failed');
        }
        
        showResult('PDF rotated successfully');
        showDownloadLink(data.output_file);
    } catch (error) {
        showResult(`Rotation error: ${error.message}`, true);
    } finally {
        hideLoading();
    }
}

// Merge Files
async function mergeFiles() {
    const fileInput = document.getElementById('mergeFiles');
    const files = fileInput.files;
    
    if (files.length < 2) {
        showResult('Please select at least 2 files to merge', true);
        return;
    }
    
    showLoading();
    const uploadedFiles = [];
    
    for (let file of files) {
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            uploadedFiles.push(data.filename);
        } catch (error) {
            showResult(`Upload error: ${error.message}`, true);
            hideLoading();
            return;
        }
    }
    
    const mergeType = document.getElementById('mergeType').value;
    
    try {
        const response = await fetch('/api/pdf/merge', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ files: uploadedFiles })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Merge failed');
        }
        
        showResult('Files merged successfully');
        showDownloadLink(data.output_file);
    } catch (error) {
        showResult(`Merge error: ${error.message}`, true);
    } finally {
        hideLoading();
    }
}

// Split PDF
async function splitPDF() {
    const fileInput = document.getElementById('splitFile');
    const splitType = document.getElementById('splitType').value;
    const ranges = document.getElementById('splitRange').value;
    
    showLoading();
    const filename = await uploadFile(fileInput);
    
    if (!filename) {
        hideLoading();
        return;
    }
    
    try {
        const response = await fetch('/api/pdf/split', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename, split_type: splitType, ranges })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Split failed');
        }
        
        showResult(`PDF split into ${data.output_files.length} files`);
        data.output_files.forEach((file, index) => {
            showDownloadLink(file, `Part ${index + 1}`);
        });
    } catch (error) {
        showResult(`Split error: ${error.message}`, true);
    } finally {
        hideLoading();
    }
}

// Compress File
async function compressFile() {
    const fileInput = document.getElementById('compressFile');
    const quality = document.getElementById('compressQuality').value;
    
    showLoading();
    const filename = await uploadFile(fileInput);
    
    if (!filename) {
        hideLoading();
        return;
    }
    
    try {
        const response = await fetch('/api/pdf/compress', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename, quality })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Compression failed');
        }
        
        showResult(`File compressed! Size reduced by ${data.reduction_percent.toFixed(1)}%`);
        showDownloadLink(data.output_file);
    } catch (error) {
        showResult(`Compression error: ${error.message}`, true);
    } finally {
        hideLoading();
    }
}

// Add Watermark
async function addWatermark() {
    const fileInput = document.getElementById('watermarkFile');
    const text = document.getElementById('watermarkText').value;
    const position = document.getElementById('watermarkPosition').value;
    const opacity = document.getElementById('watermarkOpacity').value / 100;
    
    showLoading();
    const filename = await uploadFile(fileInput);
    
    if (!filename) {
        hideLoading();
        return;
    }
    
    try {
        const response = await fetch('/api/pdf/watermark', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename, text, position, opacity })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Watermark failed');
        }
        
        showResult('Watermark added successfully');
        showDownloadLink(data.output_file);
    } catch (error) {
        showResult(`Watermark error: ${error.message}`, true);
    } finally {
        hideLoading();
    }
}

// Protect PDF
async function protectPDF() {
    const fileInput = document.getElementById('protectFile');
    const password = document.getElementById('protectPassword').value;
    
    if (!password) {
        showResult('Please enter a password', true);
        return;
    }
    
    showLoading();
    const filename = await uploadFile(fileInput);
    
    if (!filename) {
        hideLoading();
        return;
    }
    
    try {
        const response = await fetch('/api/pdf/protect', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename, password })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Protection failed');
        }
        
        showResult('PDF protected successfully');
        showDownloadLink(data.output_file);
    } catch (error) {
        showResult(`Protection error: ${error.message}`, true);
    } finally {
        hideLoading();
    }
}

// Unlock PDF
async function unlockPDF() {
    const fileInput = document.getElementById('unlockFile');
    const password = document.getElementById('unlockPassword').value;
    
    if (!password) {
        showResult('Please enter the password', true);
        return;
    }
    
    showLoading();
    const filename = await uploadFile(fileInput);
    
    if (!filename) {
        hideLoading();
        return;
    }
    
    try {
        const response = await fetch('/api/pdf/unlock', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename, password })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Unlock failed');
        }
        
        showResult('PDF unlocked successfully');
        showDownloadLink(data.output_file);
    } catch (error) {
        showResult(`Unlock error: ${error.message}`, true);
    } finally {
        hideLoading();
    }
}

// Extract Content
async function extractContent() {
    const fileInput = document.getElementById('extractFile');
    const extractType = document.getElementById('extractType').value;
    
    showLoading();
    const filename = await uploadFile(fileInput);
    
    if (!filename) {
        hideLoading();
        return;
    }
    
    try {
        let endpoint;
        switch(extractType) {
            case 'text':
                endpoint = '/api/pdf/extract-text';
                break;
            case 'images':
                endpoint = '/api/pdf/extract-images';
                break;
            default:
                endpoint = '/api/pdf/extract-text';
        }
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Extraction failed');
        }
        
        if (extractType === 'text') {
            showResult(`Extracted ${data.length} characters of text`);
            document.getElementById('resultContent').innerHTML += `<pre style="max-height:300px;overflow:auto;background:white;padding:15px;border-radius:8px;">${data.text}</pre>`;
        } else if (extractType === 'images') {
            showResult(`Extracted ${data.count} images`);
            data.output_files.forEach((file, index) => {
                showDownloadLink(file, `Image ${index + 1}`);
            });
        }
    } catch (error) {
        showResult(`Extraction error: ${error.message}`, true);
    } finally {
        hideLoading();
    }
}

// OCR
async function performOCR() {
    const fileInput = document.getElementById('ocrFile');
    const language = document.getElementById('ocrLanguage').value;
    
    showLoading();
    const filename = await uploadFile(fileInput);
    
    if (!filename) {
        hideLoading();
        return;
    }
    
    try {
        const response = await fetch('/api/ocr', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename, language })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'OCR failed');
        }
        
        showResult(`Extracted ${data.length} characters`);
        document.getElementById('resultContent').innerHTML += `<pre style="max-height:300px;overflow:auto;background:white;padding:15px;border-radius:8px;">${data.text}</pre>`;
    } catch (error) {
        showResult(`OCR error: ${error.message}`, true);
    } finally {
        hideLoading();
    }
}

// Resize Image
async function resizeImage() {
    const fileInput = document.getElementById('imageFile');
    const width = document.getElementById('resizeWidth').value;
    const height = document.getElementById('resizeHeight').value;
    const maintainAspect = document.getElementById('maintainAspect').checked;
    
    if (!width && !height) {
        showResult('Please enter width and/or height', true);
        return;
    }
    
    showLoading();
    const filename = await uploadFile(fileInput);
    
    if (!filename) {
        hideLoading();
        return;
    }
    
    try {
        const response = await fetch('/api/image/resize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                filename, 
                width: width ? parseInt(width) : null,
                height: height ? parseInt(height) : null,
                maintain_aspect: maintainAspect
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Resize failed');
        }
        
        showResult('Image resized successfully');
        showDownloadLink(data.output_file);
    } catch (error) {
        showResult(`Resize error: ${error.message}`, true);
    } finally {
        hideLoading();
    }
}

// Crop Image
async function cropImage() {
    const fileInput = document.getElementById('imageFile');
    const x = document.getElementById('cropX').value;
    const y = document.getElementById('cropY').value;
    const width = document.getElementById('cropWidth').value;
    const height = document.getElementById('cropHeight').value;
    
    if (!width || !height) {
        showResult('Please enter crop dimensions', true);
        return;
    }
    
    showLoading();
    const filename = await uploadFile(fileInput);
    
    if (!filename) {
        hideLoading();
        return;
    }
    
    try {
        const response = await fetch('/api/image/crop', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                filename,
                x: parseInt(x),
                y: parseInt(y),
                width: parseInt(width),
                height: parseInt(height)
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Crop failed');
        }
        
        showResult('Image cropped successfully');
        showDownloadLink(data.output_file);
    } catch (error) {
        showResult(`Crop error: ${error.message}`, true);
    } finally {
        hideLoading();
    }
}

// Show/hide split range input
document.getElementById('splitType')?.addEventListener('change', function() {
    const rangeInput = document.getElementById('splitRange');
    rangeInput.style.display = this.value === 'range' ? 'block' : 'none';
});