from dataclasses import dataclass
from datetime import datetime

from domain.gps import Gps


@dataclass
class Parking:
    empty_count: int
    gps: Gps
    timestamp: datetime