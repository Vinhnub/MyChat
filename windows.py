from PySide6.QtWidgets import (QWidget,  QLabel, QHBoxLayout,
                                QVBoxLayout, QPushButton, QLineEdit,
                                QFormLayout, QGridLayout, QStatusBar)
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

        label.setStyleSheet("""
    QLabel {
        border: 1px solid black;
        padding: 8px;
    }
""")

        exitBtn.setStyleSheet("""
    QPushButton {
        border: 1px solid black;
        padding: 5px;
    }
""")
        signInBtn.setStyleSheet("""
    QPushButton {
        border: 1px solid black;
        padding: 5px;
    }
""")
        signUpBtn.setStyleSheet("""
    QPushButton {
        border: 1px solid black;
        padding: 5px;
    }
""")

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
        self.main.show()

    def signUpBtnClicked(self):
        self.main.secondWindow = SignUpWindow(self.app, self.main)
        self.main.show()

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
        label.setStyleSheet("""
    QLabel {
        border: 1px solid black;
        padding: 8px;
    }
""")

        entryLayout = QFormLayout()
        usernameEntry = QLineEdit()
        passwordEntry = QLineEdit()
        usernameLabel = QLabel("Username:")
        passwordLabel = QLabel("Password:")
        usernameLabel.setFont(QFont('Arial', 10))
        passwordLabel.setFont(QFont('Arial', 10))
        entryLayout.addRow(usernameLabel, usernameEntry)
        entryLayout.addRow(passwordLabel, passwordEntry)
        
        btnLayout = QHBoxLayout()
        enterBtn = QPushButton("Enter")
        cancelBtn = QPushButton("Cancel")
        enterBtn.setFont(QFont('Arial', 10))
        cancelBtn.setFont(QFont('Arial', 10))
        enterBtn.setStyleSheet("""
    QPushButton {
        border: 1px solid gray;
        padding: 5px;
    }
""")
        cancelBtn.setStyleSheet("""
    QPushButton {
        border: 1px solid gray;
        padding: 5px;
    }
""")
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
        self.main.secondWindow = None

    def enterClicked(self):
        pass

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
        label.setStyleSheet("""
    QLabel {
        border: 1px solid black;
        padding: 8px;
    }
""")
        
        entryLayout = QFormLayout()
        fullnameEntry = QLineEdit()
        usernameEntry = QLineEdit()
        passwordEntry = QLineEdit()
        fullnameLabel = QLabel("Fullname:")
        usernameLabel = QLabel("Username:")
        passwordLabel = QLabel("Password:")
        fullnameLabel.setFont(QFont('Arial', 10))
        usernameLabel.setFont(QFont('Arial', 10))
        passwordLabel.setFont(QFont('Arial', 10))
        entryLayout.addRow(fullnameLabel, fullnameEntry)
        entryLayout.addRow(usernameLabel, usernameEntry)
        entryLayout.addRow(passwordLabel, passwordEntry)
        
        btnLayout = QHBoxLayout()
        enterBtn = QPushButton("Enter")
        cancelBtn = QPushButton("Cancel")
        enterBtn.setFont(QFont('Arial', 10))
        cancelBtn.setFont(QFont('Arial', 10))
        enterBtn.setStyleSheet("""
    QPushButton {
        border: 1px solid gray;
        padding: 5px;
    }
""")
        cancelBtn.setStyleSheet("""
    QPushButton {
        border: 1px solid gray;
        padding: 5px;
    }
""")
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
        self.main.secondWindow = None

    def enterClicked(self):
        pass

    def showError(self):
        pass