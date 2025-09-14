from PySide6.QtWidgets import (QWidget,  QLabel, QHBoxLayout,
                                QVBoxLayout, QPushButton, QLineEdit,
                                QFormLayout, QGridLayout, QStatusBar,
                                QMessageBox, QListWidget)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from chat_model import *
from list_group import *
from current_group_widget import *
from user_profile import *
from list_member import *
from list_member_call import *

class StartWindow(QWidget):
    def __init__(self, app, main):
        super().__init__()
        self.app = app
        self.main = main
        self.setWindowTitle("MyChat")

        layout = QVBoxLayout()
        label = QLabel("Welcome to MyChat")
        signInBtn = QPushButton("Sign in")
        signUpBtn = QPushButton("Sign up")
        exitBtn = QPushButton("Exit")

        label.setFont(QFont('Arial', 16))
        signInBtn.setFont(QFont('Arial', 10))
        signUpBtn.setFont(QFont('Arial', 10))
        exitBtn.setFont(QFont('Arial', 10))

        signInBtn.clicked.connect(self.signInBtnClicked)
        signUpBtn.clicked.connect(self.signUpBtnClicked)
        exitBtn.clicked.connect(self.exit)

        layout.addWidget(label)
        layout.addWidget(signInBtn)
        layout.addWidget(signUpBtn)
        layout.addWidget(exitBtn)

        self.setLayout(layout)

    def signInBtnClicked(self):
        self.main.secondWindow = SignInWindow(self.app, self.main)
        self.main.secondWindow.show()

    def signUpBtnClicked(self):
        self.main.secondWindow = SignUpWindow(self.app, self.main)
        self.main.secondWindow.show()

    def exit(self):
        self.app.quit()

    def closeEvent(self, event):
        self.app.quit()
        event.accept()

class SignInWindow(QWidget):
    def __init__(self, app, main):
        super().__init__()
        self.app = app
        self.main = main
        self.setWindowTitle("Sign in")

        label = QLabel("Sign in")
        label.setFont(QFont('Arial', 16))
        label.setAlignment(Qt.AlignCenter)

        entryLayout = QFormLayout()
        self.usernameEntry = QLineEdit()
        self.passwordEntry = QLineEdit()
        usernameLabel = QLabel("Username:")
        passwordLabel = QLabel("Password:")
        usernameLabel.setFont(QFont('Arial', 10))
        passwordLabel.setFont(QFont('Arial', 10))
        entryLayout.addRow(usernameLabel, self.usernameEntry)
        entryLayout.addRow(passwordLabel, self.passwordEntry)
        
        btnLayout = QHBoxLayout()
        enterBtn = QPushButton("Enter")
        cancelBtn = QPushButton("Cancel")
        enterBtn.setFont(QFont('Arial', 10))
        cancelBtn.setFont(QFont('Arial', 10))

        enterBtn.clicked.connect(self.enterClicked)
        cancelBtn.clicked.connect(self.cancelClicked)
        btnLayout.addWidget(cancelBtn)
        btnLayout.addWidget(enterBtn)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addLayout(entryLayout)
        layout.addLayout(btnLayout)
        
        self.setLayout(layout)

    def cancelClicked(self):
        self.close()

    def enterClicked(self):
        if self.usernameEntry.text() == "" or self.passwordEntry.text() == "":
            return
        self.main.signIn(self.usernameEntry.text(), self.passwordEntry.text())

    def showError(self):
        ret = QMessageBox.critical(self,"Error", "Something is wrong!", QMessageBox.Ok)
        if ret == QMessageBox.Ok:
            pass

