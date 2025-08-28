from PySide6.QtWidgets import QListWidget, QSplitter, QComboBox, QTabWidget, QAbstractItemView, QListWidget, QRadioButton, QButtonGroup, QCheckBox,QGroupBox,QGridLayout, QSizePolicy, QTextEdit, QLineEdit, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox, QLabel
from clientSocket import *
from PySide6.QtWidgets import QDialog, QApplication, QWidget, QVBoxLayout, QListView, QLineEdit, QPushButton, QStyledItemDelegate
from PySide6.QtCore import  Qt, QAbstractListModel, QModelIndex, QRect, QSize, QPoint, Signal, QObject
from PySide6.QtGui import  QPainter, QColor, QFont
from datetime import datetime
from PySide6.QtCore import Signal, QObject

class WidgetSignUp(QDialog):
    def __init__(self, client):
        super().__init__()
        self.setWindowTitle("Sign Up")
        self.name = None
        self.passW = None
        self.confirm = None
        self.client = client

        username = QLabel("Username: ")
        self.lineInputUsername = QLineEdit()
        
        passW = QLabel("PassWorld: ")
        self.lineInputPassW = QLineEdit()
        self.lineInputPassW.setEchoMode(QLineEdit.Password)

        passWAgain = QLabel("Confirm: ")
        self.lineInputPassWAgain = QLineEdit()
        self.lineInputPassWAgain.setEchoMode(QLineEdit.Password)
        self.lineInputPassWAgain.returnPressed.connect(self.checkSignUp)

        layOutUserH = QHBoxLayout()
        layOutUserH.addWidget(username)
        layOutUserH.addWidget(self.lineInputUsername)

        layOutPassH = QHBoxLayout()
        layOutPassH.addWidget(passW)
        layOutPassH.addWidget(self.lineInputPassW)

        layOutPassAH = QHBoxLayout()
        layOutPassAH.addWidget(passWAgain)
        layOutPassAH.addWidget(self.lineInputPassWAgain)

        SignUpBtn = QPushButton("Sign Up")
        SignUpBtn.clicked.connect(self.checkSignUp)

        layOutV = QVBoxLayout()
        layOutV.addLayout(layOutUserH)
        layOutV.addLayout(layOutPassH)
        layOutV.addLayout(layOutPassAH)
        layOutV.addWidget(SignUpBtn)
        
        self.setLayout(layOutV)
        
    def checkSignUp(self):
        self.name = self.lineInputUsername.text()
        self.passW = self.lineInputPassW.text()
        self.confirm = self.lineInputPassWAgain.text()
        if not self.name or not self.passW or not self.confirm:
            QMessageBox.information(self, "Sign Up result", "Invalid SignUp!")
            return
        elif self.passW != self.confirm:
            QMessageBox.information(self, "Sign Up result", "confirm passW is not match")
            return
        else:
            self.client.setNamePsw(self.name, self.passW)
            result = self.client.userLoginSignUp("signup")
            QMessageBox.information(self, "Login result", result)
            self.accept()
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

        quitButton = QPushButton("Sign up")
        quitButton.clicked.connect(self.signUp)
        
        self.ContentSplit = QListWidget()
        self.ContentSplit.addItems(["Huy", "Nam", "Linh", "An"])
        self.ContentSplit.hide()

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
        
        leftWidget = QWidget()
        leftWidget.setLayout(layOutV)

        layOutSplit = QSplitter(Qt.Horizontal)
        layOutSplit.addWidget(leftWidget)
        layOutSplit.addWidget(self.ContentSplit)
        
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(layOutSplit)

        self.setLayout(mainLayout)

    
    def CheckValid(self):
        username = self.lineInputUsername.text()
        password = self.lineInputPassW.text()
        self.client.setNamePsw(username, password)
        result = self.client.userLoginSignUp("login")
        QMessageBox.information(self, "Login result", result)
        if self.stack and result == "login successfully":
            self.client.startListenThread() # bat dau thread listen lien tuc
            self.stack.setCurrentIndex(1)
        
    def signUp(self):
        dialog = WidgetSignUp(self.client)
        dialog.exec()

#class WidgetStartChat(QWidget):
#    def __init__(self, app, client, stack=None):
#        super().__init__()
#        self.setWindowTitle("StartChat")
#        self.textEdit = QTextEdit()
#        self.client = client
#        self.client.newMessage.connect(self.displayMessage) # ket noi vao tin hieu cua client listen
#        self.app = app
#        
#        self.viewChat = QTextEdit()
#        self.viewChat.setReadOnly(True)
#        
#        InputText = QLabel("Text her: ")
#        self.lineInputText = QLineEdit()

#        layOutTextH = QHBoxLayout()
#        layOutTextH.addWidget(InputText)
#        layOutTextH.addWidget(self.lineInputText)

#        layOutV = QVBoxLayout()
#        layOutV.addWidget(self.viewChat)
#        layOutV.addLayout(layOutTextH)

#        self.lineInputText.editingFinished.connect(self.EditFinished)

#        self.setLayout(layOutV)

#    def EditFinished(self):
#        self.msg = self.lineInputText.text()
#        self.lineInputText.clear()
#        self.client.sendChat(self.msg)
    
#    def displayMessage(self, msg):
#        self.viewChat.append(msg)


