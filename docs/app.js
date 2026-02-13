// Business Card Intelligence - Static Web App
class BusinessCardApp {
    constructor() {
        this.extractedData = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadStoredData();
    }

    setupEventListeners() {
        const fileInput = document.getElementById('fileInput');
        const extractBtn = document.getElementById('extractBtn');
        const clearBtn = document.getElementById('clearBtn');
        const downloadBtn = document.getElementById('downloadBtn');

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
                // Simulate OCR processing (in real app, this would call OCR service)
                const extractedText = await this.simulateOCR(file);
                const entities = this.extractEntities(extractedText);
                
                entities._source_file = file.name;
                entities._raw_text = extractedText;
                this.extractedData.push(entities);
                
                await this.delay(500); // Simulate processing time
            } catch (error) {
                console.error(`Error processing ${file.name}:`, error);
                this.showNotification(`Error processing ${file.name}`, 'error');
            }
        }

        this.displayResults();
        this.showProgress(false);
        this.showNotification('Processing complete!', 'success');
        this.storeData();
    }

    async simulateOCR(file) {
        // Simulate OCR text extraction
        // In a real implementation, this would call an OCR API
        const sampleTexts = [
            `John Doe
Software Engineer
Tech Company Inc.
john.doe@techcompany.com
+1 (555) 123-4567
123 Tech Street, Silicon Valley, CA 94000
www.techcompany.com`,

            `Jane Smith
Marketing Director
Creative Agency
jane.smith@creative.com
+1 (555) 987-6543
456 Design Ave, New York, NY 10001`,

            `Robert Johnson
CEO
Startup Ventures
robert.j@startup.io
+1 (555) 246-8135
789 Innovation Blvd, Austin, TX 73301
www.startup.io`
        ];
        
        return sampleTexts[Math.floor(Math.random() * sampleTexts.length)];
    }

    extractEntities(text) {
        const entities = {
            Name: '',
            Title: '',
            Company: '',
            Email: '',
            Phone: '',
            Address: '',
            Website: ''
        };

        const lines = text.split('\n').map(line => line.trim()).filter(line => line);
        
        // Simple regex-based entity extraction
        lines.forEach(line => {
            // Email
            if (!entities.Email && line.match(/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/)) {
                entities.Email = line;
            }
            // Phone
            else if (!entities.Phone && line.match(/[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}/)) {
                entities.Phone = line;
            }
            // Website
            else if (!entities.Website && line.match(/^www\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/)) {
                entities.Website = line;
            }
            // Name (usually first line)
            else if (!entities.Name && line.split(' ').length >= 2 && line.length < 30) {
                entities.Name = line;
            }
            // Title (usually contains common title keywords)
            else if (!entities.Title && (line.includes('Engineer') || line.includes('Manager') || line.includes('Director') || line.includes('CEO') || line.includes('Developer') || line.includes('Designer'))) {
                entities.Title = line;
            }
            // Company (usually contains Inc, Corp, LLC, etc.)
            else if (!entities.Company && (line.includes('Inc') || line.includes('Corp') || line.includes('LLC') || line.includes('Company') || line.includes('Agency'))) {
                entities.Company = line;
            }
            // Address (usually contains street, city, state)
            else if (!entities.Address && (line.match(/\d+\s+\w+\s+(Street|St|Ave|Avenue|Blvd|Boulevard)/) || line.match(/^[A-Z][a-z]+,\s+[A-Z]{2}\s+\d{5}$/))) {
                entities.Address = line;
            }
        });

        return entities;
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
                            <pre>${card._raw_text}</pre>
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
        // Create CSV content (simplified Excel format)
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
                document.body.removeChild(notification);
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
