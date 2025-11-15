"""CNI (Identity Card) document extractor"""
import re
from typing import Dict, Any, Optional
from .document_processor import DocumentProcessor


class CNIExtractor(DocumentProcessor):
    """Extract data from Romanian Identity Cards (CNI)"""
    
    def __init__(self, tesseract_path: Optional[str] = None):
        super().__init__(tesseract_path)
        
        # Define extraction patterns for Romanian CNI
        self.patterns = {
            'cnp': r'CNP[:\s]*(\d{13})',
            'last_name': r'(?:NUME|Nume)[:\s]*([A-ZĂÂÎȘȚ][A-ZĂÂÎȘȚa-zăâîșț\s\-]+)',
            'first_name': r'(?:PRENUME|Prenume)[:\s]*([A-ZĂÂÎȘȚ][A-ZĂÂÎȘȚa-zăâîșț\s\-]+)',
            'birth_date': r'(?:Data nașterii|DATA NAȘTERII|Născut)[:\s]*(\d{2}[\.\/\-]\d{2}[\.\/\-]\d{4})',
            'sex': r'(?:SEX|Sex)[:\s]*([MF])',
            'nationality': r'(?:Cetățenie|CETĂȚENIE)[:\s]*([A-ZĂÂÎȘȚa-zăâîșț]+)',
            'series': r'(?:Serie|SERIE)[:\s]*([A-Z]{2})',
            'number': r'(?:Nr\.|Număr)[:\s]*(\d{6,})',
            'issued_by': r'(?:Emis de|EMIS DE)[:\s]*([A-ZĂÂÎȘȚa-zăâîșț\s\-]+)',
            'valid_until': r'(?:Valabil până la|VALABIL)[:\s]*(\d{2}[\.\/\-]\d{2}[\.\/\-]\d{4})',
            'address': r'(?:Domiciliu|DOMICILIU|Adresa)[:\s]*([A-ZĂÂÎȘȚa-zăâîșț0-9\s\-,\.]+)'
        }
    
    def extract_cni_data(self, file_path: str) -> Dict[str, Any]:
        """
        Extract data from CNI document
        
        Args:
            file_path: Path to CNI document
            
        Returns:
            Dictionary with extracted CNI data
        """
        # Process document with OCR
        ocr_result = self.process_document(file_path, lang='ron+eng')
        text = ocr_result['text']
        
        # Clean text
        cleaned_text = self.clean_text(text)
        
        # Extract structured data
        extracted_data = self.extract_patterns(cleaned_text, self.patterns)
        
        # Post-process CNP
        if extracted_data.get('cnp'):
            cnp = re.sub(r'\D', '', extracted_data['cnp'])
            if len(cnp) == 13:
                extracted_data['cnp'] = cnp
            else:
                extracted_data['cnp'] = None
        
        # Validate and extract additional info from CNP
        if extracted_data.get('cnp'):
            cnp_info = self._parse_cnp(extracted_data['cnp'])
            extracted_data.update(cnp_info)
        
        # Standardize date formats
        if extracted_data.get('birth_date'):
            extracted_data['birth_date'] = self._standardize_date(extracted_data['birth_date'])
        
        if extracted_data.get('valid_until'):
            extracted_data['valid_until'] = self._standardize_date(extracted_data['valid_until'])
        
        return {
            'document_type': 'CNI',
            'confidence': ocr_result['confidence'],
            'extracted_data': extracted_data,
            'raw_text': cleaned_text
        }
    
    @staticmethod
    def _parse_cnp(cnp: str) -> Dict[str, Any]:
        """
        Parse additional information from CNP
        
        CNP format: SAALLZZJJNNNC
        S = sex (1,3,5,7=M; 2,4,6,8=F)
        AA = year of birth
        LL = month of birth
        ZZ = day of birth
        JJ = county code
        NNN = sequence number
        C = control digit
        """
        if not cnp or len(cnp) != 13:
            return {}
        
        try:
            sex_digit = int(cnp[0])
            sex = 'M' if sex_digit in [1, 3, 5, 7] else 'F'
            
            year = int(cnp[1:3])
            # Determine century based on first digit
            if sex_digit in [1, 2]:
                year += 1900
            elif sex_digit in [3, 4]:
                year += 1800
            elif sex_digit in [5, 6]:
                year += 2000
            
            month = int(cnp[3:5])
            day = int(cnp[5:7])
            county_code = cnp[7:9]
            
            return {
                'sex_from_cnp': sex,
                'birth_year': year,
                'birth_month': month,
                'birth_day': day,
                'county_code': county_code
            }
        except (ValueError, IndexError):
            return {}
    
    @staticmethod
    def _standardize_date(date_str: str) -> str:
        """Standardize date format to YYYY-MM-DD"""
        # Try different date formats
        patterns = [
            (r'(\d{2})[\.\/\-](\d{2})[\.\/\-](\d{4})', '{2}-{1}-{0}'),  # DD.MM.YYYY
            (r'(\d{4})[\.\/\-](\d{2})[\.\/\-](\d{2})', '{0}-{1}-{2}'),  # YYYY.MM.DD
        ]
        
        for pattern, format_str in patterns:
            match = re.match(pattern, date_str)
            if match:
                groups = match.groups()
                return format_str.format(*groups)
        
        return date_str