class SignUpWindow(QWidget):
    def __init__(self, app, main):
        super().__init__()
        self.app = app
        self.main = main
        self.setWindowTitle("Sign up")

        label = QLabel("Sign up")
        label.setFont(QFont('Arial', 16))
        label.setAlignment(Qt.AlignCenter)

        entryLayout = QFormLayout()
        self.fullnameEntry = QLineEdit()
        self.usernameEntry = QLineEdit()
        self.passwordEntry = QLineEdit()
        fullnameLabel = QLabel("Fullname:")
        usernameLabel = QLabel("Username:")
        passwordLabel = QLabel("Password:")
        fullnameLabel.setFont(QFont('Arial', 10))
        usernameLabel.setFont(QFont('Arial', 10))
        passwordLabel.setFont(QFont('Arial', 10))
        entryLayout.addRow(fullnameLabel, self.fullnameEntry)
        entryLayout.addRow(usernameLabel, self.usernameEntry)
        entryLayout.addRow(passwordLabel, self.passwordEntry)
        
        btnLayout = QHBoxLayout()
        enterBtn = QPushButton("Enter")
        cancelBtn = QPushButton("Cancel")
        enterBtn.setFont(QFont('Arial', 10))
        cancelBtn.setFont(QFont('Arial', 10))

        enterBtn.clicked.connect(self.enterClicked)
        cancelBtn.clicked.connect(self.cancelClicked)
        btnLayout.addWidget(cancelBtn)
        btnLayout.addWidget(enterBtn)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addLayout(entryLayout)
        layout.addLayout(btnLayout)
        
        self.setLayout(layout)

    def cancelClicked(self):
        self.main.secondWindow = None

    def enterClicked(self):
        if self.fullnameEntry.text() == "" or self.usernameEntry.text() == "" or self.passwordEntry.text() == "":
            return 
        self.main.signUp(self.fullnameEntry.text(), self.usernameEntry.text(), self.passwordEntry.text())

    def showError(self):
        ret = QMessageBox.critical(self,"Error", "Username already exists!", QMessageBox.Ok)
        if ret == QMessageBox.Ok:
            pass
            
    def showSuccess(self):
        ret = QMessageBox.information(self, "Success", "Create account successfuly", QMessageBox.Ok)
        if ret == QMessageBox.Ok:
            self.close()


