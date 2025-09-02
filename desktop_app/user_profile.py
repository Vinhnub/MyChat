from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt

class UserProfileWidget(QWidget):
    def __init__(self, fullName):
        super().__init__()
        self.setFixedWidth(250)
        self.setFixedHeight(50)
        self.setStyleSheet(""" 
            border: 1px solid gray;
        """)
        self.fullName = fullName
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        lblFullName = QLabel(fullName)
        lblFullName.setAlignment(Qt.AlignCenter)
        lblFullName.setStyleSheet("font-weight: bold; font-size: 12pt;")

        layout.addWidget(lblFullName)
