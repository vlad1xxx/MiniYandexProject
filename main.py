import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPixmap, QIcon
import requests


class MapApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.lon = None
        self.lat = None
        self.delta = 0.02
        self.view = 'map'
        self.pt = True  # отвечает за ставить метку или нет
        self.is_search = True
        uic.loadUi("main.ui", self)
        self.setWindowTitle("Yandex Map")
        self.initUI()

    # присоединяем кнопки к функциям
    def initUI(self):
        self.search_btn.setIcon(QIcon('images/image.png'))
        self.search_btn.clicked.connect(self.search)
        # кнопки смены режима карты
        self.scheme.clicked.connect(self.make_map)
        self.satellite.clicked.connect(self.make_satellite)
        self.hybrid.clicked.connect(self.make_hybrid)

    # идет поиск по карте
    def search(self):
        if self.is_search:
            text = self.input_line.text()  # беру текст
            if text:
                self.lon, self.lat = self.get_toponym_coords(text)  # ищем топоним и получаем координаты
                self.update_map()
                self.is_search = False
                self.search_btn.setIcon(QIcon('images/image2.png'))
                self.input_line.setDisabled(True)
                self.setFocus()
        else:
            self.pt = False
            self.input_line.clear()  # очистка поля ввода
            self.update_map()  # отображаю карту без метки
            self.is_search = True
            self.search_btn.setIcon(QIcon('images/image.png'))
            self.input_line.setDisabled(False)

    # получение координат топонима
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

    # получение изображения карты
    def get_image(self):
        req_url = f"http://static-maps.yandex.ru/1.x/"
        params = {
            "ll": ",".join((str(self.lon), str(self.lat))),
            "spn": ",".join((str(self.delta), str(self.delta))),
            "l": self.view,
            "size": '650,450'
        }
        if self.pt:  # если True то карта будет с меткой
            params['pt'] = ",".join((str(self.lon), str(self.lat), 'pm2rdm'))
        response = requests.get(req_url, params=params)
        self.pt = True
        if response.status_code == 200:
            return response.content
        print(f'Ошибка {response.status_code}')

    # отображает карту
    def update_map(self):
        pixmap = QPixmap()
        pixmap.loadFromData(self.get_image())
        self.image.setPixmap(pixmap)

    # режим 'гибрид'
    def make_hybrid(self):
        self.view = 'skl'
        self.update_map()
        self.setFocus()

    # режим 'схема'
    def make_map(self):
        self.view = 'map'
        self.update_map()
        self.setFocus()

    # режим 'спутник'
    def make_satellite(self):
        self.view = 'sat'
        self.update_map()
        self.setFocus()

    # следит за нажатыми кнопками, нажата стрелка вверх - карта двинется наверх и тд
    def keyPressEvent(self, event):
        print(event.key())
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
        # изменение масштаба
        elif event.key() == Qt.Key_PageUp:
            if self.delta > 0.001:
                self.delta /= 2.4
        elif event.key() == Qt.Key_PageDown:
            if self.delta < 50:
                self.delta *= 2.4
        self.update_map()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MapApp()
    ex.show()
    sys.exit(app.exec_())
