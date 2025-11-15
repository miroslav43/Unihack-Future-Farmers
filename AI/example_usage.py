#!/usr/bin/env python3
"""Example usage of AI module"""
from processor import AIProcessor
from pathlib import Path


def example_ocr_processing():
    """Example: Process documents with OCR"""
    print("=" * 60)
    print("Example 1: OCR Document Processing")
    print("=" * 60)
    
    processor = AIProcessor()
    
    # Example paths (replace with actual files)
    example_docs = [
        {'file_path': 'examples/cni_sample.pdf', 'document_type': 'cni'},
        {'file_path': 'examples/certificate.pdf', 'document_type': 'certificate'},
        {'file_path': 'examples/parcel.pdf', 'document_type': 'parcel'},
    ]
    
    # Process CNI
    print("\n📄 Processing CNI document...")
    cni_path = 'examples/cni_sample.pdf'
    
    if Path(cni_path).exists():
        result = processor.process_document(cni_path, 'cni')
        
        if result['success']:
            data = result['data']
            print(f"✅ Success! Confidence: {data['confidence']:.2%}")
            print(f"Extracted CNP: {data['extracted_data'].get('cnp')}")
            print(f"Name: {data['extracted_data'].get('first_name')} {data['extracted_data'].get('last_name')}")
        else:
            print(f"❌ Error: {result['error']}")
    else:
        print(f"⚠️  File not found: {cni_path}")
        print("   Place sample documents in 'examples/' folder")


def example_chm_generation():
    """Example: Generate CHM document"""
    print("\n" + "=" * 60)
    print("Example 2: CHM Document Generation")
    print("=" * 60)
    
    processor = AIProcessor()
    
    # Sample data
    farmer_data = {
        'first_name': 'Ion',
        'last_name': 'Popescu',
        'cnp': '1800101123456',
        'email': 'ion@example.com',
        'phone': '0712345678',
        'age': 45,
        'experience_years': 20,
        'experience_level': 'advanced',
        'total_parcels': 3,
        'total_land_area': 15.5,
        'has_equipment': True,
        'has_irrigation': True,
        'has_storage': True,
        'county': 'Ilfov',
        'city': 'Bucuresti',
        'address': 'Str. Agricultorilor nr. 10'
    }
    
    assessment_data = {
        'overall_rating': 'excellent',
        'eligibility_score': 85,
        'bonitate_score': {
            'soil_quality': 85,
            'irrigation_access': 90,
            'location_score': 75,
            'infrastructure_score': 80,
            'overall_score': 82
        },
        'farmer_score': {
            'experience_score': 90,
            'education_score': 75,
            'equipment_score': 85,
            'financial_score': 70,
            'overall_score': 80
        },
        'risk_assessment': {
            'risk_level': 'low',
            'risk_factors': ['Limited financial reserves'],
            'mitigation_suggestions': ['Consider agricultural insurance'],
            'confidence_score': 0.87
        },
        'recommendations': [
            'Eligible for agricultural subsidies',
            'Consider expanding irrigation system',
            'Recommended for young farmer programs'
        ]
    }
    
    application_data = {
        'application_number': 'SUB-2024-ABC123',
        'application_type': 'subsidies',
        'requested_amount': 50000.0,
        'description': 'Cerere subventii pentru imbunatatirea sistemului de irigatii',
        'supporting_docs': [
            'documents/cni.pdf',
            'documents/ownership.pdf',
            'documents/parcel.pdf'
        ]
    }
    
    # Generate CHM
    print("\n📝 Generating CHM document...")
    output_path = 'output/CHM-2024-EXAMPLE.pdf'
    
    # Create output directory
    Path('output').mkdir(exist_ok=True)
    
    result = processor.generate_chm(
        output_path=output_path,
        farmer_data=farmer_data,
        assessment_data=assessment_data,
        application_data=application_data
    )
    
    if result['success']:
        print(f"✅ CHM generated successfully!")
        print(f"📁 File saved to: {result['file_path']}")
    else:
        print(f"❌ Error: {result['error']}")


