from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from decimal import Decimal

from .mapping import Mapping


class PositionType(Enum):
    ONCE = "once"
    EACH = "each"


class PositionSL(Enum):
    NO_SL = "no_sl"
    SIGNAL_SL = "signal_sl"
    USER_SL = "user_sl"


@dataclass
class Configuration:
    mappings: List[Mapping]
    position_type: PositionType = PositionType.ONCE
    interval_minutes: int = 0
    position_sl: PositionSL = PositionSL.NO_SL
    stop_loss: Optional[Decimal] = None 