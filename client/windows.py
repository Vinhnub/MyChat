from PySide6.QtWidgets import (QWidget,  QLabel, QHBoxLayout,
                                QVBoxLayout, QPushButton, QLineEdit,
                                QFormLayout, QGridLayout, QStatusBar,
                                QMessageBox)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

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

        enterBtn.clicked.connect(self.showError)
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
        

    def showError(self):
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


class MainWindow(QWidget):
    pass