def example_report_generation():
    """Example: Generate assessment report"""
    print("\n" + "=" * 60)
    print("Example 3: Assessment Report Generation")
    print("=" * 60)
    
    processor = AIProcessor()
    
    # Sample data (same as CHM example)
    farmer_data = {
        'first_name': 'Ion',
        'last_name': 'Popescu',
        'cnp': '1800101123456',
        'age': 45,
        'experience_years': 20,
        'experience_level': 'advanced',
        'total_parcels': 3,
        'total_land_area': 15.5,
        'has_equipment': True,
        'has_irrigation': True,
        'has_storage': True,
        'county': 'Ilfov',
        'city': 'Bucuresti',
    }
    
    assessment_data = {
        'overall_rating': 'excellent',
        'eligibility_score': 85,
        'bonitate_score': {
            'soil_quality': 85,
            'irrigation_access': 90,
            'location_score': 75,
            'infrastructure_score': 80,
            'overall_score': 82
        },
        'farmer_score': {
            'experience_score': 90,
            'education_score': 75,
            'equipment_score': 85,
            'financial_score': 70,
            'overall_score': 80
        },
        'risk_assessment': {
            'risk_level': 'low',
            'risk_factors': ['Limited financial reserves'],
            'mitigation_suggestions': ['Consider agricultural insurance'],
            'confidence_score': 0.87
        },
        'recommendations': [
            'Eligible for agricultural subsidies',
            'Consider expanding irrigation system'
        ]
    }
    
    # Generate report
    print("\n📊 Generating assessment report...")
    output_path = 'output/REPORT-2024-EXAMPLE.pdf'
    
    result = processor.generate_assessment_report(
        output_path=output_path,
        farmer_data=farmer_data,
        assessment_data=assessment_data
    )
    
    if result['success']:
        print(f"✅ Report generated successfully!")
        print(f"📁 File saved to: {result['file_path']}")
    else:
        print(f"❌ Error: {result['error']}")


def example_batch_processing():
    """Example: Batch process multiple documents"""
    print("\n" + "=" * 60)
    print("Example 4: Batch Document Processing")
    print("=" * 60)
    
    processor = AIProcessor()
    
    documents = [
        {'file_path': 'examples/cni1.pdf', 'document_type': 'cni'},
        {'file_path': 'examples/cni2.pdf', 'document_type': 'cni'},
        {'file_path': 'examples/cert1.pdf', 'document_type': 'certificate'},
    ]
    
    print(f"\n📦 Processing {len(documents)} documents...")
    results = processor.batch_process_documents(documents)
    
    success_count = sum(1 for r in results if r['success'])
    print(f"\n✅ Successfully processed: {success_count}/{len(documents)}")
    
    for i, result in enumerate(results, 1):
        if result['success']:
            print(f"  {i}. ✅ {result['file_path']}")
        else:
            print(f"  {i}. ❌ {result['file_path']} - {result.get('error', 'Unknown error')}")


def main():
    """Run all examples"""
    print("\n🌾 Farmer Assessment System - AI Module Examples\n")
    
    # Create examples and output directories
    Path('examples').mkdir(exist_ok=True)
    Path('output').mkdir(exist_ok=True)
    
    # Run examples
    try:
        example_ocr_processing()
    except Exception as e:
        print(f"Example 1 error: {e}")
    
    try:
        example_chm_generation()
    except Exception as e:
        print(f"Example 2 error: {e}")
    
    try:
        example_report_generation()
    except Exception as e:
        print(f"Example 3 error: {e}")
    
    try:
        example_batch_processing()
    except Exception as e:
        print(f"Example 4 error: {e}")
    
    print("\n" + "=" * 60)
    print("✨ Examples completed!")
    print("=" * 60)
    print("\n📝 Notes:")
    print("  - Place sample PDF documents in 'examples/' folder for OCR testing")
    print("  - Generated files are saved in 'output/' folder")
    print("  - Install Tesseract OCR for document processing to work")
    print("\n")


if __name__ == "__main__":
    main()
