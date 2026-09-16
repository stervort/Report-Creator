"""
Report Generator Module
Orchestrates the generation of all reports
"""

import json
import os
import logging
from datetime import datetime
from pathlib import Path

from data_loader import load_qb_data
from accrual_processor import AccrualProcessor
from pdf_builder import generate_budget_manager_report, generate_top_level_report, generate_campus_wide_report
from excel_builder import generate_detail_excel

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ReportGenerator:
    """Main report generator"""
    
    def __init__(self, config_path):
        """Initialize report generator"""
        self.config_path = config_path
        self.config = self._load_config()
        
        self.bva, self.gl = load_qb_data(
            self.config['file_paths']['budget_vs_actuals'],
            self.config['file_paths']['general_ledger']
        )
        
        self.output_folder = Path(self.config['file_paths']['output_folder'])
        self.output_folder.mkdir(exist_ok=True)
    
    def _load_config(self):
        """Load configuration from JSON file"""
        logger.info(f"Loading config from {self.config_path}")
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        return config
    
    def generate_all_reports(self):
        """Generate all configured reports"""
        logger.info("=" * 60)
        logger.info("GENERATING REPORTS")
        logger.info("=" * 60)
        
        for report_config in self.config['reports']:
            self._generate_single_report(report_config)
        
        logger.info("=" * 60)
        logger.info("ALL REPORTS GENERATED")
        logger.info("=" * 60)
    
    def generate_report(self, report_name):
        """Generate a specific report by name"""
        report_config = None
        for r in self.config['reports']:
            if r['name'] == report_name:
                report_config = r
                break
        
        if not report_config:
            logger.error(f"Report '{report_name}' not found in config")
            return False
        
        return self._generate_single_report(report_config)
    
    def _generate_single_report(self, report_config):
        """Generate a single report"""
        report_name = report_config['name']
        logger.info(f"\nGenerating: {report_name}")
        logger.info("-" * 40)
        
        departments = report_config.get('departments', [])
        if departments == 'all':
            departments = self.bva.get_classes()
        
        logger.info(f"  Departments: {', '.join(departments)}")
        logger.info(f"  Include Payroll: {report_config.get('include_payroll', False)}")
        logger.info(f"  Include Detail: {report_config.get('include_detail', False)}")
        logger.info(f"  Include Excel: {report_config.get('include_excel', False)}")
        
        try:
            bva_data = self._prepare_bva_data(departments, report_config)
            transactions = self._prepare_transactions(departments, report_config)
            
            pdf_filename = self._sanitize_filename(report_name) + '.pdf'
            pdf_path = self.output_folder / pdf_filename
            
            report_type = report_config.get('type', 'budget-manager')
            
            if report_type == 'budget-manager':
                generate_budget_manager_report(
                    str(pdf_path),
                    report_config,
                    bva_data,
                    self.config['branding']
                )
            elif report_type == 'top-level':
                generate_top_level_report(
                    str(pdf_path),
                    report_config,
                    bva_data,
                    self.config['branding']
                )
            elif report_type == 'campus-wide':
                generate_campus_wide_report(
                    str(pdf_path),
                    report_config,
                    bva_data,
                    self.config['branding']
                )
            
            logger.info(f"  ✓ PDF: {pdf_filename}")
            
            if report_config.get('include_excel', False):
                excel_filename = self._sanitize_filename(report_name) + '_detail.xlsx'
                excel_path = self.output_folder / excel_filename
                
                generate_detail_excel(
                    str(excel_path),
                    report_name,
                    self.config['branding']['company_name'],
                    transactions
                )
                
                logger.info(f"  ✓ Excel: {excel_filename}")
            
            return True
        
        except Exception as e:
            logger.error(f"  ✗ Error generating {report_name}: {e}", exc_info=True)
            return False
    
    def _prepare_bva_data(self, departments, report_config):
        """Prepare Budget vs Actuals data for the report"""
        data = {'summary': []}
        return data
    
    def _prepare_transactions(self, departments, report_config):
        """Prepare transaction details for Excel export"""
        all_txs = self.gl.get_transactions_for_classes(departments)
        
        if self.config['accrual_settings'].get('condense_accruals', True):
            processor = AccrualProcessor(self.config['accrual_settings'])
            all_txs = processor.process_transactions(all_txs)
            all_txs = processor.filter_for_detail_report(all_txs)
        
        return all_txs
    
    @staticmethod
    def _sanitize_filename(name):
        """Sanitize string for use as filename"""
        return "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).replace(' ', '_')


def main(config_path='report_config.json', report_name=None):
    """Main entry point"""
    try:
        generator = ReportGenerator(config_path)
        
        if report_name:
            generator.generate_report(report_name)
        else:
            generator.generate_all_reports()
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == '__main__':
    import sys
    exit(main())
