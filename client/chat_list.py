from PySide6.QtWidgets import QApplication, QWidget, QListWidget, QListWidgetItem, QLabel, QVBoxLayout
import sys

class ChatItemWidget(QWidget):
    def __init__(self, name, last_msg):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        # Tên
        lblName = QLabel(name)
        lblName.setStyleSheet("font-weight: bold; font-size: 12pt;")

        # Tin nhắn cuối
        lblMsg = QLabel(last_msg)
        lblMsg.setStyleSheet("color: gray; font-size: 10pt;")

        layout.addWidget(lblName)
        layout.addWidget(lblMsg)


class ListGroups(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Danh sách hội thoại")
        self.setFixedWidth(250)

        self.listWidget = QListWidget()

        # Demo data
        data = [
            ("Nguyễn Văn AAAAAAAAAAAAAAAAAAAAAAAAAAA", "Tin nhắn cuối nè"),
            ("Nhóm bạn bè", "Hôm nay đi chơi nhé?"),
            ("Trần B", "Đã gửi một ảnh"),
        ]

        for name, msg in data:
            item = QListWidgetItem(self.listWidget)
            widget = ChatItemWidget(name, msg)
            item.setSizeHint(widget.sizeHint())
            self.listWidget.addItem(item)
            self.listWidget.setItemWidget(item, widget)

        layout = QVBoxLayout(self)
        layout.addWidget(self.listWidget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ListGroups()
    win.show()
    sys.exit(app.exec())
