import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPixmap
import requests


class MapApp(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)
        self.setWindowTitle("Yandex Map")
        self.update_map()

    def update_map(self):
        response = requests.get("https://static-maps.yandex.ru/1.x/?ll=37.677751,55.757718&spn=0.016457,"
                                "0.00619&l=map&size=650,450")
        pixmap = QPixmap()
        pixmap.loadFromData(response.content)
        self.image.setPixmap(pixmap)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MapApp()
    ex.show()
    sys.exit(app.exec_())