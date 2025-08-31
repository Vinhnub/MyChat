from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QStackedWidget
import sys, asyncio, qasync

from clientSocket import ClientChat
from Widgets import WidgetLogin, ChatWindow, Profile


class MainWindow(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.client = ClientChat()

        self.stack = QStackedWidget()
        self.setWindowTitle("MyChat")

        self.w1 = WidgetLogin(self.app, self.client, self.stack)
        self.w2 = ChatWindow(self.app, self.client, stack=self.stack)
        self.w3 = Profile(self.app, self.client, self.stack)

        self.stack.addWidget(self.w1)
        self.stack.addWidget(self.w2)
        self.stack.addWidget(self.w3)

        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow(app)
    window.show()

    # Đặt connect() sau khi window tạo xong và loop đang quản lý
    loop.create_task(window.client.connect())

    with loop:
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass

