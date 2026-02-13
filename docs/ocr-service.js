// Real OCR Service for GitHub Pages Deployment
class OCRService {
    constructor() {
        // Using free OCR APIs that work from browser
        this.ocrSpaceApiKey = null; // Users can add their own API key
        this.ocrApiEndpoint = 'https://api.ocr.space/parse/image';
    }

    // Method to extract text from image using free OCR API
    async extractTextFromImage(imageFile) {
        try {
            // Try OCR.space API (free tier, 500 requests/month)
            if (this.ocrSpaceApiKey) {
                const result = await this.extractWithOCRSpace(imageFile);
                if (result) return result;
            }

            // Fallback to Tesseract.js (runs in browser)
            return await this.extractWithTesseract(imageFile);
        } catch (error) {
            console.error('OCR extraction failed:', error);
            throw new Error('Failed to extract text from image');
        }
    }

    // OCR.space API integration
    async extractWithOCRSpace(imageFile) {
        const formData = new FormData();
        formData.append('file', imageFile);
        formData.append('apikey', this.ocrSpaceApiKey);
        formData.append('language', 'eng');
        formData.append('isOverlayRequired', false);
        formData.append('detectOrientation', true);
        formData.append('scale', true);
        formData.append('OCREngine', 2);

        const response = await fetch(this.ocrApiEndpoint, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        
        if (result.IsErroredOnProcessing) {
            throw new Error(result.ErrorMessage || 'OCR processing failed');
        }

        return result.ParsedResults[0]?.ParsedText || '';
    }

    // Tesseract.js (runs entirely in browser)
    async extractWithTesseract(imageFile) {
        // Dynamically load Tesseract.js
        if (!window.Tesseract) {
            await this.loadTesseract();
        }

        const result = await window.Tesseract.recognize(
            imageFile,
            'eng',
            {
                logger: (m) => {
                    if (m.status === 'recognizing text') {
                        console.log(`OCR Progress: ${Math.round(m.progress * 100)}%`);
                    }
                }
            }
        );

        return result.data.text;
    }

    // Load Tesseract.js library
    async loadTesseract() {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/tesseract.js@4/dist/tesseract.min.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    // Set API key for OCR.space
    setAPIKey(apiKey) {
        this.ocrSpaceApiKey = apiKey;
        localStorage.setItem('ocr_api_key', apiKey);
    }

    // Get stored API key
    getAPIKey() {
        return this.ocrSpaceApiKey || localStorage.getItem('ocr_api_key');
    }

    // Extract entities from OCR text
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
        
        // Enhanced regex patterns for better extraction
        const patterns = {
            email: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/i,
            phone: /(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})/g,
            website: /(?:https?:\/\/)?(?:www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:\/[^\s]*)?/g,
            address: /\d+\s+[\w\s]+\s+(?:Street|St|Avenue|Ave|Boulevard|Blvd|Lane|Ln|Road|Rd|Drive|Dr|Court|Ct|Way|Place|Pl)\s*[\w\s]*/gi,
            title: /\b(?:CEO|CTO|CFO|President|Vice President|Director|Manager|Engineer|Developer|Designer|Consultant|Analyst|Coordinator|Specialist|Administrator|Assistant|Associate|Partner|Founder|Owner|Lead|Senior|Junior|Principal)\b/gi
        };

        // Extract entities using patterns
        lines.forEach((line, index) => {
            // Email extraction
            if (!entities.Email && patterns.email.test(line)) {
                entities.Email = line.match(patterns.email)[0];
            }
            // Phone extraction
            else if (!entities.Phone && patterns.phone.test(line)) {
                const phoneMatch = line.match(patterns.phone);
                if (phoneMatch) {
                    entities.Phone = phoneMatch[0];
                }
            }
            // Website extraction
            else if (!entities.Website && patterns.website.test(line)) {
                const websiteMatch = line.match(patterns.website);
                if (websiteMatch) {
                    entities.Website = websiteMatch[0].replace(/^https?:\/\//, '');
                }
            }
            // Address extraction
            else if (!entities.Address && patterns.address.test(line)) {
                entities.Address = line;
            }
            // Title extraction
            else if (!entities.Title && patterns.title.test(line)) {
                entities.Title = line;
            }
            // Company extraction (heuristic)
            else if (!entities.Company && this.looksLikeCompany(line)) {
                entities.Company = line;
            }
            // Name extraction (heuristic - usually first 2-3 words)
            else if (!entities.Name && index < 3 && line.split(' ').length >= 2 && line.split(' ').length <= 4 && !patterns.email.test(line)) {
                entities.Name = line;
            }
        });

        return entities;
    }

    // Helper method to identify company names
    looksLikeCompany(text) {
        const companyIndicators = [
            'Inc', 'Corp', 'LLC', 'Ltd', 'Co', 'Company', 'Corporation', 
            'Incorporated', 'Limited', 'LLC', 'LP', 'PLC', 'Group', 'Holdings',
            'Enterprises', 'Solutions', 'Technologies', 'Systems', 'Services',
            'Consulting', 'Agency', 'Studio', 'Labs', 'Ventures', 'Partners'
        ];
        
        return companyIndicators.some(indicator => 
            text.toLowerCase().includes(indicator.toLowerCase())
        );
    }
}

// Export for use in main app
window.OCRService = OCRService;
