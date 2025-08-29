from PySide6.QtCore import Qt
from clientSocket import *
from Widgets import *
from PySide6.QtWidgets import QStackedWidget ,QApplication, QWidget, QMainWindow, QPushButton, QSlider
from PySide6.QtGui import QPixmap, QIcon
import sys

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        client = ClientChat()
        client.startListenThread()
        
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
   window = MainWindow()
   window.show()
   app.exec()
