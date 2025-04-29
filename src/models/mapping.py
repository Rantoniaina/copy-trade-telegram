from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class SLPosition(Enum):
    BEFORE = "before"
    AFTER = "after"


@dataclass
class Mapping:
    from_message: List[str]
    mapping: str
    sl_position: Optional[SLPosition] = None 