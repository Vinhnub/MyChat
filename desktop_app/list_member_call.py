from PySide6.QtWidgets import QApplication, QWidget, QListWidget, QListWidgetItem, QLabel, QVBoxLayout, QSlider
import sys
from PySide6.QtCore import Qt

class MemberCallWidget(QWidget):
    def __init__(self, parentWidget, username, fullName):
        super().__init__()
        self._parent = parentWidget
        self.username = username
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        lblusername = QLabel(username)
        lblusername.setStyleSheet("color: gray; font-size: 10pt;")

        lblFullName = QLabel(fullName)
        lblFullName.setStyleSheet("font-weight: bold; font-size: 12pt;")

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMaximum(100)
        self.slider.setMinimum(0)
        self.slider.setValue(100)

        self.slider.sliderReleased.connect(self.changeVolume)

        layout.addWidget(lblFullName)
        layout.addWidget(lblusername)
        layout.addWidget(self.slider)

    def changeVolume(self):
        self._parent.changeVolume(self.username, self.slider.value())


class ListMemberCallWidget(QWidget):
    def __init__(self, window, data):
        super().__init__()
        self.setFixedWidth(400)
        self._window = window

        self.listWidget = QListWidget()
        self.dictMember = {}
        if data:
            for item in data:
                username, fullName = item[0], item[1]
                item = QListWidgetItem()
                widget = MemberCallWidget(self, username, fullName)
                item.setSizeHint(widget.sizeHint())
                self.listWidget.addItem(item)
                self.listWidget.setItemWidget(item, widget)
                self.dictMember[username] = (item, widget)

        layout = QVBoxLayout(self)
        layout.addWidget(self.listWidget)

    def addMemberIntoCall(self, data):
        username = next(iter(data))
        item = QListWidgetItem()
        widget = MemberCallWidget(self, username, data[username])
        item.setSizeHint(widget.sizeHint())
        self.listWidget.insertItem(0, item)
        self.listWidget.setItemWidget(item, widget)
        self.dictMember[username] = (item, widget)

    def removeMemberFromCall(self, username):
        item, widget = self.dictMember[username]
        row = self.listWidget.row(item)
        self.listWidget.takeItem(row) 
        del self.dictMember[username]

    def changeVolume(self, username, value):
        if self._window:
            self._window.changeVolume(username, value)

# dataTest = {"vinh" : "Nguyen Van Vinh", "vinhnub" : "Alex"}

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     win = ListMemberCallWidget(None, dataTest)
#     win.show()
#     sys.exit(app.exec())
