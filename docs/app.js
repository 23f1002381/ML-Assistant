// Business Card Intelligence - Real OCR Web App for GitHub Pages
class BusinessCardApp {
    constructor() {
        this.extractedData = [];
        this.ocrService = null;
        this.init();
    }

    async init() {
        // Load OCR service
        this.ocrService = new OCRService();
        
        // Load any stored API key
        const storedApiKey = this.ocrService.getAPIKey();
        if (storedApiKey) {
            this.ocrService.setAPIKey(storedApiKey);
        }

        this.setupEventListeners();
        this.loadStoredData();
        this.showAPIKeySection();
    }

    setupEventListeners() {
        const fileInput = document.getElementById('fileInput');
        const extractBtn = document.getElementById('extractBtn');
        const clearBtn = document.getElementById('clearBtn');
        const downloadBtn = document.getElementById('downloadBtn');
        const apiKeyBtn = document.getElementById('apiKeyBtn');
        const uploadArea = document.getElementById('uploadArea');

        if (fileInput) {
            fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        }

        if (extractBtn) {
            extractBtn.addEventListener('click', () => this.extractInformation());
        }

        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearAll());
        }

        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => this.downloadExcel());
        }

        if (apiKeyBtn) {
            apiKeyBtn.addEventListener('click', () => this.setAPIKey());
        }

        // Drag and drop functionality
        if (uploadArea) {
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });

            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('dragover');
            });

            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                
                const files = Array.from(e.dataTransfer.files);
                const fileInput = document.getElementById('fileInput');
                fileInput.files = e.dataTransfer.files;
                this.handleFileSelect({ target: { files } });
            });

            uploadArea.addEventListener('click', () => {
                fileInput.click();
            });
        }
    }

    showAPIKeySection() {
        const apiKeySection = document.getElementById('apiKeySection');
        const hasApiKey = this.ocrService.getAPIKey();
        
        if (apiKeySection) {
            if (hasApiKey) {
                apiKeySection.innerHTML = `
                    <div style="background: #e8f5e8; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                        <p style="margin: 0; color: #2d5a2d;">✅ OCR API Key configured</p>
                        <button onclick="app.setAPIKey()" style="margin-top: 0.5rem; padding: 0.5rem 1rem; background: #2d5a2d; color: white; border: none; border-radius: 4px; cursor: pointer;">Change API Key</button>
                    </div>
                `;
            } else {
                apiKeySection.innerHTML = `
                    <div style="background: #fff3cd; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                        <h4 style="margin: 0 0 0.5rem 0; color: #856404;">🔑 Set Up OCR API Key (Optional)</h4>
                        <p style="margin: 0 0 0.5rem 0; color: #856404;">Get free OCR API key from <a href="https://ocr.space/" target="_blank">OCR.space</a> (500 requests/month free)</p>
                        <button onclick="app.setAPIKey()" style="padding: 0.5rem 1rem; background: #856404; color: white; border: none; border-radius: 4px; cursor: pointer;">Set API Key</button>
                        <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; color: #666;">Without API key, app will use browser-based OCR (slower but free)</p>
                    </div>
                `;
            }
        }
    }

    setAPIKey() {
        const apiKey = prompt('Enter your OCR.space API key (get free key at https://ocr.space/):');
        if (apiKey) {
            this.ocrService.setAPIKey(apiKey);
            this.showAPIKeySection();
            this.showNotification('API key saved successfully!', 'success');
        }
    }

    handleFileSelect(event) {
        const files = event.target.files;
        const maxFiles = 10;
        
        if (files.length > maxFiles) {
            this.showNotification(`Maximum ${maxFiles} files allowed. Only first ${maxFiles} will be processed.`, 'warning');
            const fileArray = Array.from(files).slice(0, maxFiles);
            this.displaySelectedFiles(fileArray);
        } else {
            this.displaySelectedFiles(Array.from(files));
        }
    }

    displaySelectedFiles(files) {
        const filePreview = document.getElementById('filePreview');
        if (!filePreview) return;

        filePreview.innerHTML = '';
        files.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <div class="file-info">
                    <span class="file-name">${file.name}</span>
                    <span class="file-size">${this.formatFileSize(file.size)}</span>
                </div>
                <div class="file-preview">
                    <img src="${URL.createObjectURL(file)}" alt="${file.name}" />
                </div>
            `;
            filePreview.appendChild(fileItem);
        });

        document.getElementById('extractBtn').disabled = false;
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async extractInformation() {
        const fileInput = document.getElementById('fileInput');
        const files = Array.from(fileInput.files);
        
        if (files.length === 0) {
            this.showNotification('Please select files first', 'error');
            return;
        }

        this.showProgress(true);
        this.extractedData = [];

        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            this.updateProgress(i + 1, files.length, file.name);
            
            try {
                // Real OCR extraction
                const extractedText = await this.ocrService.extractTextFromImage(file);
                
                if (!extractedText.trim()) {
                    this.showNotification(`No text detected in: ${file.name}`, 'warning');
                    const entities = { Name: '', Title: '', Company: '', Email: '', Phone: '', Address: '', Website: '' };
                    entities._source_file = file.name;
                    entities._raw_text = '';
                    this.extractedData.push(entities);
                } else {
                    const entities = this.ocrService.extractEntities(extractedText);
                    entities._source_file = file.name;
                    entities._raw_text = extractedText;
                    this.extractedData.push(entities);
                }
                
                // Small delay to show progress
                await this.delay(100);
            } catch (error) {
                console.error(`Error processing ${file.name}:`, error);
                this.showNotification(`Error processing ${file.name}: ${error.message}`, 'error');
                
                // Add empty entry for failed processing
                const entities = { Name: '', Title: '', Company: '', Email: '', Phone: '', Address: '', Website: '' };
                entities._source_file = file.name;
                entities._raw_text = `Error: ${error.message}`;
                this.extractedData.push(entities);
            }
        }

        this.displayResults();
        this.showProgress(false);
        this.showNotification('Processing complete!', 'success');
        this.storeData();
    }

    displayResults() {
        const resultsContainer = document.getElementById('resultsContainer');
        const summaryContainer = document.getElementById('summaryContainer');
        
        if (!resultsContainer) return;

        resultsContainer.innerHTML = '';
        
        this.extractedData.forEach((card, index) => {
            const cardElement = document.createElement('div');
            cardElement.className = 'result-card';
            cardElement.innerHTML = `
                <div class="card-header">
                    <h3>Card ${index + 1}: ${card._source_file}</h3>
                    <button class="toggle-btn" onclick="app.toggleCardDetails(${index})">
                        <span class="toggle-icon">▼</span>
                    </button>
                </div>
                <div class="card-content" id="card-${index}">
                    <div class="card-fields">
                        ${Object.entries(card).filter(([key]) => !key.startsWith('_')).map(([field, value]) => `
                            <div class="field-group">
                                <label>${field}:</label>
                                <input type="text" value="${value}" onchange="app.updateField(${index}, '${field}', this.value)" />
                            </div>
                        `).join('')}
                    </div>
                    <div class="raw-text">
                        <button class="toggle-raw" onclick="app.toggleRawText(${index})">View Raw OCR Text</button>
                        <div class="raw-content" id="raw-${index}" style="display: none;">
                            <pre>${card._raw_text || 'No text extracted'}</pre>
                        </div>
                    </div>
                </div>
            `;
            resultsContainer.appendChild(cardElement);
        });

        // Update summary
        if (summaryContainer) {
            const emailsFound = this.extractedData.filter(card => card.Email).length;
            const phonesFound = this.extractedData.filter(card => card.Phone).length;
            
            summaryContainer.innerHTML = `
                <div class="summary-stats">
                    <div class="stat">
                        <span class="stat-number">${this.extractedData.length}</span>
                        <span class="stat-label">Cards Processed</span>
                    </div>
                    <div class="stat">
                        <span class="stat-number">${emailsFound}</span>
                        <span class="stat-label">Emails Found</span>
                    </div>
                    <div class="stat">
                        <span class="stat-number">${phonesFound}</span>
                        <span class="stat-label">Phones Found</span>
                    </div>
                </div>
            `;
        }

        document.getElementById('downloadBtn').disabled = false;
        document.getElementById('clearBtn').disabled = false;
    }

    toggleCardDetails(index) {
        const content = document.getElementById(`card-${index}`);
        const icon = document.querySelector(`.result-card:nth-child(${index + 1}) .toggle-icon`);
        
        if (content.style.display === 'none') {
            content.style.display = 'block';
            icon.textContent = '▼';
        } else {
            content.style.display = 'none';
            icon.textContent = '▶';
        }
    }

    toggleRawText(index) {
        const rawContent = document.getElementById(`raw-${index}`);
        const button = rawContent.previousElementSibling;
        
        if (rawContent.style.display === 'none') {
            rawContent.style.display = 'block';
            button.textContent = 'Hide Raw OCR Text';
        } else {
            rawContent.style.display = 'none';
            button.textContent = 'View Raw OCR Text';
        }
    }

    updateField(cardIndex, field, value) {
        this.extractedData[cardIndex][field] = value;
        this.storeData();
    }

    showProgress(show) {
        const progressContainer = document.getElementById('progressContainer');
        if (progressContainer) {
            progressContainer.style.display = show ? 'block' : 'none';
        }
    }

    updateProgress(current, total, filename) {
        const progressBar = document.getElementById('progressBar');
        const statusText = document.getElementById('statusText');
        
        if (progressBar) {
            progressBar.style.width = `${(current / total) * 100}%`;
        }
        
        if (statusText) {
            statusText.textContent = `Processing ${current} of ${total}: ${filename}`;
        }
    }

    clearAll() {
        this.extractedData = [];
        document.getElementById('fileInput').value = '';
        document.getElementById('filePreview').innerHTML = '';
        document.getElementById('resultsContainer').innerHTML = '';
        document.getElementById('summaryContainer').innerHTML = '';
        document.getElementById('extractBtn').disabled = true;
        document.getElementById('downloadBtn').disabled = true;
        document.getElementById('clearBtn').disabled = true;
        localStorage.removeItem('businessCardData');
        this.showNotification('All data cleared', 'info');
    }

    downloadExcel() {
        // Create CSV content
        const headers = ['Name', 'Title', 'Company', 'Email', 'Phone', 'Address', 'Website'];
        const csvContent = [
            headers.join(','),
            ...this.extractedData.map(card => 
                headers.map(header => `"${card[header] || ''}"`).join(',')
            )
        ].join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'business_cards_extracted.csv';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showNotification('Excel file downloaded!', 'success');
    }

    storeData() {
        localStorage.setItem('businessCardData', JSON.stringify(this.extractedData));
    }

    loadStoredData() {
        const stored = localStorage.getItem('businessCardData');
        if (stored) {
            this.extractedData = JSON.parse(stored);
            if (this.extractedData.length > 0) {
                this.displayResults();
                document.getElementById('downloadBtn').disabled = false;
                document.getElementById('clearBtn').disabled = false;
            }
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (document.body.contains(notification)) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize the app when DOM is loaded
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new BusinessCardApp();
});
