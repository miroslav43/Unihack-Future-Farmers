"""Parcel/cadastral document extractor"""
import re
from typing import Dict, Any, Optional
from .document_processor import DocumentProcessor


class ParcelExtractor(DocumentProcessor):
    """Extract data from parcel and cadastral documents"""
    
    def __init__(self, tesseract_path: Optional[str] = None):
        super().__init__(tesseract_path)
        
        # Define extraction patterns for parcel documents
        self.patterns = {
            'parcel_number': r'(?:Nr\.\s*parcel[aă]|Parcel[aă])[:\s]*([0-9A-Z\-\/]+)',
            'cadastral_number': r'(?:Nr\.\s*cadastral|Cadastral)[:\s]*([0-9A-Z\-\/]+)',
            'area_hectares': r'(?:Suprafața|Arie)[:\s]*(\d+[,\.]?\d*)\s*(?:ha|hectare|mp|m²)',
            'owner_name': r'(?:Proprietar|Titular)[:\s]*([A-ZĂÂÎȘȚa-zăâîșț\s\-]+)',
            'owner_cnp': r'CNP[:\s]*(\d{13})',
            'location': r'(?:Locație|Amplasament|Adres[aă])[:\s]*([A-ZĂÂÎȘȚa-zăâîșț0-9\s\-,\.]+)',
            'county': r'(?:Județ|County)[:\s]*([A-ZĂÂÎȘȚa-zăâîșț\s\-]+)',
            'city': r'(?:Oraș|Localitate|Comună)[:\s]*([A-ZĂÂÎȘȚa-zăâîșț\s\-]+)',
            'land_use': r'(?:Destinație|Folosință)[:\s]*([A-ZĂÂÎȘȚa-zăâîșț\s\-]+)',
            'soil_class': r'(?:Clas[aă]\s*sol|Bonitate)[:\s]*([IVX0-9]+)',
            'topo_number': r'(?:Nr\.\s*topografic|Topografic)[:\s]*([0-9A-Z\-\/]+)',
        }
    
    def extract_parcel_data(self, file_path: str) -> Dict[str, Any]:
        """
        Extract data from parcel/cadastral document
        
        Args:
            file_path: Path to parcel document
            
        Returns:
            Dictionary with extracted parcel data
        """
        # Process document with OCR
        ocr_result = self.process_document(file_path, lang='ron+eng')
        text = ocr_result['text']
        
        # Clean text
        cleaned_text = self.clean_text(text)
        
        # Extract structured data
        extracted_data = self.extract_patterns(cleaned_text, self.patterns)
        
        # Post-process area
        if extracted_data.get('area_hectares'):
            area_str = extracted_data['area_hectares'].replace(',', '.')
            try:
                area_value = float(area_str)
                
                # Check if it's in square meters and convert to hectares
                if 'mp' in text or 'm²' in text:
                    area_value = area_value / 10000  # Convert m² to ha
                
                extracted_data['area_hectares'] = round(area_value, 4)
            except ValueError:
                extracted_data['area_hectares'] = None
        
        # Extract coordinates if present
        coordinates = self._extract_coordinates(cleaned_text)
        if coordinates:
            extracted_data['coordinates'] = coordinates
        
        # Convert soil class to numeric bonitate score
        if extracted_data.get('soil_class'):
            extracted_data['bonitate_score'] = self._soil_class_to_score(
                extracted_data['soil_class']
            )
        
        return {
            'document_type': 'PARCEL',
            'confidence': ocr_result['confidence'],
            'extracted_data': extracted_data,
            'raw_text': cleaned_text
        }
    
    @staticmethod
    def _extract_coordinates(text: str) -> Optional[Dict[str, float]]:
        """Extract GPS coordinates if present"""
        # Pattern for coordinates: 44.123456, 26.123456
        pattern = r'(\d{2}\.\d+)[,\s]+(\d{2}\.\d+)'
        match = re.search(pattern, text)
        
        if match:
            try:
                lat = float(match.group(1))
                lon = float(match.group(2))
                
                # Validate coordinates are in Romania range
                if 43 <= lat <= 48 and 20 <= lon <= 30:
                    return {'latitude': lat, 'longitude': lon}
            except ValueError:
                pass
        
        return None
    
    @staticmethod
    def _soil_class_to_score(soil_class: str) -> int:
        """
        Convert Romanian soil class (I-V) to numeric score (1-100)
        
        Soil classes in Romania:
        - Clasa I: 80-100 points (best quality)
        - Clasa II: 60-79 points
        - Clasa III: 40-59 points
        - Clasa IV: 20-39 points
        - Clasa V: 1-19 points (poorest quality)
        """
        # Convert Roman numerals to numeric
        roman_map = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5}
        
        # Try to extract Roman numeral
        for roman, value in roman_map.items():
            if roman in soil_class.upper():
                # Convert to score (inverse - class I is best)
                score_map = {1: 90, 2: 70, 3: 50, 4: 30, 5: 15}
                return score_map.get(value, 50)
        
        # Try numeric extraction
        numbers = re.findall(r'\d+', soil_class)
        if numbers:
            class_num = int(numbers[0])
            if 1 <= class_num <= 5:
                score_map = {1: 90, 2: 70, 3: 50, 4: 30, 5: 15}
                return score_map.get(class_num, 50)
        
        return 50  # Default middle score if unable to determine
