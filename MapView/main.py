import asyncio
from kivy.app import App
from kivy_garden.mapview import MapMarker, MapView
from kivy.clock import Clock
from lineMapLayer import LineMapLayer
from datasource import Datasource


class MapViewApp(App):
    def __init__(self, **kwargs):
        super().__init__()

        self.datasource = Datasource()
        self.car_marker = MapMarker(source="images/car.png")
        self.map_layer = LineMapLayer()
        self.pothole_markers = []
        self.bump_markers = []

    def on_start(self):
        """
        Встановлює необхідні маркери, викликає функцію для оновлення мапи
        """
        self.points_queue = list() # щоб був плавний рух
        self.mapview.add_widget(self.car_marker)
        Clock.schedule_interval(self.update, 1.0 / 12)  # 12 раз за секунду

    def update(self, *args):
        """
        Викликається регулярно для оновлення мапи
        """
        self.points_queue.extend(self.datasource.get_new_points())

        try:
            point = self.points_queue.pop(0)
            self.map_layer.add_point((point[0], point[1]))
            self.update_car_marker(point)

            if point[2] == 'pothole':
                self.set_pothole_marker(point)
            elif point[2] == 'bump':
                self.set_bump_marker(point)
        except IndexError:
            pass
        self.mapview.trigger_update("full")

    def update_car_marker(self, point):
        """
        Оновлює відображення маркера машини на мапі
        :param point: GPS координати
        """
        self.car_marker.lat, self.car_marker.lon = point[0], point[1]
        # self.mapview.remove_widget(self.car_marker)
        # self.mapview.add_widget(self.car_marker)

    def set_pothole_marker(self, point):
        """
        Встановлює маркер для ями
        :param point: GPS координати
        """
        same_markers = [marker for marker in self.pothole_markers if marker.lat == point[0] and marker.lon == point[1]]
        if len(same_markers) > 0:
            return
        self.pothole_marker = MapMarker(source="images/pothole.png")
        self.mapview.add_widget(self.pothole_marker)
        self.pothole_marker.lat, self.pothole_marker.lon = point[0], point[1]
        self.mapview.remove_widget(self.pothole_marker)
        self.mapview.add_widget(self.pothole_marker)
        self.pothole_markers.append(self.pothole_marker)

    def set_bump_marker(self, point):
        """
        Встановлює маркер для лежачого поліцейського
        :param point: GPS координати
        """
        same_markers = [marker for marker in self.bump_markers if marker.lat == point[0] and marker.lon == point[1]]
        if len(same_markers) > 0:
            return

        self.bump_marker = MapMarker(source="images/bump.png")
        self.mapview.add_widget(self.bump_marker)
        self.bump_marker.lat, self.bump_marker.lon = point[0], point[1]
        self.bump_markers.append(self.bump_marker)

    def build(self):
        """
        Ініціалізує мапу MapView(zoom, lat, lon)
        :return: мапу
        """
        self.mapview = MapView()
        self.mapview.add_layer(self.map_layer, mode="scatter")
        return self.mapview


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(MapViewApp().async_run(async_lib="asyncio"))
    loop.close()
