from dataclasses import dataclass
from typing import List


@dataclass
class Setup:
    """
    DEPRECATED: This class is deprecated and will be removed in a future version.
    Buy and sell conditions are now part of the Configuration class.
    """
    buy_conditions: List[str]
    sell_conditions: List[str] 