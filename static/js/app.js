// Universal File Converter - Main JavaScript

const API_BASE = '/api';
let uploadedFiles = [];
let convertedFiles = [];

// DOM Elements
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
const toolButtons = document.querySelectorAll('.tool-btn');
const toolPanels = document.querySelectorAll('.tool-panel');
const progressSection = document.getElementById('progressSection');
const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');
const resultsSection = document.getElementById('resultsSection');
const resultsList = document.getElementById('resultsList');
const modalOverlay = document.getElementById('modalOverlay');
const modalTitle = document.getElementById('modalTitle');
const modalBody = document.getElementById('modalBody');
const modalFooter = document.getElementById('modalFooter');
const modalClose = document.getElementById('modalClose');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    // Dropzone
    dropzone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);
    
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });
    
    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
    });
    
    dropzone.addEventListener('drop', handleFileDrop);
    
    // Tool navigation
    toolButtons.forEach(btn => {
        btn.addEventListener('click', () => switchTool(btn.dataset.tool));
    });
    
    // Convert button
    document.getElementById('convertBtn')?.addEventListener('click', handleConvert);
    
    // OCR button
    document.getElementById('ocrBtn')?.addEventListener('click', handleOCR);
    
    // PDF tool actions
    document.querySelectorAll('.tool-action-btn').forEach(btn => {
        btn.addEventListener('click', () => handleToolAction(btn.dataset.action));
    });
    
    // Results actions
    document.getElementById('downloadAllBtn')?.addEventListener('click', downloadAllAsZip);
    document.getElementById('clearResultsBtn')?.addEventListener('click', clearResults);
    
    // Modal
    modalClose.addEventListener('click', closeModal);
    modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) closeModal();
    });
}

// File Selection
function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    uploadFiles(files);
}

function handleFileDrop(e) {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    
    const files = Array.from(e.dataTransfer.files);
    uploadFiles(files);
}

// Upload Files
async function uploadFiles(files) {
    for (const file of files) {
        await uploadSingleFile(file);
    }
}

async function uploadSingleFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            uploadedFiles.push(data);
            addFileToList(data);
        } else {
            showError(data.error || 'Upload failed');
        }
    } catch (error) {
        showError('Upload error: ' + error.message);
    }
}

function addFileToList(fileData) {
    const fileItem = document.createElement('div');
    fileItem.className = 'file-item';
    fileItem.dataset.fileId = fileData.file_id;
    
    const icon = getFileIcon(fileData.file_type);
    
    fileItem.innerHTML = `
        <div class="file-info-wrapper">
            <div class="file-icon">${icon}</div>
            <div class="file-details">
                <h4>${fileData.original_filename}</h4>
                <div class="file-meta">
                    ${fileData.file_type.toUpperCase()} • ${fileData.size_formatted}
                </div>
            </div>
        </div>
        <div class="file-actions">
            <button class="btn-icon btn-delete" onclick="removeFile('${fileData.file_id}')">
                🗑️
            </button>
        </div>
    `;
    
    fileList.appendChild(fileItem);
}

function getFileIcon(fileType) {
    const icons = {
        'pdf': '📄',
        'image': '🖼️',
        'video': '🎥',
        'audio': '🎵',
        'document': '📝',
        'spreadsheet': '📊',
        'presentation': '📽️',
        'text': '📃',
        'archive': '📦',
        'other': '📎'
    };
    return icons[fileType] || icons['other'];
}

function removeFile(fileId) {
    uploadedFiles = uploadedFiles.filter(f => f.file_id !== fileId);
    const fileItem = document.querySelector(`[data-file-id="${fileId}"]`);
    if (fileItem) fileItem.remove();
}

// Tool Switching
function switchTool(toolName) {
    toolButtons.forEach(btn => btn.classList.remove('active'));
    toolPanels.forEach(panel => panel.classList.remove('active'));
    
    const activeBtn = document.querySelector(`[data-tool="${toolName}"]`);
    const activePanel = document.getElementById(`panel-${toolName}`);
    
    if (activeBtn) activeBtn.classList.add('active');
    if (activePanel) activePanel.classList.add('active');
}

// Universal Convert
async function handleConvert() {
    if (uploadedFiles.length === 0) {
        showError('Please upload a file first');
        return;
    }
    
    const targetFormat = document.getElementById('targetFormat').value;
    if (!targetFormat) {
        showError('Please select a target format');
        return;
    }
    
    showProgress('Converting file...');
    
    try {
        for (const file of uploadedFiles) {
            const response = await fetch(`${API_BASE}/convert`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    filename: file.filename,
                    target_format: targetFormat
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                convertedFiles.push({
                    filename: data.output_filename,
                    originalName: file.original_filename
                });
            } else {
                showError(data.error || 'Conversion failed');
            }
        }
        
        hideProgress();
        showResults();
    } catch (error) {
        hideProgress();
        showError('Conversion error: ' + error.message);
    }
}

