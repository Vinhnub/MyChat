from PySide6.QtCore import Qt
from clientSocket import *
from Widgets import *
from PySide6.QtWidgets import QStackedWidget ,QApplication, QWidget, QMainWindow, QPushButton, QSlider
import sys

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        client = ClientChat()
        self.stack = QStackedWidget()
        
        self.w1 = WidgetLogin(app, client, self.stack)
        self.w2 = ChatWindow(app, client, self.stack)
        self.stack.addWidget(self.w1)
        self.stack.addWidget(self.w2)
        
        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

if __name__ == "__main__":
   app = QApplication(sys.argv)
   window = MainWindow()
   window.show()
   app.exec()
