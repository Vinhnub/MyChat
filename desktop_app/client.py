from PySide6.QtWidgets import QApplication
import sys
from main import Main

app = QApplication(sys.argv)

main = Main(app)
main.show()

app.exec()

