from windows import *

class Main():
    def __init__(self, app):
        self.app = app
        self.user = None
        self.mainWindow = StartWindow(self.app, self)
        self.secondWindow = None

    def show(self):
        self.mainWindow.show()
        if self.secondWindow is not None:
            self.secondWindow.show()