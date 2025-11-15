"""CHM (Agricultural application) document generator"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from datetime import datetime
from typing import Dict, Any
from pathlib import Path


class CHMGenerator:
    """Generate CHM (Cerere de Plată) documents"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='BodyText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            spaceAfter=6,
            alignment=TA_JUSTIFY
        ))
    
    def generate_chm(
        self,
        output_path: str,
        farmer_data: Dict[str, Any],
        assessment_data: Dict[str, Any],
        application_data: Dict[str, Any]
    ) -> str:
        """
        Generate CHM document
        
        Args:
            output_path: Path where PDF will be saved
            farmer_data: Farmer information
            assessment_data: Assessment and scoring data
            application_data: Application details
            
        Returns:
            Path to generated PDF
        """
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Build document content
        story = []
        
        # Header
        story.extend(self._build_header(application_data))
        
        # Farmer information section
        story.extend(self._build_farmer_section(farmer_data))
        
        # Assessment section
        story.extend(self._build_assessment_section(assessment_data))
        
        # Application details section
        story.extend(self._build_application_section(application_data))
        
        # Supporting documents section
        story.extend(self._build_documents_section(application_data))
        
        # Declaration and signature
        story.extend(self._build_declaration_section(farmer_data))
        
        # Build PDF
        doc.build(story)
        
        return output_path
    
    def _build_header(self, application_data: Dict[str, Any]) -> list:
        """Build document header"""
        elements = []
        
        # Title
        title = Paragraph(
            "CERERE DE FINANȚARE AGRICOLĂ",
            self.styles['CustomTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.5*cm))
        
        # Application number and date
        app_number = application_data.get('application_number', 'N/A')
        app_type = application_data.get('application_type', 'N/A').upper()
        date_str = datetime.now().strftime('%d.%m.%Y')
        
        info_text = f"<b>Număr cerere:</b> {app_number}<br/>"
        info_text += f"<b>Tip cerere:</b> {app_type}<br/>"
        info_text += f"<b>Data depunerii:</b> {date_str}"
        
        info_para = Paragraph(info_text, self.styles['BodyText'])
        elements.append(info_para)
        elements.append(Spacer(1, 0.8*cm))
        
        return elements
    
    def _build_farmer_section(self, farmer_data: Dict[str, Any]) -> list:
        """Build farmer information section"""
        elements = []
        
        # Section header
        header = Paragraph("I. DATELE SOLICITANTULUI", self.styles['SectionHeader'])
        elements.append(header)
        
        # Farmer data table
        data = [
            ['Nume și prenume:', f"{farmer_data.get('last_name', '')} {farmer_data.get('first_name', '')}"],
            ['CNP:', farmer_data.get('cnp', 'N/A')],
            ['Vârstă:', f"{farmer_data.get('age', 'N/A')} ani"],
            ['Email:', farmer_data.get('email', 'N/A')],
            ['Telefon:', farmer_data.get('phone', 'N/A')],
            ['Județ:', farmer_data.get('county', 'N/A')],
            ['Localitate:', farmer_data.get('city', 'N/A')],
            ['Adresă:', farmer_data.get('address', 'N/A')],
        ]
        
        table = Table(data, colWidths=[5*cm, 12*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.5*cm))
        
        # Agricultural experience
        exp_text = f"<b>Experiență agricolă:</b> {farmer_data.get('experience_years', 0)} ani "
        exp_text += f"({farmer_data.get('experience_level', 'N/A')})<br/>"
        exp_text += f"<b>Suprafață totală:</b> {farmer_data.get('total_land_area', 0)} ha<br/>"
        exp_text += f"<b>Număr parcele:</b> {farmer_data.get('total_parcels', 0)}<br/>"
        
        resources = []
        if farmer_data.get('has_equipment'):
            resources.append('Echipament agricol')
        if farmer_data.get('has_irrigation'):
            resources.append('Sistem de irigații')
        if farmer_data.get('has_storage'):
            resources.append('Spații de depozitare')
        
        exp_text += f"<b>Resurse:</b> {', '.join(resources) if resources else 'Niciuna'}"
        
        exp_para = Paragraph(exp_text, self.styles['BodyText'])
        elements.append(exp_para)
        elements.append(Spacer(1, 0.8*cm))
        
        return elements
    
    def _build_assessment_section(self, assessment_data: Dict[str, Any]) -> list:
        """Build assessment section"""
        elements = []
        
        # Section header
        header = Paragraph("II. EVALUARE ȘI SCORING", self.styles['SectionHeader'])
        elements.append(header)
        
        # Overall rating
        rating = assessment_data.get('overall_rating', 'N/A').upper()
        eligibility = assessment_data.get('eligibility_score', 0)
        
        rating_text = f"<b>Rating general:</b> {rating}<br/>"
        rating_text += f"<b>Scor eligibilitate:</b> {eligibility}/100"
        
        rating_para = Paragraph(rating_text, self.styles['BodyText'])
        elements.append(rating_para)
        elements.append(Spacer(1, 0.3*cm))
        
        # Bonitate scores
        bonitate = assessment_data.get('bonitate_score', {})
        farmer_score = assessment_data.get('farmer_score', {})
        
        scores_data = [
            ['CRITERII', 'PUNCTAJ'],
            ['Bonitate sol', f"{bonitate.get('overall_score', 0)}/100"],
            ['Experiență fermier', f"{farmer_score.get('overall_score', 0)}/100"],
            ['Infrastructură', f"{bonitate.get('infrastructure_score', 0)}/100"],
            ['Resurse', f"{farmer_score.get('equipment_score', 0)}/100"],
        ]
        
        scores_table = Table(scores_data, colWidths=[10*cm, 7*cm])
        scores_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(scores_table)
        elements.append(Spacer(1, 0.5*cm))
        
        # Recommendations
        recommendations = assessment_data.get('recommendations', [])
        if recommendations:
            rec_text = "<b>Recomandări:</b><br/>"
            for i, rec in enumerate(recommendations[:5], 1):
                rec_text += f"{i}. {rec}<br/>"
            
            rec_para = Paragraph(rec_text, self.styles['BodyText'])
            elements.append(rec_para)
        
        elements.append(Spacer(1, 0.8*cm))
        
        return elements
    
    def _build_application_section(self, application_data: Dict[str, Any]) -> list:
        """Build application details section"""
        elements = []
        
        # Section header
        header = Paragraph("III. DETALII CERERE", self.styles['SectionHeader'])
        elements.append(header)
        
        # Application details
        app_type = application_data.get('application_type', 'N/A')
        amount = application_data.get('requested_amount', 0)
        description = application_data.get('description', 'N/A')
        
        details_text = f"<b>Tip finanțare:</b> {app_type}<br/>"
        details_text += f"<b>Suma solicitată:</b> {amount:,.2f} RON<br/>"
        details_text += f"<b>Descriere:</b> {description}"
        
        details_para = Paragraph(details_text, self.styles['BodyText'])
        elements.append(details_para)
        elements.append(Spacer(1, 0.8*cm))
        
        return elements
    
    def _build_documents_section(self, application_data: Dict[str, Any]) -> list:
        """Build supporting documents section"""
        elements = []
        
        # Section header
        header = Paragraph("IV. DOCUMENTE ANEXATE", self.styles['SectionHeader'])
        elements.append(header)
        
        docs = application_data.get('supporting_docs', [])
        if docs:
            docs_text = ""
            for i, doc in enumerate(docs, 1):
                doc_name = Path(doc).name
                docs_text += f"{i}. {doc_name}<br/>"
        else:
            docs_text = "Niciun document anexat"
        
        docs_para = Paragraph(docs_text, self.styles['BodyText'])
        elements.append(docs_para)
        elements.append(Spacer(1, 0.8*cm))
        
        return elements
    
    def _build_declaration_section(self, farmer_data: Dict[str, Any]) -> list:
        """Build declaration and signature section"""
        elements = []
        
        # Section header
        header = Paragraph("V. DECLARAȚIE ȘI SEMNĂTURĂ", self.styles['SectionHeader'])
        elements.append(header)
        
        # Declaration text
        declaration = """
        Subsemnatul/Subsemnata, declar pe propria răspundere că informațiile furnizate în 
        prezenta cerere sunt corecte și complete. Înțeleg că furnizarea de informații false 
        poate duce la respingerea cererii și la consecințe legale.
        """
        
        decl_para = Paragraph(declaration, self.styles['BodyText'])
        elements.append(decl_para)
        elements.append(Spacer(1, 1*cm))
        
        # Signature section
        date_str = datetime.now().strftime('%d.%m.%Y')
        name = f"{farmer_data.get('last_name', '')} {farmer_data.get('first_name', '')}"
        
        sig_data = [
            ['Data:', date_str, 'Semnătura:', '________________________'],
            ['Numele:', name, '', '']
        ]
        
        sig_table = Table(sig_data, colWidths=[2*cm, 6*cm, 2*cm, 7*cm])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(sig_table)
        
        return elements
