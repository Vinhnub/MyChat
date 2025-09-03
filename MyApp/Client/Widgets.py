from PySide6.QtWidgets import QMainWindow, QListWidget, QSplitter, QComboBox, QTabWidget, QAbstractItemView, QListWidget, QRadioButton, QButtonGroup, QCheckBox,QGroupBox,QGridLayout, QSizePolicy, QTextEdit, QLineEdit, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox, QLabel
from clientSocket import *
from PySide6.QtWidgets import QStackedWidget, QListWidgetItem, QStatusBar, QToolBar, QDialog, QApplication, QWidget, QVBoxLayout, QListView, QLineEdit, QPushButton, QStyledItemDelegate
from PySide6.QtCore import  Qt, QAbstractListModel, QModelIndex, QRect, QSize, QPoint, Signal, QObject
from PySide6.QtGui import  QAction, QPainter, QColor, QFont, QIcon, QPixmap
from datetime import datetime

class WidgetCreateGroup(QDialog):
    def __init__(self, client, clientname):
        super().__init__()
        self.setWindowTitle("Create Group")
        self.userAdded = []
        self.name = ""
        self.client = client
        self.clientName = clientname

        self.client.searchMessage.connect(self.showAllUser)
        self.client.createGroupMessage.connect(self.showResult)

        labelGroupN = QLabel("Group Name:")
        self.lineGroupN = QLineEdit()
        self.lineGroupN.editingFinished.connect(self.setNameGroup)

        layoutNH = QHBoxLayout()
        layoutNH.addWidget(labelGroupN)
        layoutNH.addWidget(self.lineGroupN)

        self.listWidget = QListWidget(self)
        self.listWidget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.listWidget.itemClicked.connect(self.saveSelection)
        
        self.createBtn = QPushButton("Create")
        self.createBtn.setAutoDefault(False)
        self.createBtn.setDefault(False)
        self.createBtn.clicked.connect(self.createGroup)
        
        vlayout = QVBoxLayout()
        vlayout.addLayout(layoutNH)
        vlayout.addWidget(self.listWidget)
        vlayout.addWidget(self.createBtn)
        self.setLayout(vlayout)

    def setNameGroup(self):
        self.name = self.lineGroupN.text()
        self.showAllUserFunction()

    def saveSelection(self, item):
        if item.text() in self.userAdded:
            self.userAdded.remove(item.text())
        else:
            self.userAdded.append(item.text())

    def createGroup(self):
        asyncio.create_task(self.client.createGroup(self.clientName, self.name, self.userAdded))
        
    def showAllUserFunction(self):
        asyncio.create_task(self.client.searchUser("Search", name=None))

    def showAllUser(self, list):
        self.listWidget.clear()
        self.listWidget.addItems(list)

    def showResult(self,result):
        if result == "CreateGroup successfully":
           QMessageBox.information(self, "Response",result)
        else:
            QMessageBox.information(self, "Response",result)


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

class WidgetSearchResult(QDialog):
    def __init__(self,client,clientName, users):
        super().__init__()
        self.setWindowTitle("SearchResult")
        self.client = client
        self.clientName = clientName
        self.users = users
        self.resize(100, 150)
        self.listWidget = QListWidget()
        self.listWidget.addItem("Search Result")
        for user in self.users:
            self.listWidget.addItem(user)

        self.listWidget.itemClicked.connect(self.itemClicked)
        self.layOutV = QVBoxLayout()
        self.layOutV.addWidget(self.listWidget)

        self.setLayout(self.layOutV)


    def itemClicked(self, item):
        username = item.text()
        if username == "Search Result":
            return
        option = WidgetOptionUser(self.client, self.clientName, username)
        option.setModal(True) 
        option.show() 

class Profile(QMainWindow):
    def __init__(self, app, client, stack=None):
        super().__init__()
        self.app = app
        self.setWindowTitle("Profile")
        self.stack = stack
        self.client = client
        self.client