// Handle Tool Actions
async function handleToolAction(action) {
    if (uploadedFiles.length === 0) {
        showError('Please upload a file first');
        return;
    }
    
    switch (action) {
        case 'merge':
            await mergePDFs();
            break;
        case 'split':
            showSplitPDFModal();
            break;
        case 'compress':
            await compressPDF();
            break;
        case 'to-images':
            await pdfToImages();
            break;
        case 'watermark':
            showWatermarkModal();
            break;
        case 'rotate':
            showRotateModal();
            break;
        case 'protect':
            showProtectModal();
            break;
        case 'unlock':
            showUnlockModal();
            break;
        case 'page-numbers':
            showPageNumbersModal();
            break;
        case 'extract-text':
            await extractText();
            break;
        case 'resize':
            showResizeModal();
            break;
        case 'compress-img':
            await compressImage();
            break;
        case 'to-pdf':
            await imagesToPDF();
            break;
        case 'extract-audio':
            await extractAudio();
            break;
        default:
            showError('Action not implemented yet');
    }
}

// PDF Operations
async function mergePDFs() {
    if (uploadedFiles.length < 2) {
        showError('Please upload at least 2 PDF files');
        return;
    }
    
    showProgress('Merging PDFs...');
    
    try {
        const response = await fetch(`${API_BASE}/pdf/merge`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filenames: uploadedFiles.map(f => f.filename)
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            convertedFiles.push({
                filename: data.output_filename,
                originalName: 'merged.pdf'
            });
            hideProgress();
            showResults();
        } else {
            hideProgress();
            showError(data.error);
        }
    } catch (error) {
        hideProgress();
        showError('Merge error: ' + error.message);
    }
}

async function compressPDF() {
    showProgress('Compressing PDF...');
    
    try {
        const response = await fetch(`${API_BASE}/pdf/compress`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: uploadedFiles[0].filename,
                quality: 'medium'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            convertedFiles.push({
                filename: data.output_filename,
                originalName: 'compressed.pdf',
                meta: `${data.compression_ratio} smaller`
            });
            hideProgress();
            showResults();
        } else {
            hideProgress();
            showError(data.error);
        }
    } catch (error) {
        hideProgress();
        showError('Compression error: ' + error.message);
    }
}

async function pdfToImages() {
    showProgress('Converting PDF to images...');
    
    try {
        const response = await fetch(`${API_BASE}/pdf/to-images`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: uploadedFiles[0].filename,
                format: 'png',
                dpi: 200
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            data.output_files.forEach(filename => {
                convertedFiles.push({ filename, originalName: filename });
            });
            hideProgress();
            showResults();
        } else {
            hideProgress();
            showError(data.error);
        }
    } catch (error) {
        hideProgress();
        showError('Conversion error: ' + error.message);
    }
}

async function extractText() {
    showProgress('Extracting text...');
    
    try {
        const response = await fetch(`${API_BASE}/pdf/extract-text`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: uploadedFiles[0].filename
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            convertedFiles.push({
                filename: data.output_filename,
                originalName: 'extracted_text.txt'
            });
            hideProgress();
            showResults();
        } else {
            hideProgress();
            showError(data.error);
        }
    } catch (error) {
        hideProgress();
        showError('Extraction error: ' + error.message);
    }
}

// Image Operations
async function compressImage() {
    showProgress('Compressing image...');
    
    try {
        const response = await fetch(`${API_BASE}/image/compress`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: uploadedFiles[0].filename,
                quality: 85
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            convertedFiles.push({
                filename: data.output_filename,
                originalName: 'compressed_image',
                meta: `${data.compression_ratio} smaller`
            });
            hideProgress();
            showResults();
        } else {
            hideProgress();
            showError(data.error);
        }
    } catch (error) {
        hideProgress();
        showError('Compression error: ' + error.message);
    }
}

async function imagesToPDF() {
    showProgress('Converting images to PDF...');
    
    try {
        const response = await fetch(`${API_BASE}/images/to-pdf`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filenames: uploadedFiles.map(f => f.filename)
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            convertedFiles.push({
                filename: data.output_filename,
                originalName: 'images.pdf'
            });
            hideProgress();
            showResults();
        } else {
            hideProgress();
            showError(data.error);
        }
    } catch (error) {
        hideProgress();
        showError('Conversion error: ' + error.message);
    }
}

