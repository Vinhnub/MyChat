from PySide6.QtWidgets import QApplication, QWidget, QListWidget, QListWidgetItem, QLabel, QVBoxLayout
import sys

class ChatItemWidget(QWidget):
    def __init__(self, name, lastMsg):
        super().__init__()
        self.name = name
        self.lastMsg = lastMsg
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        lblName = QLabel(name)
        lblName.setStyleSheet("font-weight: bold; font-size: 12pt;")

        lblMsg = QLabel(lastMsg)
        lblMsg.setStyleSheet("color: gray; font-size: 10pt;")

        layout.addWidget(lblName)
        layout.addWidget(lblMsg)


class ListGroups(QWidget):
    def __init__(self, window, data):
        super().__init__()
        self._window = window
        self.setFixedWidth(250)

        self.listWidget = QListWidget()
        self.dictGroups = {}

        for groupName in data.keys():
            item = QListWidgetItem()
            widget = ChatItemWidget(groupName, data[groupName][-1]["mesContent"])
            item.setSizeHint(widget.sizeHint())
            self.listWidget.addItem(item)
            self.listWidget.setItemWidget(item, widget)
            self.dictGroups[groupName] = (item, widget)

        self.listWidget.itemClicked.connect(self.onItemClicked)

        layout = QVBoxLayout(self)
        layout.addWidget(self.listWidget)
    
    def onItemClicked(self, item):
        widget = self.listWidget.itemWidget(item)
        self._window.chatWidget.switchDataset(widget.name)

    def moveToTop(self, groupName):
        item, widget = self.dictGroups[groupName]
        row = self.listWidget.row(item)
        if row <= 0:
            return
        
        name = widget.name
        lastMsg = widget.lastMsg
        
        taken = self.listWidget.takeItem(row)  

        newWidget = ChatItemWidget(name, lastMsg)
        taken.setSizeHint(newWidget.sizeHint())

        self.listWidget.insertItem(0, taken)
        self.listWidget.setItemWidget(taken, newWidget)

        self.dictGroups[groupName] = (taken, newWidget)

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     win = ListGroups()
#     win.show()
#     sys.exit(app.exec())