#        self.client.searchMessage.connect(self.showSearch)
        self.client.showFriendMessage.connect(self.showFriend)
        self.client.updateStatusMessage.connect(self.updateStatus)
        self.client.updateLastMessage.connect(self.updateNewMess)

        self.dialog = None
        self.groups = None
        self.clicked = None
        self.friendOnl = None
        self.chatStack = QStackedWidget()
        self.chats = {}

        self.friendName = None
        menuBar = self.menuBar()
        self.clientName = None
        self.listFriendUser = []

        meMenu = menuBar.addMenu(QIcon("image/useraccount"), "&Me")
        SearchAcction = meMenu.addAction(QIcon("image/searchicon"), "Search All")
        SearchAcction.triggered.connect(self.searchFunction)

        # --- Friend list ---
        self.friendlist = QListWidget()
        self.friendlist.setFixedWidth(150)   # fix ngang 50, cao tự giãn theo cửa sổ

        btnBack = QPushButton("BackToMainChat")
        btnBack.setFixedWidth(80)
        btnBack.clicked.connect(self.backToMainChat)

        createGroup = QPushButton("createGroup")
        createGroup.setFixedWidth(80)
        createGroup.clicked.connect(self.createGroup)

        layoutH = QHBoxLayout()
        layoutH.addWidget(btnBack)
        layoutH.addWidget(createGroup)

        leftWidget = QWidget()
        leftLayout = QVBoxLayout()
        leftLayout.addWidget(self.friendlist)
        leftLayout.addLayout(layoutH)
        leftWidget.setLayout(leftLayout)

        # --- Splitter chính ---
        self.layOutSplit = QSplitter(Qt.Horizontal)
        self.layOutSplit.addWidget(leftWidget)
        self.layOutSplit.addWidget(self.chatStack)
        self.layOutSplit.setSizes([150, 600])

        # click item -------------------------------------
        self.setCentralWidget(self.layOutSplit)

        self.friendlist.itemClicked.connect(self.connectPrivitedChat)
        # working with status bars
        #self.setStatusBar(QStatusBar(self))

        self.iconOn = QPixmap("image/onlineicon").scaled(16, 16)
        self.iconOff = QPixmap("image/offlineicon").scaled(16,16)
        self.iconGroup = QPixmap("image/groupicon").scaled(16,16)
