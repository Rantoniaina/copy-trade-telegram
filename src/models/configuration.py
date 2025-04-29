from dataclasses import dataclass
from typing import List

from .mapping import Mapping


@dataclass
class Configuration:
    mappings: List[Mapping] 