from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt

class CurrentGroupWidget(QWidget):
    def __init__(self, name):
        super().__init__()
        self.setFixedWidth(600)
        self.setFixedHeight(50)
        self.setStyleSheet(""" 
            border: 1px solid gray;
        """)
        self.name = name
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)


        self.name = QLabel(name)
        self.name.setStyleSheet("font-weight: bold; font-size: 12pt;")
        self.name.setAlignment(Qt.AlignCenter)
        

        layout.addWidget(self.name)
        #layout.addWidget(lblMsg)

    def switchGroup(self, groupName):
        self.name.setText(groupName)
