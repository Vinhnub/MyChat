from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QComboBox, QTabWidget, QAbstractItemView, QListWidget, QRadioButton, QButtonGroup, QCheckBox,QGroupBox,QGridLayout, QSizePolicy, QTextEdit, QLineEdit, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox, QLabel
from client.clientSocket import *
from PySide6.QtCore import Signal, QObject
import threading

class WidgetLogin(QWidget):
    def __init__(self, app, client, stack=None):
        super().__init__()
        self.setWindowTitle("Login")
        self.app = app
        self.client = client
        self.stack = stack
        self.msg = ""

        username = QLabel("Username: ")
        self.lineInputUsername = QLineEdit()
        
        passW = QLabel("PassWorld: ")
        self.lineInputPassW = QLineEdit()

        LoginButton = QPushButton("Login")
        LoginButton.clicked.connect(self.CheckValid)

        quitButton = QPushButton("Quit")
        quitButton.clicked.connect(self.quitLogin)

        layOutUserH = QHBoxLayout()
        layOutUserH.addWidget(username)
        layOutUserH.addWidget(self.lineInputUsername)

        layOutPassH = QHBoxLayout()
        layOutPassH.addWidget(passW)
        layOutPassH.addWidget(self.lineInputPassW)

        layOutLoginH = QHBoxLayout()
        layOutLoginH.addWidget(LoginButton)
        layOutLoginH.addWidget(quitButton)

        layOutV = QVBoxLayout()
        layOutV.addLayout(layOutUserH)
        layOutV.addLayout(layOutPassH)
        layOutV.addLayout(layOutLoginH)
        
        self.setLayout(layOutV)


    def CheckValid(self):
        username = self.lineInputUsername.text()
        password = self.lineInputPassW.text()
        self.client.setNamePsw(username, password)
        result = self.client.userLogin()
        QMessageBox.information(self, "Login result", result)
        if self.stack and result == "login successfully":
            self.client.startListenThread() # bat dau thread listen lien tuc
            self.stack.setCurrentIndex(1)
        
    def quitLogin(self):
        self.app.quit()

class WidgetStartChat(QWidget):
    def __init__(self, app, client, stack=None):
        super().__init__()
        self.setWindowTitle("StartChat")
        self.textEdit = QTextEdit()
        self.client = client
        self.client.newMessage.connect(self.displayMessage) # ket noi vao tin hieu cua client listen
        self.app = app
        
        self.viewChat = QTextEdit()
        self.viewChat.setReadOnly(True)
        
        InputText = QLabel("Text her: ")
        self.lineInputText = QLineEdit()

        layOutTextH = QHBoxLayout()
        layOutTextH.addWidget(InputText)
        layOutTextH.addWidget(self.lineInputText)

        layOutV = QVBoxLayout()
        layOutV.addWidget(self.viewChat)
        layOutV.addLayout(layOutTextH)

        self.lineInputText.editingFinished.connect(self.EditFinished)

        self.setLayout(layOutV)

    def EditFinished(self):
        self.msg = self.lineInputText.text()
        self.lineInputText.clear()
        self.client.sendChat(self.msg)
    
    def displayMessage(self, msg):
        self.viewChat.append(msg)


