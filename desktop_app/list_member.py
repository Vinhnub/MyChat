from PySide6.QtWidgets import QApplication, QWidget, QListWidget, QListWidgetItem, QLabel, QVBoxLayout
import sys

class MemberWidget(QWidget):
    def __init__(self, username, fullName):
        super().__init__()
        self.username = username
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        lblusername = QLabel(username)
        lblusername.setStyleSheet("color: gray; font-size: 10pt;")

        lblFullName = QLabel(fullName)
        lblFullName.setStyleSheet("font-weight: bold; font-size: 12pt;")

        layout.addWidget(lblFullName)
        layout.addWidget(lblusername)


class ListMemberWidget(QWidget):
    def __init__(self, window, data):
        super().__init__()
        self.setFixedWidth(250)
        self._window = window

        self.listWidget = QListWidget()
        if data:
            for (username, fullName) in data:
                item = QListWidgetItem()
                widget = MemberWidget(username, fullName)
                item.setSizeHint(widget.sizeHint())
                self.listWidget.addItem(item)
                self.listWidget.setItemWidget(item, widget)

        layout = QVBoxLayout(self)
        layout.addWidget(self.listWidget)

