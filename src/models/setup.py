from dataclasses import dataclass
from typing import List, Optional
from decimal import Decimal


@dataclass
class Setup:
    """
    Represents the result of processing an incoming message based on configuration.
    Contains the trading setup details extracted from the message.
    """
    instrument: str  # The trading pair/instrument based on mapping value
    sl: Optional[Decimal] = None  # Stop loss level in decimal
    tps: List[Decimal] = None  # Array of take profit levels in decimal 