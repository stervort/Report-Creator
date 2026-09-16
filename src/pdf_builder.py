"""
PDF Builder Module
Generates professional PDF reports
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFBuilder:
    """Build professional PDF reports"""
    
    def __init__(self, filepath, branding_config):
        self.filepath = filepath
        self.branding = branding_config
        self.story = []
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        try:
            self.styles.add(ParagraphStyle(
                name='ReportTitle',
                parent=self.styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#1f4788'),
                spaceAfter=12,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            ))
        except KeyError:
            pass
        
        try:
            self.styles.add(ParagraphStyle(
                name='SectionHeader',
                parent=self.styles['Heading2'],
                fontSize=12,
                textColor=colors.HexColor('#1f4788'),
                spaceAfter=8,
                spaceBefore=8,
                fontName='Helvetica-Bold'
            ))
        except KeyError:
            pass
    
    def add_header(self, report_name):
        """Add report header"""
        self.story.append(Paragraph(self.branding.get('company_name', ''), self.styles['ReportTitle']))
        self.story.append(Paragraph(report_name, self.styles.get('SectionHeader', self.styles['Heading2'])))
        
        period = self.branding.get('report_period', '')
        if period:
            self.story.append(Paragraph(f"<i>For the period: {period}</i>", self.styles['Normal']))
        
        self.story.append(Paragraph(
            f"<i>Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</i>",
            self.styles['Normal']
        ))
        
        self.story.append(Spacer(1, 0.3*inch))
    
    def add_section_header(self, title):
        """Add section header"""
        self.story.append(Paragraph(title, self.styles.get('SectionHeader', self.styles['Heading2'])))
        self.story.append(Spacer(1, 0.1*inch))
    
    def add_budget_vs_actual_table(self, data):
        """Add Budget vs Actual table"""
        table_data = [
            ['Account', 'Actual', 'Budget', 'Variance', '% of Budget']
        ]
        
        for row in data:
            desc = str(row.get('description', ''))[:50]
            actual = self._format_currency(row.get('actual'))
            budget = self._format_currency(row.get('budget'))
            variance = self._format_currency(row.get('variance'))
            variance_pct = self._format_percent(row.get('variance_pct'))
            
            table_data.append([desc, actual, budget, variance, variance_pct])
        
        table = Table(table_data, colWidths=[2.5*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.1*inch])
        
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))
    
    def add_summary_text(self, text):
        """Add summary paragraph"""
        self.story.append(Paragraph(text, self.styles['Normal']))
        self.story.append(Spacer(1, 0.1*inch))
    
    def add_spacer(self, width, height):
        """Add spacer"""
        self.story.append(Spacer(width, height))
    
    def add_page_break(self):
        """Add page break"""
        self.story.append(PageBreak())
    
    def add_footer(self):
        """Add footer"""
        self.story.append(Spacer(1, 0.3*inch))
        footer_text = self.branding.get('footer_text', '')
        if footer_text:
            try:
                footer_style = ParagraphStyle(
                    'FooterStyle',
                    parent=self.styles['Normal'],
                    fontSize=8,
                    textColor=colors.grey,
                    alignment=TA_CENTER
                )
            except KeyError:
                footer_style = self.styles['Normal']
            self.story.append(Paragraph(footer_text, footer_style))
    
    def build(self):
        """Generate the PDF file"""
        logger.info(f"Building PDF: {self.filepath}")
        
        doc = SimpleDocTemplate(
            self.filepath,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        doc.build(self.story)
        logger.info(f"PDF created: {self.filepath}")
    
    @staticmethod
    def _format_currency(value):
        """Format number as currency"""
        if value is None or value == '':
            return '-'
        try:
            return f"${float(value):,.0f}"
        except (ValueError, TypeError):
            return str(value)
    
    @staticmethod
    def _format_percent(value):
        """Format number as percentage"""
        if value is None or value == '':
            return '-'
        try:
            return f"{float(value)*100:.1f}%"
        except (ValueError, TypeError):
            return str(value)


def generate_budget_manager_report(pdf_path, report_config, bva_data, branding):
    """Generate a budget manager report"""
    builder = PDFBuilder(pdf_path, branding)
    
    builder.add_header(report_config['name'])
    
    builder.add_section_header("Budget vs. Actual Summary")
    builder.add_budget_vs_actual_table(bva_data.get('summary', []))
    
    builder.add_summary_text(
        f"This report shows budget compared to actual expenses for {', '.join(report_config['departments'])}"
    )
    
    if report_config.get('include_detail', False):
        builder.add_page_break()
        builder.add_section_header("Detailed Transactions")
        builder.add_summary_text("See accompanying Excel file for detailed transaction list.")
    
    builder.add_footer()
    builder.build()


def generate_top_level_report(pdf_path, report_config, bva_data, branding):
    """Generate a top-level manager report"""
    builder = PDFBuilder(pdf_path, branding)
    
    builder.add_header(report_config['name'])
    
    builder.add_section_header("Consolidated Summary - All Departments")
    builder.add_budget_vs_actual_table(bva_data.get('consolidated', []))
    
    if report_config.get('include_detail', False):
        builder.add_page_break()
        
        for dept in report_config.get('departments', []):
            builder.add_section_header(f"Department: {dept}")
            builder.add_budget_vs_actual_table(bva_data.get(f'dept_{dept}', []))
            builder.add_spacer(1, 0.15*inch)
    
    builder.add_footer()
    builder.build()


def generate_campus_wide_report(pdf_path, report_config, bva_data, branding):
    """Generate campus-wide report"""
    builder = PDFBuilder(pdf_path, branding)
    
    builder.add_header(report_config['name'])
    
    builder.add_section_header("Campus-Wide Summary")
    builder.add_budget_vs_actual_table(bva_data.get('campus_summary', []))
    
    builder.add_section_header("Key Metrics")
    builder.add_summary_text(
        "Total revenue, total expenses, and profitability across all departments and cost centers."
    )
    
    builder.add_footer()
    builder.build()
