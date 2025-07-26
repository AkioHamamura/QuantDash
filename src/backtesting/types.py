# Common types and data structures for backtesting

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Trade:
    """Simple trade record"""
    entry_date: datetime
    exit_date: Optional[datetime] = None
    shares: int = 0
    entry_price: float = 0.0
    exit_price: float = 0.0
    profit_loss: float = 0.0
