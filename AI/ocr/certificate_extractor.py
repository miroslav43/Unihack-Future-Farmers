"""Agricultural certificate extractor"""
import re
from typing import Dict, Any, Optional
from .document_processor import DocumentProcessor


class CertificateExtractor(DocumentProcessor):
    """Extract data from agricultural certificates"""
    
    def __init__(self, tesseract_path: Optional[str] = None):
        super().__init__(tesseract_path)
        
        # Define extraction patterns for certificates
        self.patterns = {
            'certificate_number': r'(?:Nr\.|Număr)[:\s]*(\d+[\/\-]?\d*)',
            'issue_date': r'(?:Data emiterii|Emis la)[:\s]*(\d{2}[\.\/\-]\d{2}[\.\/\-]\d{4})',
            'valid_until': r'(?:Valabil până|Valid până)[:\s]*(\d{2}[\.\/\-]\d{2}[\.\/\-]\d{4})',
            'holder_name': r'(?:Titular|Beneficiar)[:\s]*([A-ZĂÂÎȘȚa-zăâîșț\s\-]+)',
            'holder_cnp': r'CNP[:\s]*(\d{13})',
            'certificate_type': r'(?:Tip certificat|Categorie)[:\s]*([A-ZĂÂÎȘȚa-zăâîșț\s\-]+)',
            'issued_by': r'(?:Emis de|Autoritate)[:\s]*([A-ZĂÂÎȘȚa-zăâîșț\s\-]+)',
            'area_hectares': r'(?:Suprafață|Arie)[:\s]*(\d+[,\.]?\d*)\s*(?:ha|hectare)',
            'parcel_id': r'(?:Parcel[aă]|ID parcel[aă])[:\s]*([A-Z0-9\-]+)',
        }
    
    def extract_certificate_data(self, file_path: str) -> Dict[str, Any]:
        """
        Extract data from agricultural certificate
        
        Args:
            file_path: Path to certificate document
            
        Returns:
            Dictionary with extracted certificate data
        """
        # Process document with OCR
        ocr_result = self.process_document(file_path, lang='ron+eng')
        text = ocr_result['text']
        
        # Clean text
        cleaned_text = self.clean_text(text)
        
        # Extract structured data
        extracted_data = self.extract_patterns(cleaned_text, self.patterns)
        
        # Post-process numeric values
        if extracted_data.get('area_hectares'):
            area = extracted_data['area_hectares'].replace(',', '.')
            try:
                extracted_data['area_hectares'] = float(area)
            except ValueError:
                extracted_data['area_hectares'] = None
        
        # Standardize dates
        for date_field in ['issue_date', 'valid_until']:
            if extracted_data.get(date_field):
                extracted_data[date_field] = self._standardize_date(extracted_data[date_field])
        
        # Determine certificate validity
        extracted_data['is_valid'] = self._check_validity(extracted_data.get('valid_until'))
        
        return {
            'document_type': 'CERTIFICATE',
            'confidence': ocr_result['confidence'],
            'extracted_data': extracted_data,
            'raw_text': cleaned_text
        }
    
    @staticmethod
    def _standardize_date(date_str: str) -> str:
        """Standardize date format to YYYY-MM-DD"""
        patterns = [
            (r'(\d{2})[\.\/\-](\d{2})[\.\/\-](\d{4})', '{2}-{1}-{0}'),
            (r'(\d{4})[\.\/\-](\d{2})[\.\/\-](\d{2})', '{0}-{1}-{2}'),
        ]
        
        for pattern, format_str in patterns:
            match = re.match(pattern, date_str)
            if match:
                groups = match.groups()
                return format_str.format(*groups)
        
        return date_str
    
    @staticmethod
    def _check_validity(valid_until: Optional[str]) -> bool:
        """Check if certificate is still valid"""
        if not valid_until:
            return False
        
        try:
            from datetime import datetime
            valid_date = datetime.strptime(valid_until, '%Y-%m-%d')
            return valid_date >= datetime.now()
        except (ValueError, TypeError):
            return False