// Video Operations
async function extractAudio() {
    showProgress('Extracting audio...');
    
    try {
        const response = await fetch(`${API_BASE}/video/extract-audio`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: uploadedFiles[0].filename,
                audio_format: 'mp3'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            convertedFiles.push({
                filename: data.output_filename,
                originalName: 'audio.mp3'
            });
            hideProgress();
            showResults();
        } else {
            hideProgress();
            showError(data.error);
        }
    } catch (error) {
        hideProgress();
        showError('Extraction error: ' + error.message);
    }
}

// OCR
async function handleOCR() {
    if (uploadedFiles.length === 0) {
        showError('Please upload a file first');
        return;
    }
    
    const language = document.getElementById('ocrLanguage').value;
    const outputFormat = document.getElementById('ocrOutput').value;
    
    showProgress('Performing OCR...');
    
    try {
        const response = await fetch(`${API_BASE}/ocr`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: uploadedFiles[0].filename,
                language,
                output_format: outputFormat
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            convertedFiles.push({
                filename: data.output_filename,
                originalName: outputFormat === 'text' ? 'ocr_text.txt' : 'ocr_searchable.pdf'
            });
            hideProgress();
            showResults();
        } else {
            hideProgress();
            showError(data.error);
        }
    } catch (error) {
        hideProgress();
        showError('OCR error: ' + error.message);
    }
}

// Modals
function showWatermarkModal() {
    modalTitle.textContent = 'Add Watermark';
    modalBody.innerHTML = `
        <div class="form-group">
            <label>Watermark Text:</label>
            <input type="text" id="watermarkText" class="form-control" value="CONFIDENTIAL">
        </div>
        <div class="form-group">
            <label>Opacity:</label>
            <input type="range" id="watermarkOpacity" class="form-control" min="0" max="1" step="0.1" value="0.3">
        </div>
    `;
    modalFooter.innerHTML = `
        <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
        <button class="btn btn-primary" onclick="applyWatermark()">Apply</button>
    `;
    modalOverlay.style.display = 'flex';
}

async function applyWatermark() {
    const text = document.getElementById('watermarkText').value;
    const opacity = parseFloat(document.getElementById('watermarkOpacity').value);
    
    closeModal();
    showProgress('Adding watermark...');
    
    try {
        const response = await fetch(`${API_BASE}/pdf/watermark`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: uploadedFiles[0].filename,
                watermark_text: text,
                opacity
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            convertedFiles.push({
                filename: data.output_filename,
                originalName: 'watermarked.pdf'
            });
            hideProgress();
            showResults();
        } else {
            hideProgress();
            showError(data.error);
        }
    } catch (error) {
        hideProgress();
        showError('Watermark error: ' + error.message);
    }
}

function closeModal() {
    modalOverlay.style.display = 'none';
}

// Progress
function showProgress(message) {
    progressText.textContent = message;
    progressBar.style.width = '100%';
    progressSection.style.display = 'block';
    resultsSection.style.display = 'none';
}

function hideProgress() {
    progressSection.style.display = 'none';
}

// Results
function showResults() {
    resultsList.innerHTML = '';
    
    convertedFiles.forEach(file => {
        const resultItem = document.createElement('div');
        resultItem.className = 'result-item';
        resultItem.innerHTML = `
            <div class="result-info">
                <div class="result-name">${file.originalName}</div>
                <div class="result-meta">${file.meta || 'Ready to download'}</div>
            </div>
            <button class="btn btn-primary" onclick="downloadFile('${file.filename}')">
                Download
            </button>
        `;
        resultsList.appendChild(resultItem);
    });
    
    resultsSection.style.display = 'block';
}

function downloadFile(filename) {
    window.open(`${API_BASE}/download/${filename}`, '_blank');
}

async function downloadAllAsZip() {
    try {
        const response = await fetch(`${API_BASE}/download-multiple`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filenames: convertedFiles.map(f => f.filename)
            })
        });
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'converted_files.zip';
        a.click();
    } catch (error) {
        showError('Download error: ' + error.message);
    }
}

function clearResults() {
    convertedFiles = [];
    uploadedFiles = [];
    fileList.innerHTML = '';
    resultsSection.style.display = 'none';
}

// Error Handling
function showError(message) {
    alert('Error: ' + message);
}

// Additional modal functions (simplified versions)
function showSplitPDFModal() { showError('Split PDF modal not fully implemented in this demo'); }
function showRotateModal() { showError('Rotate modal not fully implemented in this demo'); }
function showProtectModal() { showError('Protect modal not fully implemented in this demo'); }
function showUnlockModal() { showError('Unlock modal not fully implemented in this demo'); }
function showPageNumbersModal() { showError('Page numbers modal not fully implemented in this demo'); }
function showResizeModal() { showError('Resize modal not fully implemented in this demo'); }