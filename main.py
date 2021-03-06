import sys
from PyQt5.QtCore import Qt
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPixmap
from Y_search_module import Map, NotFoundResponseError, Address


class QMapShower(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('map_ui.ui', self)
        self.mode_combo.addItems(['Гибрид', 'Схема', 'Спутник'])
        self.mode_dict = {'Схема': 'skl', 'Спутник': 'sat', 'Гибрид': 'map'}
        self.map_ = Map(coords=[0, 0], size = [1, 1])
        self.addresses = []

        self.set_map()

        self.show_but.clicked.connect(self.set_map)
        self.search_but.clicked.connect(self.find_object)
        self.back_but.clicked.connect(self.del_last_pt)
        self.mode_combo.currentTextChanged.connect(self.set_map)
        self.withpost_check.stateChanged.connect(self.set_address)

    def set_map(self):
        self.map_.remove_self()
        pt = [ad.get_form_coords() + ',pm2dbm' for ad in self.addresses]
        self.map_ = Map(coords=[self.lon_spin.value(), self.lat_spin.value()],
                        size = [self.size_spin.value(),
                                self.size_spin.value()],
                        mode=self.mode_dict[self.mode_combo.currentText()],
                        pt=pt)
        self.map_lab.setPixmap(QPixmap(self.map_.get_map()))

    def closeEvent(self, event):
        self.map_.remove_self()

    def keyPressEvent(self, event):
        size_delta = lon_delta = lat_delta = 0
        if event.key() == Qt.Key_PageUp:
            size_delta = (self.size_spin.value() / 10)
        if event.key() == Qt.Key_PageDown:
            size_delta = -(self.size_spin.value() / 10)
        self.size_spin.setValue(self.size_spin.value() + size_delta)
        if event.key() == Qt.Key_Left:
            lon_delta = -(self.size_spin.value())
        if event.key() == Qt.Key_Right:
            lon_delta = (self.size_spin.value())
        self.lon_spin.setValue(self.lon_spin.value() + lon_delta)
        if event.key() == Qt.Key_Up:
            lat_delta = (self.size_spin.value())
        if event.key() == Qt.Key_Down:
            lat_delta = -(self.size_spin.value())
        self.lat_spin.setValue(self.lat_spin.value() + lat_delta)
        if any([lat_delta, lon_delta, size_delta]):
            self.set_map()

    def find_object(self):
        self.statusbar.showMessage('')
        if not self.search_ed.text():
            return
        try:
            address = Address(self.search_ed.text())
        except NotFoundResponseError as ex:
            self.statusbar.showMessage('Ничего не найдено.')
            return
        self.addresses += [address]
        self.set_address()
        lon, lat = address.coords
        self.lon_spin.setValue(lon)
        self.lat_spin.setValue(lat)
        self.size_spin.setValue(max(address.size))
        self.set_map()

    def del_last_pt(self):
        if self.addresses:
            del self.addresses[-1]
            self.address_ed.setText('')
            self.search_ed.setText('')
            self.set_map()

    def set_address(self):
        if self.addresses:
            ind = ', почтовый индекс: ' + self.addresses[-1].post_index\
                if self.withpost_check.checkState() else ''
            self.address_ed.setText(self.addresses[-1].full_address + ind)
        else:
            self.address_ed.setText('')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wind = QMapShower()
    wind.show()
    sys.exit(app.exec())