#        self.onlineIcon = QIcon(iconOn)
#        self.offlineIcon = QIcon(iconOff)

        self.setCentralWidget(self.layOutSplit)

    def setUserInfo(self, name: str):
        self.clientName = name

    def updateMenu(self):
        mb = self.menuBar()
        mb.clear()
        meMenu = mb.addMenu(QIcon("image/useraccount"), "&Me")
        searchAction = meMenu.addAction(QIcon("image/searchicon"), "Search All")
        searchAction.triggered.connect(self.searchFunction)
        if self.clientName:
            menuf5 = mb.addMenu(str(self.clientName))
            f5Action = menuf5.addAction(QIcon("image/f5icon"), "Refresh")
            f5Action.triggered.connect(self.getFriend)

    # ---------- show search -----------
    def searchFunction(self):
        asyncio.create_task(self.client.searchUser("Search", name=None))
    
    def showSearch(self, users):
        self.dialog = WidgetSearchResult(self.client,self.clientName,users)
        self.dialog.show()

    #----- show friend ------
    def getFriend(self):
        asyncio.create_task(self.client.clientShowFriend("showfriend", self.clientName))
    
    def showFriend(self, users, groups):
        self.listFriendUser = users
        self.groups = groups
        self.friendlist.clear()
        self.friendlist.addItems(users)
        self.friendlist.addItem("Groups:")
        self.friendlist.addItems(groups)

        asyncio.create_task(self.client.getUserOnl(users))

    def updateStatus(self,friendsOnl):   
        self.friendlist.clear()
        listFriendUser = self.listFriendUser
        self.friendlist.addItem("--Friends--")  
        self.friendOnl = friendsOnl
        if not friendsOnl:
            for f in listFriendUser:
                item = QListWidgetItem()
                widget = QWidget()
                layout = QVBoxLayout(widget)
                
                labelFriend = QLabel()
                labelFriend.setObjectName("icon")

                labelLastChat = QLabel("last msg:...")
                labelLastChat.setObjectName("lastMsg")

                labelFriend.setPixmap(self.iconOff)
                labelNameFriend = QLabel(f)
                labelNameFriend.setObjectName("friendName")

                layoutHFriend = QHBoxLayout()
                layoutHFriend.setSpacing(2)                   
                layoutHFriend.setContentsMargins(0, 0, 0, 0)   
                layoutHFriend.addWidget(labelFriend)
                layoutHFriend.addWidget(labelNameFriend)
                
                 
                layout.addLayout(layoutHFriend)
                layout.addWidget(labelLastChat)

                self.friendlist.addItem(item)
                self.friendlist.setItemWidget(item, widget)
                
                widget.setLayout(layout)
                # Gắn widget vào item
                item.setSizeHint(widget.sizeHint())  

            self.friendlist.addItem("--Groups--")
            for f in self.groups:
                item = QListWidgetItem()
                widget = QWidget()
                layout = QVBoxLayout(widget)
                
                labelFriend = QLabel()
                labelFriend.setObjectName("icon")

                labelLastChat = QLabel("last msg:...")
                labelLastChat.setObjectName("lastMsg")

                labelFriend.setPixmap(self.iconGroup)
                labelNameFriend = QLabel(f)
                labelNameFriend.setObjectName("friendName")

                layoutHFriend = QHBoxLayout()
                layoutHFriend.setSpacing(2)                    
                layoutHFriend.setContentsMargins(0, 0, 0, 0)   
                layoutHFriend.addWidget(labelFriend)
                layoutHFriend.addWidget(labelNameFriend)
                
                 
                layout.addLayout(layoutHFriend)
                layout.addWidget(labelLastChat)

                self.friendlist.addItem(item)
                self.friendlist.setItemWidget(item, widget)
                
                widget.setLayout(layout)
                # Gắn widget vào item
                item.setSizeHint(widget.sizeHint())
        else:
            for f in friendsOnl:
                item = QListWidgetItem()
                widget = QWidget()
                layout = QVBoxLayout(widget)
               
                labelFriend = QLabel()
                labelLastChat = QLabel("lastmsg:......")
                labelLastChat.setObjectName("lastMsg")

                labelFriend.setPixmap(self.iconOn)
                labelFriend.setObjectName("icon")

                labelNameFriend = QLabel(f)
                labelNameFriend.setObjectName("friendName")

                layoutHFriend = QHBoxLayout()
                layoutHFriend.setSpacing(2)                
                layoutHFriend.setContentsMargins(0, 0, 0, 0)   
                layoutHFriend.addWidget(labelFriend)
                layoutHFriend.addWidget(labelNameFriend)
                layoutHFriend.setSpacing(2)
                    
                layout.addLayout(layoutHFriend)
                layout.addWidget(labelLastChat)

                self.friendlist.addItem(item)
                self.friendlist.setItemWidget(item, widget)
                widget.setLayout(layout)
                # Gắn widget vào item
                item.setSizeHint(widget.sizeHint())

                listFriendUser.remove(f)

            for f in listFriendUser:
                item = QListWidgetItem()
                widget = QWidget()
                layout = QVBoxLayout(widget)

                labelFriend = QLabel()
                labelLastChat = QLabel("last msg:...")
                labelLastChat.setObjectName("lastMsg")

                labelFriend.setPixmap(self.iconOff)
                labelFriend.setObjectName("icon")

                labelNameFriend = QLabel(f)
                labelNameFriend.setObjectName("friendName")

                layoutHFriend = QHBoxLayout()
                layoutHFriend.setSpacing(2)                    
                layoutHFriend.setContentsMargins(0, 0, 0, 0)   
                layoutHFriend.addWidget(labelFriend)
                layoutHFriend.addWidget(labelNameFriend)
                 
                layout.addLayout(layoutHFriend)
                layout.addWidget(labelLastChat)

                self.friendlist.addItem(item)
                self.friendlist.setItemWidget(item, widget)
                widget.setLayout(layout)
                # Gắn widget vào item
                item.setSizeHint(widget.sizeHint())
            self.friendlist.addItem("--Groups--")
            for f in self.groups:
                item = QListWidgetItem()
                widget = QWidget()
                layout = QVBoxLayout(widget)
                
                labelFriend = QLabel()
                labelLastChat = QLabel("last msg:...")
                labelLastChat.setObjectName("lastMsg")

                labelFriend.setPixmap(self.iconGroup)
                labelNameFriend = QLabel(f)
                labelNameFriend.setObjectName("friendName")

                layoutHFriend = QHBoxLayout()
                layoutHFriend.setSpacing(2)             
                layoutHFriend.setContentsMargins(0, 0, 0, 0)   
                layoutHFriend.addWidget(labelFriend)
                layoutHFriend.addWidget(labelNameFriend)
                 
                layout.addLayout(layoutHFriend)
                layout.addWidget(labelLastChat)

                self.friendlist.addItem(item)
                self.friendlist.setItemWidget(item, widget)
                
                widget.setLayout(layout)
                # Gắn widget vào item
                item.setSizeHint(widget.sizeHint())

    #------ handle event ------------
    def connectPrivitedChat(self, item):
        widget = self.friendlist.itemWidget(item)
        if widget:
            self.friendName = widget.findChild(QLabel, "friendName").text()
        if self.friendName != "--Friends--" and self.friendName != "--Groups--":
            if self.friendName in self.chats:
               index = self.chatStack.indexOf(self.chats[self.friendName])
               self.chatStack.setCurrentIndex(index)
            else:
                if self.friendName in self.groups:
                    chatPrivite = ChatWindow(self.app, self.client, self.clientName, self.friendName, group=True)
                else:
                    chatPrivite = ChatWindow(self.app, self.client, self.clientName, self.friendName, privite=True)
                self.chatStack.addWidget(chatPrivite)
                self.chatStack.setCurrentWidget(chatPrivite)
                self.chats[self.friendName] = chatPrivite
        else:
            return
        
    def updateNewMess(self, mess, sender,group):
        if group == "":
            for i in range(self.friendlist.count()):
                item = self.friendlist.item(i)
                widget = self.friendlist.itemWidget(item)
                if not widget:
                    continue
                friendName = widget.findChild(QLabel, "friendName").text()
                if friendName == sender:
                    lastMsgLabel = widget.findChild(QLabel, "lastMsg")
                    refreshIcon = widget.findChild(QLabel,"icon")
                    refreshIcon.setPixmap(self.iconOn)
                    if lastMsgLabel:
                        lastMsgLabel.setText(f"last msg: {mess}")  # cập nhật tin nhắn cuối
                    break
        else:
            for i in range(self.friendlist.count()):
                item = self.friendlist.item(i)
                widget = self.friendlist.itemWidget(item)
                if not widget:
                    continue
                friendName = widget.findChild(QLabel, "friendName").text()
                if friendName == group:
                    lastMsgLabel = widget.findChild(QLabel, "lastMsg")
                    if lastMsgLabel:
                        lastMsgLabel.setText(f"last msg: {mess}")  # cập nhật tin nhắn cuối
                    break



        

