"""Main AI processor - integrates OCR and document generation"""
from typing import Dict, Any, Optional
from pathlib import Path

from ocr.cni_extractor import CNIExtractor
from ocr.certificate_extractor import CertificateExtractor
from ocr.parcel_extractor import ParcelExtractor
from document_generation.chm_generator import CHMGenerator
from document_generation.report_generator import ReportGenerator


class AIProcessor:
    """Main AI processor for document processing and generation"""
    
    def __init__(self, tesseract_path: Optional[str] = None):
        """
        Initialize AI processor
        
        Args:
            tesseract_path: Optional path to Tesseract executable
        """
        self.cni_extractor = CNIExtractor(tesseract_path)
        self.certificate_extractor = CertificateExtractor(tesseract_path)
        self.parcel_extractor = ParcelExtractor(tesseract_path)
        self.chm_generator = CHMGenerator()
        self.report_generator = ReportGenerator()
    
    def process_document(
        self,
        file_path: str,
        document_type: str
    ) -> Dict[str, Any]:
        """
        Process a document based on its type
        
        Args:
            file_path: Path to the document
            document_type: Type of document ('cni', 'certificate', 'parcel', etc.)
            
        Returns:
            Dictionary with extracted data and confidence
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"Document not found: {file_path}")
        
        document_type = document_type.lower()
        
        try:
            if document_type == 'cni':
                result = self.cni_extractor.extract_cni_data(file_path)
            elif document_type == 'certificate':
                result = self.certificate_extractor.extract_certificate_data(file_path)
            elif document_type in ['parcel', 'cadastral']:
                result = self.parcel_extractor.extract_parcel_data(file_path)
            else:
                # Generic document processing
                from ocr.document_processor import DocumentProcessor
                processor = DocumentProcessor(self.cni_extractor.tesseract_path)
                ocr_result = processor.process_document(file_path)
                result = {
                    'document_type': 'OTHER',
                    'confidence': ocr_result['confidence'],
                    'extracted_data': {'text': ocr_result['text']},
                    'raw_text': ocr_result['text']
                }
            
            return {
                'success': True,
                'data': result
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': None
            }
    
    def generate_chm(
        self,
        output_path: str,
        farmer_data: Dict[str, Any],
        assessment_data: Dict[str, Any],
        application_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate CHM document
        
        Args:
            output_path: Path where PDF will be saved
            farmer_data: Farmer information
            assessment_data: Assessment data
            application_data: Application details
            
        Returns:
            Dictionary with generation result
        """
        try:
            generated_path = self.chm_generator.generate_chm(
                output_path,
                farmer_data,
                assessment_data,
                application_data
            )
            
            return {
                'success': True,
                'file_path': generated_path,
                'message': 'CHM document generated successfully'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'file_path': None
            }
    
    def generate_assessment_report(
        self,
        output_path: str,
        farmer_data: Dict[str, Any],
        assessment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate assessment report
        
        Args:
            output_path: Path where PDF will be saved
            farmer_data: Farmer information
            assessment_data: Assessment data
            
        Returns:
            Dictionary with generation result
        """
        try:
            generated_path = self.report_generator.generate_assessment_report(
                output_path,
                farmer_data,
                assessment_data
            )
            
            return {
                'success': True,
                'file_path': generated_path,
                'message': 'Assessment report generated successfully'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'file_path': None
            }
    
    def batch_process_documents(
        self,
        documents: list[Dict[str, str]]
    ) -> list[Dict[str, Any]]:
        """
        Process multiple documents in batch
        
        Args:
            documents: List of dicts with 'file_path' and 'document_type'
            
        Returns:
            List of processing results
        """
        results = []
        
        for doc in documents:
            file_path = doc.get('file_path')
            doc_type = doc.get('document_type')
            
            if not file_path or not doc_type:
                results.append({
                    'success': False,
                    'error': 'Missing file_path or document_type',
                    'file_path': file_path
                })
                continue
            
            result = self.process_document(file_path, doc_type)
            result['file_path'] = file_path
            results.append(result)
        
        return results


# Convenience function for quick processing
def process_farmer_documents(
    cni_path: str,
    certificate_path: Optional[str] = None,
    parcel_path: Optional[str] = None,
    tesseract_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process all farmer documents at once
    
    Args:
        cni_path: Path to CNI document
        certificate_path: Optional path to certificate
        parcel_path: Optional path to parcel document
        tesseract_path: Optional Tesseract path
        
    Returns:
        Combined results
    """
    processor = AIProcessor(tesseract_path)
    
    results = {
        'cni': processor.process_document(cni_path, 'cni')
    }
    
    if certificate_path:
        results['certificate'] = processor.process_document(certificate_path, 'certificate')
    
    if parcel_path:
        results['parcel'] = processor.process_document(parcel_path, 'parcel')
    
    return results
