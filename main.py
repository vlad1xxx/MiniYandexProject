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
        self.point = tuple()
        self.address = ''
        self.pt = True  # отвечает за ставить метку или нет
        self.is_search = True
        uic.loadUi("main.ui", self)
        self.setWindowTitle("Yandex Map")
        self.image.mousePressEvent = self.click_on_map
        self.initUI()

    # присоединяем кнопки к функциям
    def initUI(self):
        # self.image.resize(450, 450)
        self.search_btn.setIcon(QIcon('images/image.png'))
        self.search_btn.clicked.connect(self.search)
        self.show_index.stateChanged.connect(self.print_address)
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
                self.point = (str(self.lon), str(self.lat), 'pm2rdm')
                self.update_map()
                self.is_search = False
                self.search_btn.setIcon(QIcon('images/image2.png'))
                self.input_line.setDisabled(True)
                self.setFocus()
        else:
            self.pt = False
            self.address = ''
            self.index = ''
            self.input_line.clear() # очистка поля ввода
            self.address_label.clear()
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
        print(json_response)
        toponym = json_response["response"]["GeoObjectCollection"] \
            ["featureMember"][0]["GeoObject"]
        toponym_coords = toponym["Point"]["pos"]
        self.address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        self.index = toponym["metaDataProperty"]["GeocoderMetaData"]['Address']['postal_code']
        self.print_address()
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
            params['pt'] = ",".join(self.point)
        response = requests.get(req_url, params=params)
        self.pt = True
        if response.status_code == 200:
            return response.content

    # отображает адрес
    def print_address(self):
        if self.show_index.isChecked():
            self.address_label.setText(self.address + '\n' + self.index)
        else:
            self.address_label.setText(self.address)
        # выравнивание текста
        self.address_label.setWordWrap(True)

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

    def search_toponym(self, lon, lat):
        params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": ','.join((str(lon), str(lat))),
            "format": "json"
        }
        response = requests.get(f'https://geocode-maps.yandex.ru/1.x/', params=params)
        json_response = response.json()
        address = json_response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['Address']['formatted']
        self.print_address(address)

    def click_on_map(self, event):
        pos = event.pos()
        lon, lat = self.find_new_lonlat(pos.x(), pos.y())
        # обновляем координаты метки
        self.point = (str(lon), str(lat), 'pm2rdm')
        self.update_map()

    # следит за нажатыми кнопками, нажата стрелка вверх - карта двинется наверх и тд
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
        # изменение масштаба
        elif event.key() == Qt.Key_PageUp:
            if self.delta > 0.001:
                self.delta /= 2.4
        elif event.key() == Qt.Key_PageDown:
            if self.delta < 50:
                self.delta *= 2.4
        self.update_map()

    def find_new_lonlat(self, x, y):
        center_x = 325
        center_y = 225
        lon = self.lon + (x - center_x) * (self.delta * 2 / 450)
        lat = self.lat - (y - center_y) * (self.delta * 2 / 650)
        return lon, lat


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MapApp()
    ex.show()
    sys.exit(app.exec_())

