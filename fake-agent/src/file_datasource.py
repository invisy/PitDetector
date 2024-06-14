import csv
from abc import abstractmethod, ABC
from datetime import datetime

from domain.accelerometer import Accelerometer
from domain.aggregated_data import AggregatedData
from domain.gps import Gps
from domain.parking import Parking


class AbstractFileDatasource(ABC):
    @abstractmethod
    def startReading(self):
        pass

    @abstractmethod
    def stopReading(self):
        pass

    @abstractmethod
    def read(self) -> AggregatedData:
        pass


class AgentFileDatasource(AbstractFileDatasource):
    def __init__(self, accelerometer_filename: str, gps_filename: str) -> None:
        self.accelerometer_filename = accelerometer_filename
        self.gps_filename = gps_filename
        self.accelerometer_file = None
        self.gps_file = None

    def startReading(self):
        self.accelerometer_file = open(self.accelerometer_filename, 'r')
        self.gps_file = open(self.gps_filename, 'r')
        next(csv.reader(self.accelerometer_file))
        next(csv.reader(self.gps_file))

    def stopReading(self):
        if self.accelerometer_file:
            self.accelerometer_file.close()
        if self.gps_file:
            self.gps_file.close()

    def read(self) -> AggregatedData:
        try:
            accelerometer_data = next(csv.reader(self.accelerometer_file))
            gps_data = next(csv.reader(self.gps_file))
            if accelerometer_data[0] == 'x' and accelerometer_data[1] == 'y' and accelerometer_data[2] == 'z':
                accelerometer_data = next(csv.reader(self.accelerometer_file))
            if gps_data[0] == 'longitude' and gps_data[1] == 'latitude':
                gps_data = next(csv.reader(self.gps_file))
        except StopIteration:
            self.accelerometer_file.seek(0)
            self.gps_file.seek(0)
            return self.read()

        return AggregatedData(
            accelerometer=Accelerometer(*accelerometer_data),
            gps=Gps(*gps_data),
            timestamp=datetime.now()
        )


class ParkingFileDatasource(AbstractFileDatasource):
    def __init__(self, parking_filename: str) -> None:
        self.parking_filename = parking_filename
        self.parking_file = None

    def startReading(self):
        self.parking_file = open(self.parking_filename, 'r')

    def stopReading(self):
        if self.parking_file:
            self.parking_file.close()

    def read(self) -> Parking:
        try:
            parking_data = next(csv.reader(self.parking_file))
            if parking_data[0] == 'empty_count' and parking_data[1] == 'longitude' and parking_data[2] == 'latitude':
                parking_data = next(csv.reader(self.parking_file))
        except StopIteration:
            self.parking_file.seek(0)
            return self.read()

        return Parking(
            empty_count=int(parking_data[0]),
            gps=Gps(*parking_data[1:]),
            timestamp=datetime.now()
        )
