from dataclasses import dataclass
from typing import List


@dataclass
class Setup:
    buy_conditions: List[str]
    sell_conditions: List[str] 