# ---- Model ----
class ChatModel(QAbstractListModel):
    def __init__(self, messages=None):
        super().__init__()
        self.messages = messages or []  # list of dict: {"type": "message"/"date", ...}

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.messages[index.row()]

    def rowCount(self, parent=None):
        return len(self.messages)

    def addMessage(self, msg):
        # check date của tin nhắn trước
        if self.messages:
            lastMsg = self.messages[-1]
            lastDate = lastMsg.get("date") if lastMsg["type"] == "date" else lastMsg.get("time").split(" ")[0]
        else:
            lastDate = None

        todayDate = msg["time"].split(" ")[0]  # dạng dd/mm/yyyy

        # nếu khác ngày thì thêm divider
        if lastDate != todayDate:
            self.beginInsertRows(QModelIndex(), len(self.messages), len(self.messages))
            self.messages.append({"type": "date", "date": todayDate})
            self.endInsertRows()

        # thêm tin nhắn
        self.beginInsertRows(QModelIndex(), len(self.messages), len(self.messages))
        self.messages.append(msg)
        self.endInsertRows()


# ---- Delegate ----
class ChatDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        data = index.data(Qt.DisplayRole)
        if not data:
            return

        painter.save()
        rect = option.rect
        margin = 10
        padding = 8
        maxWidth = 250

        if data["type"] == "date":
            # --- divider ngày ---
            painter.setFont(QFont("Arial", 9, QFont.Bold))
            painter.setPen(QColor("#555"))
            painter.drawText(rect, Qt.AlignCenter, data["date"])
            painter.restore()
            return

        # --- message bubble ---
        text = data["text"]
        sender = data["sender"]
        timeFull = data["time"]
        timeShort = timeFull.split(" ")[1]  # chỉ lấy HH:MM

        # font
        textFont = QFont("Arial", 10)
        timeFont = QFont("Arial", 8)

        # đo text
        painter.setFont(textFont)
        metrics = painter.fontMetrics()
        textRect = metrics.boundingRect(0, 0, maxWidth, 0, Qt.TextWordWrap, text)

        # đo time
        painter.setFont(timeFont)
        timeMetrics = painter.fontMetrics()
        timeRect = timeMetrics.boundingRect(timeShort)

        # bubble rect
        bubbleRect = QRect(0, 0,
                            max(textRect.width(), timeRect.width()) + 2*padding,
                            textRect.height() + timeRect.height() + 3*padding)

        # canh trái/phải theo sender
        if sender == "me":
            bubbleRect.moveTopRight(rect.topRight() - QPoint(margin, 0))
            color = QColor("#A8E6CF")
        else:
            bubbleRect.moveTopLeft(rect.topLeft() + QPoint(margin, 0))
            color = QColor("#D3D3D3")

        # vẽ bubble
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(bubbleRect, 10, 10)

        # text
        painter.setPen(Qt.black)
        painter.setFont(textFont)
        textRect.moveTopLeft(bubbleRect.topLeft() + QPoint(padding, padding))
        painter.drawText(textRect, Qt.TextWordWrap, text)

        # time
        painter.setFont(timeFont)
        painter.setPen(Qt.darkGray)
        timeRect.moveBottomLeft(bubbleRect.bottomLeft() + QPoint(padding, -5))
        painter.drawText(timeRect, timeShort)

        painter.restore()

    def sizeHint(self, option, index):
        data = index.data(Qt.DisplayRole)
        if not data:
            return super().sizeHint(option, index)

        if data["type"] == "date":
            return QSize(100, 25)  # chiều cao divider

        text = data["text"]
        timeShort = data["time"].split(" ")[1]

        metrics = option.fontMetrics
        textRect = metrics.boundingRect(0, 0, 250, 0, Qt.TextWordWrap, text)
        timeRect = metrics.boundingRect(timeShort)

        return textRect.size() + QSize(30, 30 + timeRect.height())


# ---- Window ----
class ChatWindow(QWidget):
    def __init__(self, app, client, stack=None):
        super().__init__()
        self.setWindowTitle("Chat (Divider by Date + Short Time)")
        self.app = app
        self.model = ChatModel([
            {"type": "date", "date": "26/08/2025"},
            {"type": "message", "sender": "me", "text": "Hôm qua nè", "time": "26/08/2025 22:50"},
            {"type": "date", "date": "27/08/2025"},
            {"type": "message", "sender": "other", "text": "Hôm nay mới nè", "time": "27/08/2025 09:10"},
        ])
        self.client = client
        self.client.newMessage.connect(self.recv)
        self.view = QListView()
        self.view.setModel(self.model)
        self.view.setItemDelegate(ChatDelegate())

        self.input = QLineEdit()

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addWidget(self.input)
        self.setLayout(layout)
        self.input.editingFinished.connect(self.EditFinished)
        
#sua lai
    def recv(self, msg):
        text = msg
        if text:
            now = datetime.now().strftime("%d/%m/%Y %H:%M")
            self.model.addMessage({"type": "message", "sender": "me", "text": text, "time": now})
            self.input.clear()
            self.view.scrollToBottom()
# them
    def EditFinished(self):
        self.msg = self.input.text()
        self.input.clear()
        self.client.sendChat(self.msg)

if __name__ == "__main__":
    app = QApplication([])
    win = ChatWindow()
    win.resize(400, 500)
    win.show()
    app.exec()