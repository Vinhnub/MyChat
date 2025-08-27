from PySide6.QtCore import QSize
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMainWindow, QPushButton, QSlider, QToolBar, QStatusBar

class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("Hello")
 
        menuBar = self.menuBar()

        fileMenu = menuBar.addMenu("&file")
        quitAcction = fileMenu.addAction("Quit")
        quitAcction.triggered.connect(self.quitApp)
        addAcction = fileMenu.addAction("add")

        editMenu = menuBar.addMenu("&edit")
        cutAcction = editMenu.addAction("cut")
        copyAcction = editMenu.addAction("copy")
        insertAcction = editMenu.addAction("insert")

        #toolBar
        toolBar = QToolBar("Main tool bar")
        toolBar.setIconSize(QSize(16,16))
        self.addToolBar(toolBar)
        # add action to the toolbar
        toolBar.addAction(quitAcction)

        action1 = QAction("alo alo", self)
        action1.setStatusTip("hello to alo alo")
        action1.triggered.connect(self.toolBarButtonClick)
        toolBar.addAction(action1)

        action2 = QAction(QIcon("image/action2.png"), "hello", self)
        action2.setStatusTip("hello to hello")
        action2.triggered.connect(self.toolBarButtonClick)
        action2.setCheckable(True)
        toolBar.addAction(action2)

        toolBar.addSeparator()
        toolBar.addWidget(QPushButton("Click me!"))

        # working with status bars
        self.setStatusBar(QStatusBar(self))

        button1 = QPushButton("Button 1")
        button1.clicked.connect(self.button1Clicked)
        self.setCentralWidget(button1)

    def quitApp(self):
        self.app.quit()

    def toolBarButtonClick(self):
        self.statusBar().showMessage("Message from my app", 3000)
 
    def button1Clicked(self):
        print("Button 1 clicked!")
