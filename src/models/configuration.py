from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from decimal import Decimal

from .mapping import Mapping, SLPosition, TPPosition


class PositionType(Enum):
    ONCE = "once"
    EACH = "each"
    TP_LENGTH = "tp_length"


class PositionSL(Enum):
    NO_SL = "no_sl"
    SIGNAL_SL = "signal_sl"
    USER_SL = "user_sl"


class PositionTP(Enum):
    NO_TP = "no_tp"
    SIGNAL_TP = "signal_tp"
    USER_TP = "user_tp"
    ALTERNATE = "alternate"


@dataclass
class Configuration:
    pair_mappings: List[Mapping]
    buy_conditions: List[str]
    sell_conditions: List[str]
    sl_mappings: List[Mapping] = None
    tp_mappings: List[Mapping] = None
    position_type: PositionType = PositionType.ONCE
    interval_minutes: int = 0
    position_sl: PositionSL = PositionSL.NO_SL
    position_tp: PositionTP = PositionTP.NO_TP
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None 