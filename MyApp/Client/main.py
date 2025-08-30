from PySide6.QtCore import Qt, QTimer
from clientSocket import *
from Widgets import *
from PySide6.QtWidgets import QStackedWidget ,QApplication, QWidget, QMainWindow, QPushButton, QSlider
from PySide6.QtGui import QPixmap, QIcon
import sys
import qasync 
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        client = ClientChat()
        QTimer.singleShot(0, lambda: asyncio.create_task(client.connect()))
        
        self.stack = QStackedWidget()
        self.setWindowTitle("MyChat")     
        
        self.w1 = WidgetLogin(app, client, self.stack)
        self.w2 = ChatWindow(app, client, self.stack)
        self.w3 = Profile(app, client, self.stack)

        self.stack.addWidget(self.w1)
        self.stack.addWidget(self.w2)
        self.stack.addWidget(self.w3)
        
        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # chạy Qt event loop kết hợp với asyncio
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow()
    window.show()

    with loop:
        loop.run_forever()
