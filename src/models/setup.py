from dataclasses import dataclass
from typing import List

from .mapping import Mapping


@dataclass
class Setup:
    buy_conditions: List[str]
    sell_conditions: List[str]
    mappings: List[Mapping] 