"""Base document processor with OCR capabilities"""
import cv2
import numpy as np
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from pathlib import Path
from typing import Dict, Any, Optional, List
import re


class DocumentProcessor:
    """Base class for OCR document processing"""
    
    def __init__(self, tesseract_path: Optional[str] = None):
        """
        Initialize document processor
        
        Args:
            tesseract_path: Optional path to Tesseract executable
        """
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        self.supported_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.bmp'}
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR results
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Preprocessed image
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Apply adaptive thresholding
        binary = cv2.adaptiveThreshold(
            denoised,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        
        # Apply dilation and erosion to remove noise
        kernel = np.ones((1, 1), np.uint8)
        processed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        return processed
    
    def extract_text_from_image(
        self,
        image: np.ndarray,
        lang: str = 'ron+eng'
    ) -> tuple[str, float]:
        """
        Extract text from image using OCR
        
        Args:
            image: Input image
            lang: Language for OCR (default: Romanian + English)
            
        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        # Preprocess image
        processed = self.preprocess_image(image)
        
        # Perform OCR with confidence data
        data = pytesseract.image_to_data(
            processed,
            lang=lang,
            output_type=pytesseract.Output.DICT
        )
        
        # Extract text and calculate average confidence
        text_parts = []
        confidences = []
        
        for i, word in enumerate(data['text']):
            if word.strip():
                text_parts.append(word)
                conf = float(data['conf'][i])
                if conf > 0:  # Only include valid confidence scores
                    confidences.append(conf)
        
        text = ' '.join(text_parts)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return text, avg_confidence / 100  # Normalize to 0-1
    
    def load_document(self, file_path: str) -> List[np.ndarray]:
        """
        Load document and convert to images
        
        Args:
            file_path: Path to document file
            
        Returns:
            List of images (one per page)
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if path.suffix.lower() not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {path.suffix}")
        
        images = []
        
        if path.suffix.lower() == '.pdf':
            # Convert PDF to images
            pil_images = convert_from_path(str(path), dpi=300)
            for pil_img in pil_images:
                images.append(np.array(pil_img))
        else:
            # Load image directly
            img = cv2.imread(str(path))
            if img is None:
                raise ValueError(f"Failed to load image: {file_path}")
            images.append(img)
        
        return images
    
    def process_document(
        self,
        file_path: str,
        lang: str = 'ron+eng'
    ) -> Dict[str, Any]:
        """
        Process document and extract text
        
        Args:
            file_path: Path to document
            lang: Language for OCR
            
        Returns:
            Dictionary with extracted data
        """
        images = self.load_document(file_path)
        
        all_text = []
        all_confidences = []
        
        for image in images:
            text, confidence = self.extract_text_from_image(image, lang)
            all_text.append(text)
            all_confidences.append(confidence)
        
        combined_text = '\n'.join(all_text)
        avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0
        
        return {
            'text': combined_text,
            'confidence': avg_confidence,
            'page_count': len(images),
            'file_path': file_path
        }
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean extracted text"""
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep Romanian diacritics
        text = re.sub(r'[^\w\s\-.,;:ăâîșțĂÂÎȘȚ]', '', text)
        
        return text.strip()
    
    @staticmethod
    def extract_patterns(text: str, patterns: Dict[str, str]) -> Dict[str, Optional[str]]:
        """
        Extract data using regex patterns
        
        Args:
            text: Text to search
            patterns: Dictionary of {field_name: regex_pattern}
            
        Returns:
            Dictionary of extracted data
        """
        results = {}
        
        for field, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            results[field] = match.group(1).strip() if match else None
        
        return results
