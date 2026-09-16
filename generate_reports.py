#!/usr/bin/env python3
"""
Noorda Reports Generator
Main entry point for generating QB budget reports

Usage:
    python generate_reports.py                    # Generate all reports
    python generate_reports.py --report "Name"    # Generate specific report
"""

import sys
import argparse
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from report_generator import ReportGenerator
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='Generate Noorda College QB budget reports',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python generate_reports.py                     Generate all reports
  python generate_reports.py --report "Finance Manager"     Generate one report
  python generate_reports.py --list              List available reports
        '''
    )
    
    parser.add_argument(
        '--report',
        type=str,
        help='Generate specific report by name'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available reports'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='report_config.json',
        help='Path to configuration file (default: report_config.json)'
    )
    
    args = parser.parse_args()
    
    # Check if config file exists
    if not os.path.exists(args.config):
        logger.error(f"Config file not found: {args.config}")
        logger.info("Please make sure report_config.json is in the current directory")
        return 1
    
    try:
        # Initialize generator
        generator = ReportGenerator(args.config)
        
        # List reports
        if args.list:
            logger.info("\nAvailable reports:")
            for i, report in enumerate(generator.config['reports'], 1):
                report_type = report.get('type', 'unknown')
                depts = report.get('departments', [])
                if depts == 'all':
                    depts_str = 'all departments'
                else:
                    depts_str = f"{len(depts)} department(s)"
                logger.info(f"  {i}. {report['name']} [{report_type}] - {depts_str}")
            return 0
        
        # Generate reports
        if args.report:
            logger.info(f"Generating report: {args.report}")
            success = generator.generate_report(args.report)
            return 0 if success else 1
        else:
            generator.generate_all_reports()
            return 0
    
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        return 1
    
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
