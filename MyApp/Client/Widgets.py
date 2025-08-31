from PySide6.QtWidgets import QMainWindow, QListWidget, QSplitter, QComboBox, QTabWidget, QAbstractItemView, QListWidget, QRadioButton, QButtonGroup, QCheckBox,QGroupBox,QGridLayout, QSizePolicy, QTextEdit, QLineEdit, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox, QLabel
from clientSocket import *
from PySide6.QtWidgets import QStatusBar, QToolBar, QDialog, QApplication, QWidget, QVBoxLayout, QListView, QLineEdit, QPushButton, QStyledItemDelegate
from PySide6.QtCore import  Qt, QAbstractListModel, QModelIndex, QRect, QSize, QPoint, Signal, QObject
from PySide6.QtGui import  QAction, QPainter, QColor, QFont, QIcon, QPixmap
from datetime import datetime
class WidgetOptionUser(QDialog):
    def __init__(self, client, clientName, namefriend):
        super().__init__()
        self.client = client
        self.setWindowTitle("Option")
        self.namefriend = namefriend
        self.clientName = clientName
        self.client.optionMessage.connect(self.printResut)

        self.username = QLabel(self.namefriend)

        self.addBtn = QPushButton("Add friend")
        self.addBtn.clicked.connect(lambda: self.sendOption("add"))

        self.unfBtn = QPushButton("UnFriend")
        self.unfBtn.clicked.connect(lambda: self.sendOption("unfriend"))

        self.inviteBtn = QPushButton("Invite")
        self.inviteBtn.clicked.connect(lambda: self.sendOption("invite"))


        layoutV = QVBoxLayout()
        layoutV.addWidget(self.username)
        layoutV.addWidget(self.addBtn)
        layoutV.addWidget(self.unfBtn)
        layoutV.addWidget(self.inviteBtn)

        self.setLayout(layoutV)

    def sendOption(self, option):
        asyncio.create_task(self.client.clientSendOption(option, self.clientName, self.namefriend))
    def printResut(self, result):
        QMessageBox.information(self, "Response",result)
        
class WidgetSignUp(QDialog):
    def __init__(self, client):
        super().__init__()
        self.setWindowTitle("Sign Up")
        self.client = client
        self.client.signUpMessage.connect(self.PrintResultSignUp)

        self.username = QLabel("Username: ")
        self.lineInputUsername = QLineEdit()
        
        self.passW = QLabel("PassWorld: ")
        self.lineInputPassW = QLineEdit()
        self.lineInputPassW.setEchoMode(QLineEdit.Password)

        self.passWAgain = QLabel("Confirm: ")
        self.lineInputPassWAgain = QLineEdit()
        self.lineInputPassWAgain.setEchoMode(QLineEdit.Password)
        self.lineInputPassWAgain.returnPressed.connect(self.checkSignUp)

        layOutUserH = QHBoxLayout()
        layOutUserH.addWidget(self.username)
        layOutUserH.addWidget(self.lineInputUsername)

        layOutPassH = QHBoxLayout()
        layOutPassH.addWidget(self.passW)
        layOutPassH.addWidget(self.lineInputPassW)

        layOutPassAH = QHBoxLayout()
        layOutPassAH.addWidget(self.passWAgain)
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
        name = self.lineInputUsername.text()
        passW = self.lineInputPassW.text()
        confirm = self.lineInputPassWAgain.text()
        if not name or not passW or not confirm:
            QMessageBox.information(self, "Sign Up result", "Invalid SignUp!")
            self.username.setStyleSheet("color: red; font-weight: bold;")
            self.passW.setStyleSheet("color: red; font-weight: bold;")
            self.passWAgain.setStyleSheet("color: red; font-weight: bold;")
            return
        elif passW != confirm:
            QMessageBox.information(self, "Sign Up result", "confirm passW is not match")
            self.passW.setStyleSheet("color: red; font-weight: bold;")
            self.passWAgain.setStyleSheet("color: red; font-weight: bold;")
            return
        else:
            self.client.setNamePsw(name, passW)
            asyncio.create_task(self.client.userLoginSignUp("signup"))
            
    def PrintResultSignUp(self, msg):
        result = msg
        QMessageBox.information(self, "SignUp result", result)
        self.accept()

