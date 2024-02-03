import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPixmap
import requests


class MapApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.lon = None
        self.lat = None
        self.delta = 0.01
        self.view = "map"
        self.pt = True
        uic.loadUi("main.ui", self)
        self.setWindowTitle("Yandex Map")
        self.initUI()

    def initUI(self):
        self.search_btn.clicked.connect(self.search)
        self.cancel_btn.clicked.connect(self.clear)

    def search(self):
        text = self.input_line.text()
        self.lon, self.lat = self.get_toponym_coords(text)
        self.update_map()

    def clear(self):
        self.pt = False
        self.input_line.clear()
        self.update_map()

    def get_toponym_coords(self, toponym_name):
        req_url = "http://geocode-maps.yandex.ru/1.x/"
        params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": toponym_name,
            "format": "json"
        }
        response = requests.get(req_url, params=params)
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"] \
            ["featureMember"][0]["GeoObject"]
        toponym_coords = toponym["Point"]["pos"]
        return list(map(float, toponym_coords.split(" ")))

    def get_image(self):
        req_url = f"http://static-maps.yandex.ru/1.x/"
        params = {
            "ll": ",".join((str(self.lon), str(self.lat))),
            "spn": ",".join((str(self.delta), str(self.delta))),
            "l": self.view,
            "size": '650,450',
        }
        if self.pt:
            params['pt'] = ",".join((str(self.lon), str(self.lat), 'pm2rdm'))
        response = requests.get(req_url, params=params)
        self.pt = True
        if response.status_code == 200:
            return response.content
        print(f'Ошибка {response.status_code}')

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
            self.update_map()
        elif event.key() == Qt.Key_Right:
            if self.lon - self.delta > 179:
                self.lon = 179
            else:
                self.lon += self.delta
            self.update_map()
        elif event.key() == Qt.Key_Up:
            if self.lat + self.delta > 85:
                self.lat = 85.0
            else:
                self.lat += self.delta
            self.update_map()
        elif event.key() == Qt.Key_Down:
            if self.lat - self.delta < -85:
                self.lat = -85.0
            else:
                self.lat -= self.delta
            self.update_map()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MapApp()
    ex.show()
    sys.exit(app.exec_())
    # 55.702647, 37.530834
