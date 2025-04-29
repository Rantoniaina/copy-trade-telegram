from dataclasses import dataclass
from enum import Enum
from typing import List

from .mapping import Mapping


class PositionType(Enum):
    ONCE = "once"
    EACH = "each"


@dataclass
class Configuration:
    mappings: List[Mapping]
    position_type: PositionType = PositionType.ONCE
    interval_minutes: int = 0 