class WidgetLogin(QWidget):
    def __init__(self, app, client, stack=None):
        super().__init__()
        self.setWindowTitle("Login")
        self.app = app
        self.client = client
        self.stack = stack
        self.dialog = None
        self.msg = ""
        self.client.loginMessage.connect(self.PrintResultLogin)

        self.username = QLabel("Username: ")
        self.lineInputUsername = QLineEdit()
        
        self.passW = QLabel("PassWorld: ")
        self.lineInputPassW = QLineEdit()
        self.lineInputPassW.setEchoMode(QLineEdit.Password)
        LoginButton = QPushButton("Login")
        LoginButton.clicked.connect(self.CheckValid)

        quitButton = QPushButton("Sign up")
        quitButton.clicked.connect(self.signUp)

        layOutUserH = QHBoxLayout()
        layOutUserH.addWidget(self.username)
        layOutUserH.addWidget(self.lineInputUsername)

        layOutPassH = QHBoxLayout()
        layOutPassH.addWidget(self.passW)
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
        if not username or not password:
           self.username.setStyleSheet("color: red; font-weight: bold;")
           self.passW.setStyleSheet("color: red; font-weight: bold;")
           return
        else:
            self.client.setNamePsw(username, password)
            asyncio.create_task(self.client.userLoginSignUp("login"))

    def PrintResultLogin(self,msg):
            result = msg
            QMessageBox.information(self, "Login result", result)
            if self.stack and result == "login successfully":
                profile: Profile = self.stack.widget(2)
                profile.setUserInfo(self.lineInputUsername.text())
                profile.updateMenu()
                profile.getFriend()
                self.stack.setCurrentIndex(2)
        
    def signUp(self):
        self.dialog = WidgetSignUp(self.client)
        self.dialog.show()

