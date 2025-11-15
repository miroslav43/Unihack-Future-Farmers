"""Report generator for assessment reports"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from datetime import datetime
from typing import Dict, Any
from pathlib import Path


class ReportGenerator:
    """Generate assessment and analysis reports"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='ReportSection',
            parent=self.styles['Heading2'],
            fontSize=13,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=15,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        ))
    
    def generate_assessment_report(
        self,
        output_path: str,
        farmer_data: Dict[str, Any],
        assessment_data: Dict[str, Any]
    ) -> str:
        """
        Generate comprehensive assessment report
        
        Args:
            output_path: Path where PDF will be saved
            farmer_data: Farmer information
            assessment_data: Assessment and scoring data
            
        Returns:
            Path to generated PDF
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # Title
        title = Paragraph("RAPORT DE EVALUARE AGRICOLĂ", self.styles['ReportTitle'])
        story.append(title)
        story.append(Spacer(1, 0.5*cm))
        
        # Date
        date_str = datetime.now().strftime('%d.%m.%Y')
        date_para = Paragraph(f"<b>Data raportului:</b> {date_str}", self.styles['Normal'])
        story.append(date_para)
        story.append(Spacer(1, 1*cm))
        
        # Executive Summary
        story.extend(self._build_executive_summary(assessment_data))
        
        # Farmer Profile
        story.extend(self._build_farmer_profile(farmer_data))
        
        # Detailed Assessment
        story.extend(self._build_detailed_assessment(assessment_data))
        
        # Recommendations
        story.extend(self._build_recommendations_section(assessment_data))
        
        # Build PDF
        doc.build(story)
        
        return output_path
    
    def _build_executive_summary(self, assessment_data: Dict[str, Any]) -> list:
        """Build executive summary section"""
        elements = []
        
        header = Paragraph("REZUMAT EXECUTIV", self.styles['ReportSection'])
        elements.append(header)
        
        rating = assessment_data.get('overall_rating', 'N/A').upper()
        eligibility = assessment_data.get('eligibility_score', 0)
        risk = assessment_data.get('risk_assessment', {})
        risk_level = risk.get('risk_level', 'N/A').upper()
        
        summary_text = f"""
        <b>Rating General:</b> {rating}<br/>
        <b>Scor Eligibilitate:</b> {eligibility}/100<br/>
        <b>Nivel Risc:</b> {risk_level}<br/>
        <b>Recomandare:</b> {'APROBAT pentru finanțare' if eligibility >= 70 else 'NECESITĂ îmbunătățiri'}
        """
        
        summary_para = Paragraph(summary_text, self.styles['Normal'])
        elements.append(summary_para)
        elements.append(Spacer(1, 0.8*cm))
        
        return elements
    
    def _build_farmer_profile(self, farmer_data: Dict[str, Any]) -> list:
        """Build farmer profile section"""
        elements = []
        
        header = Paragraph("PROFILUL FERMIERULUI", self.styles['ReportSection'])
        elements.append(header)
        
        profile_data = [
            ['Nume:', f"{farmer_data.get('last_name', '')} {farmer_data.get('first_name', '')}"],
            ['Vârstă:', f"{farmer_data.get('age', 'N/A')} ani"],
            ['Experiență:', f"{farmer_data.get('experience_years', 0)} ani ({farmer_data.get('experience_level', 'N/A')})"],
            ['Suprafață totală:', f"{farmer_data.get('total_land_area', 0)} ha"],
            ['Parcele:', f"{farmer_data.get('total_parcels', 0)}"],
            ['Locație:', f"{farmer_data.get('city', 'N/A')}, {farmer_data.get('county', 'N/A')}"],
        ]
        
        table = Table(profile_data, colWidths=[5*cm, 12*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.8*cm))
        
        return elements
    
    def _build_detailed_assessment(self, assessment_data: Dict[str, Any]) -> list:
        """Build detailed assessment section"""
        elements = []
        
        header = Paragraph("EVALUARE DETALIATĂ", self.styles['ReportSection'])
        elements.append(header)
        
        bonitate = assessment_data.get('bonitate_score', {})
        farmer_score = assessment_data.get('farmer_score', {})
        
        # Bonitate scores
        bon_header = Paragraph("<b>Scor Bonitate Teren:</b>", self.styles['Normal'])
        elements.append(bon_header)
        elements.append(Spacer(1, 0.2*cm))
        
        bon_data = [
            ['Criteriu', 'Punctaj'],
            ['Calitate sol', f"{bonitate.get('soil_quality', 0)}/100"],
            ['Acces irigații', f"{bonitate.get('irrigation_access', 0)}/100"],
            ['Locație', f"{bonitate.get('location_score', 0)}/100"],
            ['Infrastructură', f"{bonitate.get('infrastructure_score', 0)}/100"],
            ['TOTAL BONITATE', f"<b>{bonitate.get('overall_score', 0)}/100</b>"],
        ]
        
        bon_table = Table(bon_data, colWidths=[10*cm, 7*cm])
        bon_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#d4e6f1')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(bon_table)
        elements.append(Spacer(1, 0.5*cm))
        
        # Farmer scores
        farm_header = Paragraph("<b>Scor Fermier:</b>", self.styles['Normal'])
        elements.append(farm_header)
        elements.append(Spacer(1, 0.2*cm))
        
        farm_data = [
            ['Criteriu', 'Punctaj'],
            ['Experiență', f"{farmer_score.get('experience_score', 0)}/100"],
            ['Educație/Training', f"{farmer_score.get('education_score', 0)}/100"],
            ['Echipament', f"{farmer_score.get('equipment_score', 0)}/100"],
            ['Capacitate financiară', f"{farmer_score.get('financial_score', 0)}/100"],
            ['TOTAL FERMIER', f"<b>{farmer_score.get('overall_score', 0)}/100</b>"],
        ]
        
        farm_table = Table(farm_data, colWidths=[10*cm, 7*cm])
        farm_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#d4e6f1')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(farm_table)
        elements.append(Spacer(1, 0.8*cm))
        
        return elements
    
    def _build_recommendations_section(self, assessment_data: Dict[str, Any]) -> list:
        """Build recommendations section"""
        elements = []
        
        header = Paragraph("RECOMANDĂRI", self.styles['ReportSection'])
        elements.append(header)
        
        recommendations = assessment_data.get('recommendations', [])
        
        if recommendations:
            rec_text = ""
            for i, rec in enumerate(recommendations, 1):
                rec_text += f"{i}. {rec}<br/><br/>"
            
            rec_para = Paragraph(rec_text, self.styles['Normal'])
            elements.append(rec_para)
        else:
            no_rec = Paragraph("Nu există recomandări specifice.", self.styles['Normal'])
            elements.append(no_rec)
        
        elements.append(Spacer(1, 0.5*cm))
        
        # Risk mitigation suggestions
        risk = assessment_data.get('risk_assessment', {})
        mitigations = risk.get('mitigation_suggestions', [])
        
        if mitigations:
            mit_header = Paragraph("<b>Sugestii de Mitigare a Riscurilor:</b>", self.styles['Normal'])
            elements.append(mit_header)
            elements.append(Spacer(1, 0.2*cm))
            
            mit_text = ""
            for i, mit in enumerate(mitigations, 1):
                mit_text += f"• {mit}<br/>"
            
            mit_para = Paragraph(mit_text, self.styles['Normal'])
            elements.append(mit_para)
        
        return elements
