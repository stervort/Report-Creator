"""
Accrual Processor Module
Condenses and nets accrual transactions
"""

import pandas as pd
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AccrualProcessor:
    """Process and condense accrual transactions"""
    
    def __init__(self, config):
        self.config = config
        self.ramp_keywords = config.get('ramp_keywords', ['Ramp', 'accrual', 'pending'])
        self.min_days = config.get('min_days_between_offset', 1)
        self.condense = config.get('condense_accruals', True)
    
    def process_transactions(self, transactions):
        """Process list of transactions and condense accruals"""
        if not self.condense:
            return transactions
        
        logger.info(f"Processing {len(transactions)} transactions for accruals")
        
        df = pd.DataFrame(transactions)
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        df['is_accrual'] = df.apply(self._is_accrual_transaction, axis=1)
        
        condensed_indices = set()
        accrual_txs = df[df['is_accrual']].copy()
        
        for idx, tx in accrual_txs.iterrows():
            if idx in condensed_indices:
                continue
            
            amount = tx['amount']
            date = tx['date']
            cls = tx['class']
            
            potential_matches = accrual_txs[
                (accrual_txs['class'] == cls) &
                (accrual_txs['amount'] == -amount) &
                (accrual_txs['date'] >= date) &
                (accrual_txs['date'] <= date + timedelta(days=self.min_days + 5)) &
                (accrual_txs.index != idx)
            ]
            
            if len(potential_matches) > 0:
                match_idx = potential_matches.index[0]
                condensed_indices.add(idx)
                condensed_indices.add(match_idx)
        
        df['condensed'] = False
        df.loc[list(condensed_indices), 'condensed'] = True
        
        result = df.to_dict('records')
        
        logger.info(f"Condensed {len(condensed_indices)} transactions ({len(condensed_indices)//2} pairs)")
        
        return result
    
    def _is_accrual_transaction(self, row):
        """Check if transaction appears to be accrual-related"""
        description = str(row.get('description', '')).lower()
        name = str(row.get('name', '')).lower()
        
        combined = f"{description} {name}"
        
        return any(keyword.lower() in combined for keyword in self.ramp_keywords)
    
    def filter_for_detail_report(self, transactions):
        """Filter transactions for detail report"""
        return [t for t in transactions if not t.get('condensed', False)]
    
    def get_summary(self, transactions):
        """Get summary of accrual condensing"""
        condensed = [t for t in transactions if t.get('condensed', False)]
        
        return {
            'total_transactions': len(transactions),
            'condensed_transactions': len(condensed),
            'condensed_pairs': len(condensed) // 2,
            'detail_transactions': len(transactions) - len(condensed)
        }
