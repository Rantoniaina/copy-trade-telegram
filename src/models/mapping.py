from dataclasses import dataclass
from typing import List


@dataclass
class Mapping:
    from_message: List[str]
    mapping: str 