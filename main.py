import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPixmap
import requests


class MapApp(QMainWindow):
    def __init__(self, lon, lat, delta, view='map'):
        super().__init__()
        self.lon = lon
        self.lat = lat
        self.delta = delta
        self.view = view
        uic.loadUi("main.ui", self)
        self.setWindowTitle("Yandex Map")
        self.update_map()

    def get_image(self):
        req_url = f"http://static-maps.yandex.ru/1.x/"
        params = {
            "ll": ",".join((self.lon, self.lat)),
            "spn": ",".join((self.delta, self.delta)),
            "l": self.view,
            "size": '650,450'
        }
        response = requests.get(req_url, params=params)
        return response.content

    def update_map(self):
        pixmap = QPixmap()
        pixmap.loadFromData(self.get_image())
        self.image.setPixmap(pixmap)


if __name__ == "__main__":
    lon = input()
    lat = input()
    delta = input()
    app = QApplication(sys.argv)
    ex = MapApp(lon, lat, delta)
    ex.show()
    sys.exit(app.exec_())