class Profile(QMainWindow):
    def __init__(self, app, client, stack=None):
        super().__init__()
        self.app = app
        self.setWindowTitle("Profile")
        self.stack = stack
        self.client = client
        self.client.searchMessage.connect(self.showSearch)
        self.client.showFriendMessage.connect(self.showFriend)
        self.chatPrivite = None
        self.friendName = None
        menuBar = self.menuBar()
        self.clientName = None
        self.task = None

        meMenu = menuBar.addMenu(QIcon("image/useraccount"), "&Me")
        SearchAcction = meMenu.addAction(QIcon("image/searchicon"), "Search All")
        SearchAcction.triggered.connect(self.searchFunction)
        
        
        self.userSplit = QListWidget()
        self.userSplit.hide()
        hbox = QHBoxLayout()
        hbox.addWidget(self.userSplit)
        rightWidget = QWidget()      # bọc hbox vào QWidget
        rightWidget.setLayout(hbox)
        
        self.groupBoxR = QGroupBox()
        vboxR = QVBoxLayout()
        vboxR.addWidget(self.userSplit)
        self.groupBoxR.setLayout(vboxR)

        self.friendlist = QListWidget()
        self.friendlist.show()

        rightWidget = QWidget()
        rightLayout = QVBoxLayout()
        rightLayout.addWidget(self.groupBoxR)
        rightWidget.setLayout(rightLayout)
        
        self.groupBoxR.setFlat(True)

        btnBack = QPushButton("BackToMainChat")
        btnBack.clicked.connect(self.backToMainChat)

        groupBox = QGroupBox("Friends")
        vbox = QVBoxLayout()
        vbox.addWidget(self.friendlist)
        vbox.addWidget(btnBack)
        groupBox.setLayout(vbox)

        leftWidget = QWidget()
        leftLayout = QVBoxLayout()
        leftLayout.addWidget(groupBox)
        leftWidget.setLayout(leftLayout)


        self.layOutSplit = QSplitter(Qt.Horizontal)
        self.layOutSplit.addWidget(leftWidget)
        self.layOutSplit.addWidget(rightWidget)

        self.userSplit.itemClicked.connect(self.itemClicked)
        self.friendlist.itemClicked.connect(self.connectPrivitedChat)
        # working with status bars
        #self.setStatusBar(QStatusBar(self))
        self.setCentralWidget(self.layOutSplit)

    def setUserInfo(self, name: str):
        self.clientName = name

    def updateMenu(self):
        mb = self.menuBar()
        mb.clear()
        meMenu = mb.addMenu(QIcon("image/useraccount"), "&Me")
        searchAction = meMenu.addAction(QIcon("image/searchicon"), "Search All")
        searchAction.triggered.connect(self.searchFunction)
        # chỉ add menu tên khi có string hợp lệ
        if self.clientName:
            mb.addMenu(str(self.clientName))

    def searchFunction(self):
        asyncio.create_task(self.client.searchUser("Search", name=None))
    
    def showSearch(self, users):
        self.layOutSplit.setSizes([50, 150])
        self.userSplit.clear()
        print("Received users:", users)
        self.userSplit.addItem("Search Result")
        self.userSplit.addItems(users)
        self.userSplit.show()
        self.groupBoxR.setFlat(False)
    #----- show friend ------
    def getFriend(self):
        self.task = asyncio.create_task(self.client.clientShowFriend("showfriend", self.clientName))
      
    def showFriend(self, users):
        self.friendlist.clear()
        self.friendlist.addItems(users)
        self.task.cancel()
    #------------------------------

    #------ handle event ------------
    def itemClicked(self, item):
        username = item.text()
        if username == "Search Result":
            return
        option = WidgetOptionUser(self.client, self.clientName, username)
        option.setModal(True) 
        option.show()

    def connectPrivitedChat(self, item):
        self.friendName = item.text()
        self.chatPrivite = ChatWindow(self.app, self.client, self.clientName, self.friendName, privite=True)
        self.chatPrivite.show()
        
    def backToMainChat(self):
        self.stack.setCurrentIndex(1)
    
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
    def __init__(self, app, client, clientName=None, recvName=None, privite=False, stack=None):
        super().__init__()
        self.setWindowTitle(recvName)
        self.app = app
        self.privite = privite
        self.clientName = clientName
        self.recvName = recvName

        self.model = ChatModel([
            {"type": "date", "date": "26/08/2025"},
            {"type": "message", "sender": "me", "text": "Hôm qua nè", "time": "26/08/2025 22:50"},
            {"type": "date", "date": "27/08/2025"},
            {"type": "message", "sender": "other", "text": "Hôm nay mới nè", "time": "27/08/2025 09:10"},
        ])
        self.client = client

        if not self.privite:
           self.client.newMessage.connect(self.recv)
        else:
            self.client.priviteChatMessage.connect(self.recv)

        self.view = QListView()
        self.view.setModel(self.model)
        self.view.setItemDelegate(ChatDelegate())

        self.input = QLineEdit()
        self.imageSend = QLabel()
        self.imageSend.setPixmap(QPixmap("image/send"))
        self.imageSend.setFixedSize(32, 32) 
        self.imageSend.setScaledContents(True)

        layoutH = QHBoxLayout()
        layoutH.addWidget(self.input)
        layoutH.addWidget(self.imageSend)

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addLayout(layoutH)

        self.setLayout(layout)
        self.input.editingFinished.connect(self.EditFinished)
        
    def sendMess(self, msg):
        text = msg
        if text:
            now = datetime.now().strftime("%d/%m/%Y %H:%M")
            self.model.addMessage({"type": "message", "sender": "me", "text": text, "time": now})
            self.input.clear()
            self.view.scrollToBottom()

    def recv(self, msg,sender=None):
        print("Da nhan duoc tin nhan")
        print(msg)
        print(sender)
        text = msg
        if sender is None:
            if text:
                now = datetime.now().strftime("%d/%m/%Y %H:%M")
                self.model.addMessage({"type": "message", "sender": "friend", "text": text, "time": now})
                self.input.clear()
                self.view.scrollToBottom() 
        else:
            if text:
                now = datetime.now().strftime("%d/%m/%Y %H:%M")
                self.model.addMessage({"type": "message", "sender": "friend", "text": text, "time": now})
                self.input.clear()
                self.view.scrollToBottom() 
        
# them
    def EditFinished(self):
        self.msg = self.input.text()
        self.sendMess(self.msg)
        self.input.clear()
       # gui server
        if not self.privite:
            asyncio.create_task(self.client.sendChat("message",self.msg))
        else:
            asyncio.create_task(self.client.sendPriviteChat(self.clientName,self.recvName,self.msg))
