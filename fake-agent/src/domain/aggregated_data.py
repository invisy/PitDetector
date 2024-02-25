from dataclasses import dataclass
from datetime import datetime
from accelerometer import Accelerometer
from gps import Gps


@dataclass
class AggregatedData:
    accelerometer: Accelerometer
    gps: Gps
    time: datetime