#    def checkMess(self, item):
#        widget = self.friendList.itemWidget(item)
#        if widget:
#           name_label = widget.findChild(QLabel) 
#           namecheck = name_label.text()
#        for f in self.friendOnl:
#           if f == namecheck:

            
        
    def backToMainChat(self):
        self.stack.setCurrentIndex(1)

    def createGroup(self):
        self.dialog = WidgetCreateGroup(self.client, self.clientName)
        self.dialog.exec()

    
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
    def __init__(self, app, client, clientName=None, recvName=None, privite=False,group=False, stack=None):
        super().__init__()
        self.setWindowTitle(recvName)
        self.app = app
        self.privite = privite
        self.group = group 
        self.clientName = clientName
        self.recvName = recvName

        self.model = ChatModel([
            {"type": "date", "date": "26/08/2025"},
            {"type": "message", "sender": "me", "text": "Hôm qua nè", "time": "26/08/2025 22:50"},
            {"type": "date", "date": "27/08/2025"},
            {"type": "message", "sender": "other", "text": "Hôm nay mới nè", "time": "27/08/2025 09:10"},
        ])
        self.client = client

        if not self.privite and not self.group:
           self.client.newMessage.connect(self.recv)
        elif self.group:
            self.client.groupChatMessage.connect(self.recv)
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

    def recv(self, msg,sender,group):
        print("Da nhan duoc tin nhan")
        print(msg)
        print(sender)
        text = msg
        if group == "" and sender == "":
            if text:
                now = datetime.now().strftime("%d/%m/%Y %H:%M")
                self.model.addMessage({"type": "message", "sender": "friend", "text": text, "time": now})
                self.input.clear()
                self.view.scrollToBottom() 
        elif group != "":
            if group != self.recvName:
                return 
            if text:
                now = datetime.now().strftime("%d/%m/%Y %H:%M")
                self.model.addMessage({"type": "message", "sender": "friend", "text": text, "time": now})
                self.input.clear()
                self.view.scrollToBottom() 
        else:
            if sender != self.recvName:
                return 
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
        if not self.privite and not self.group:
            asyncio.create_task(self.client.sendChat("message",self.msg))
        elif self.group:
            asyncio.create_task(self.client.sendGroupChat(self.clientName,self.recvName,self.msg))
        else:
            asyncio.create_task(self.client.sendPriviteChat(self.clientName,self.recvName,self.msg))