class ChatWindow(QWidget):
    def __init__(self, app, main, data, dataFilter):
        super().__init__()
        self.setWindowTitle("My Chat")
        self.setFixedHeight(700)
        self.data = data
        self.app = app
        self.main = main
        self.chatWidget = ChatWidget(self, dataFilter, data["data"]["username"])
        self.listGroup = ListGroups(self, dataFilter)
        self.createGroupBtn = QPushButton("Create group")
        self.joinGroupBtn = QPushButton("Join group")
        self.logoutBtn = QPushButton("Log out")
        self.userProfile = UserProfileWidget(data["data"]["userFullName"])
        indexGroup = next(iter(dataFilter)) if dataFilter else ""
        self.currentGroup = CurrentGroupWidget(data["data"]["groups"][indexGroup]["groupDes"] if indexGroup != "" else "")
        self.listMember = ListMemberWidget(self, data["data"]["groups"][indexGroup]["members"] if indexGroup != "" else None)
        self.callBtn = QPushButton("Call")

        self.callBtn.setFixedWidth(250)
        self.callBtn.setFixedHeight(42)
        
        self.logoutBtn.clicked.connect(self.logout)
        self.createGroupBtn.clicked.connect(self.createGroup)
        self.joinGroupBtn.clicked.connect(self.joinGroup)
        self.callBtn.clicked.connect(self.call)

        self.chatLayout = QHBoxLayout()
        self.chatLayout.addWidget(self.listGroup)
        self.chatLayout.addWidget(self.chatWidget)
        self.chatLayout.addWidget(self.listMember)
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.createGroupBtn)
        buttonLayout.addWidget(self.joinGroupBtn)
        buttonLayout.addWidget(self.logoutBtn)
        infoLayout = QHBoxLayout()
        infoLayout.addWidget(self.userProfile)
        infoLayout.addWidget(self.currentGroup)
        infoLayout.addWidget(self.callBtn)
        layout = QVBoxLayout()
        layout.addLayout(infoLayout)
        layout.addLayout(self.chatLayout)
        layout.addLayout(buttonLayout)
        
        self.setLayout(layout)

    def call(self):
        self.main.call(self.data["data"]["username"], self.chatWidget.model.currentGroup)

    def sendMessage(self, msg):
        self.main.sendMessage(msg)

    def recvMessage(self, msg):
        self.chatWidget.recvMessage(msg)
        self.listGroup.moveToTop(msg["groupName"], msg["mesContent"], self.data["data"]["username"] == msg["userName"])

    def logout(self):
        ret = QMessageBox.question(self,"Log out",
                                        "Log out?",
                                        QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.Yes : 
            self.main.logout(self.data["data"]["username"])

    def createGroup(self):
        self.main.secondWindow = CreateGroupWindow(self.app, self.main, self.data["data"]["username"])
        self.main.secondWindow.show()

    def joinGroup(self):
        self.main.secondWindow = JoinGroupWindow(self.app, self.main, self.data["data"]["username"])
        self.main.secondWindow.show()

    def addGroup(self, data):
        groupName = next(iter(data))
        self.data["data"]["groups"][groupName] = data[groupName] 
        self.chatWidget.addGroup(data)
        self.listGroup.addGroup(data)

    def switchCurrentGroup(self, groupName):
        self.currentGroup.switchGroup(self.data["data"]["groups"][groupName]["groupDes"])

    def switchListMember(self, groupName):
        index = self.chatLayout.indexOf(self.listMember)
        self.chatLayout.removeWidget(self.listMember)
        self.listMember.deleteLater()
        self.listMember = ListMemberWidget(self, self.data["data"]["groups"][groupName]["members"])
        self.chatLayout.insertWidget(index, self.listMember)

    def closeEvent(self, event):
        if self.main.secondWindow is not None and self.main.isRunningCall:
            self.main.leaveCall(self.main.user.username, self.main.secondWindow.groupName)
            self.main.secondWindow.close()
        event.accept()

class CreateGroupWindow(QWidget):
    def __init__(self, app, main, myName):
        super().__init__()
        self.app = app
        self.main = main
        self.myName = myName
        self.setWindowTitle("Create group")

        label = QLabel("Create group")
        label.setFont(QFont('Arial', 16))
        label.setAlignment(Qt.AlignCenter)

        entryLayout = QFormLayout()
        self.groupDes = QLineEdit()
        self.groupName = QLineEdit()
        self.groupPassword = QLineEdit()
        groupDesLabel = QLabel("Group des:")
        groupNameLabel = QLabel("Group name:")
        groupPasswordLabel = QLabel("Password:")
        groupDesLabel.setFont(QFont('Arial', 10))
        groupNameLabel.setFont(QFont('Arial', 10))
        groupPasswordLabel.setFont(QFont('Arial', 10))
        entryLayout.addRow(groupDesLabel, self.groupDes)
        entryLayout.addRow(groupNameLabel, self.groupName)
        entryLayout.addRow(groupPasswordLabel, self.groupPassword)
        
        btnLayout = QHBoxLayout()
        enterBtn = QPushButton("Enter")
        cancelBtn = QPushButton("Cancel")
        enterBtn.setFont(QFont('Arial', 10))
        cancelBtn.setFont(QFont('Arial', 10))

        enterBtn.clicked.connect(self.enterClicked)
        cancelBtn.clicked.connect(self.cancelClicked)
        btnLayout.addWidget(cancelBtn)
        btnLayout.addWidget(enterBtn)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addLayout(entryLayout)
        layout.addLayout(btnLayout)
        
        self.setLayout(layout)

    def cancelClicked(self):
        self.main.secondWindow = None

    def enterClicked(self):
        if self.groupDes.text() == "" or self.groupName.text() == "" or self.groupPassword.text() == "":
            return 
        self.main.createGroup(self.groupDes.text(), self.groupName.text(), self.groupPassword.text(), self.myName)

    def showError(self):
        ret = QMessageBox.critical(self,"Error", "Group name already exists!", QMessageBox.Ok)
        if ret == QMessageBox.Ok:
            pass
            
    def showSuccess(self):
        ret = QMessageBox.information(self, "Success", "Create group successfuly", QMessageBox.Ok)
        if ret == QMessageBox.Ok:
            self.close()
    pass

class JoinGroupWindow(QWidget):
    def __init__(self, app, main, myName):
        super().__init__()
        self.app = app
        self.main = main
        self.myName = myName
        self.setWindowTitle("Join group")

        label = QLabel("Join group")
        label.setFont(QFont('Arial', 16))
        label.setAlignment(Qt.AlignCenter)

        entryLayout = QFormLayout()
        self.groupNameEntry = QLineEdit()
        self.passwordEntry = QLineEdit()
        groupNameLabel = QLabel("Group name:")
        passwordLabel = QLabel("Password:")
        groupNameLabel.setFont(QFont('Arial', 10))
        passwordLabel.setFont(QFont('Arial', 10))
        entryLayout.addRow(groupNameLabel, self.groupNameEntry)
        entryLayout.addRow(passwordLabel, self.passwordEntry)
        
        btnLayout = QHBoxLayout()
        enterBtn = QPushButton("Enter")
        cancelBtn = QPushButton("Cancel")
        enterBtn.setFont(QFont('Arial', 10))
        cancelBtn.setFont(QFont('Arial', 10))

        enterBtn.clicked.connect(self.enterClicked)
        cancelBtn.clicked.connect(self.cancelClicked)
        btnLayout.addWidget(cancelBtn)
        btnLayout.addWidget(enterBtn)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addLayout(entryLayout)
        layout.addLayout(btnLayout)
        
        self.setLayout(layout)

    def cancelClicked(self):
        self.close()

    def enterClicked(self):
        if self.groupNameEntry.text() == "" or self.passwordEntry.text() == "":
            return
        self.main.joinGroup(self.groupNameEntry.text(), self.passwordEntry.text(), self.myName)

    def showError(self):
        ret = QMessageBox.critical(self,"Error", "Something is wrong!", QMessageBox.Ok)
        if ret == QMessageBox.Ok:
            pass

class CallWindow(QWidget):
    def __init__(self, app, main, data, groupName):
        super().__init__()
        self.setWindowTitle(f"Call {groupName}")
        self.app = app
        self.main = main
        self.groupName = groupName

        self.listMember = ListMemberCallWidget(self, data)
        self.micMutedBtn = QPushButton("Mute mic")
        self.speakerMutedBtn = QPushButton("Mute speaker")
        self.leaveBtn = QPushButton("Leave")

        self.micMutedBtn.clicked.connect(self.mic)
        self.speakerMutedBtn.clicked.connect(self.speaker)
        self.leaveBtn.clicked.connect(self.leave)

        layout = QVBoxLayout()
        SMLayout = QHBoxLayout()
        SMLayout.addWidget(self.micMutedBtn)
        SMLayout.addWidget(self.speakerMutedBtn)
        layout.addWidget(self.listMember)
        layout.addLayout(SMLayout)
        layout.addWidget(self.leaveBtn)
        
        self.setLayout(layout)

    def mic(self):
        if self.micMutedBtn.text() == "Mute mic":   
            self.main.muteMic()
            self.micMutedBtn.setText("Unmute mic")
        else:
            self.main.unmuteMic()
            self.micMutedBtn.setText("Mute mic")

    def speaker(self):
        if self.speakerMutedBtn.text() == "Mute speaker":    
            self.main.muteSpeaker()
            self.speakerMutedBtn.setText("Unmute speaker")
        else:
            self.main.unmuteSpeaker()
            self.speakerMutedBtn.setText("Mute speaker")

    def changeVolume(self, username, value):
        self.main.changeVolume(username, value)

    def leave(self):
        self.main.leaveCall(self.main.user.username, self.groupName)

    def addMemberIntoCall(self, data):
        self.listMember.addMemberIntoCall(data)

    def removeMemberFromCall(self, username):
        self.listMember.removeMemberFromCall(username)

    def closeEvent(self, event):
        self.leave()
         