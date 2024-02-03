import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt
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
            "ll": ",".join((str(self.lon), str(self.lat))),
            "spn": ",".join((str(self.delta), str(self.delta))),
            "l": self.view,
            "size": '650,450'
        }
        response = requests.get(req_url, params=params)
        if response.status_code == 200:
            return response.content
        print(f'Ошибка {response.status_code}')
        self.close()

    def update_map(self):
        pixmap = QPixmap()
        pixmap.loadFromData(self.get_image())
        self.image.setPixmap(pixmap)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            if self.lon - self.delta < -179:
                self.lon = -179
            else:
                self.lon -= self.delta
        elif event.key() == Qt.Key_Right:
            if self.lon - self.delta > 179:
                self.lon = 179
            else:
                self.lon += self.delta
        elif event.key() == Qt.Key_Up:
            if self.lat + self.delta > 85:
                self.lat = 85.0
            else:
                self.lat += self.delta
        elif event.key() == Qt.Key_Down:
            if self.lat - self.delta < -85:
                self.lat = -85.0
            else:
                self.lat -= self.delta
        self.update_map()


if __name__ == "__main__":
    lon = float(input())
    lat = float(input())
    delta = float(input())
    app = QApplication(sys.argv)
    ex = MapApp(lon, lat, delta)
    ex.show()
    sys.exit(app.exec_())
    # 55.702647, 37.530834