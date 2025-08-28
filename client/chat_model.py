from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QListView, QLineEdit, QPushButton, QStyledItemDelegate, QHBoxLayout
from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex, QRect, QSize, QPoint
from PySide6.QtGui import QPainter, QColor, QFont, QFontMetrics

from datetime import datetime


# ---- Model ----
class ChatModel(QAbstractListModel):
    def __init__(self, messagesA=None, messagesB=None):
        super().__init__()
        self.messagesA = messagesA or []
        self.messagesB = messagesB or []
        self.active = 0  # 0 = dataset A, 1 = dataset B

    def currentMessages(self):
        return self.messagesA if self.active == 0 else self.messagesB

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.currentMessages()[index.row()]

    def rowCount(self, parent=None):
        return len(self.currentMessages())

    def addMessage(self, msg, which=None):
        """Nếu which=None thì thêm vào dataset đang active"""
        target = self.currentMessages() if which is None else (self.messagesA if which == 0 else self.messagesB)

        # ---- kiểm tra ngày ----
        msgDate = msg["time"].split(" ")[0]   # chỉ lấy phần dd/mm/yyyy
        needDateItem = False
        if target:
            last = target[-1]
            if last["type"] == "message":
                last_date = last["time"].split(" ")[0]
                if last_date != msgDate:
                    needDateItem = True
        else:
            # dataset rỗng thì chắc chắn cần ngày
            needDateItem = True

        # Nếu target là dataset đang hiển thị thì báo insert
        if target is self.currentMessages():
            if needDateItem:
                self.beginInsertRows(QModelIndex(), len(target), len(target))
                target.append({"type": "date", "date": msgDate})
                self.endInsertRows()

            self.beginInsertRows(QModelIndex(), len(target), len(target))
            target.append(msg)
            self.endInsertRows()
        else:
            if needDateItem:
                target.append({"type": "date", "date": msgDate})
            target.append(msg)


    def switchDataset(self, which):
        if which != self.active:
            self.active = which
            # chỉ báo thay đổi layout, không reset toàn bộ
            self.layoutChanged.emit()



class ChatDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.maxCharsPerLine = 50  # số ký tự tối đa 1 dòng

    def wrapTextByChar(self, text):
        lines = []
        for i in range(0, len(text), self.maxCharsPerLine):
            lines.append(text[i:i+self.maxCharsPerLine])
        return "\n".join(lines)

    def paint(self, painter, option, index):
        data = index.data(Qt.DisplayRole)
        if not data:
            return

        painter.save()
        rect = option.rect
        margin = 10
        padding = 8
        spacing = 4  # khoảng cách giữa tên và bubble

        # date item
        if data["type"] == "date":
            painter.setFont(QFont("Arial", 9, QFont.Bold))
            painter.setPen(QColor("#555"))
            painter.drawText(rect, Qt.AlignCenter, data["date"])
            painter.restore()
            return

        text = self.wrapTextByChar(data["text"])
        sender = data["sender"]
        timeFull = data["time"]
        timeShort = timeFull.split(" ")[1]

        # font
        senderFont = QFont("Arial", 8)   # giống kích thước giờ
        textFont = QFont("Arial", 10)
        timeFont = QFont("Arial", 8)

        # đo kích thước bằng QFontMetrics
        fmText = QFontMetrics(textFont)
        textRect = fmText.boundingRect(QRect(0, 0, 1000, 0), Qt.TextWordWrap, text)

        fmSender = QFontMetrics(senderFont)
        senderRect = fmSender.boundingRect(sender)

        fmTime = QFontMetrics(timeFont)
        timeRect = fmTime.boundingRect(timeShort)

        # tính kích thước bubble (chưa đặt y)
        bubbleW = max(textRect.width(), timeRect.width()) + 2 * padding
        bubbleH = textRect.height() + timeRect.height() + 3 * padding
        bubbleRect = QRect(0, 0, bubbleW, bubbleH)

        # đặt vị trí bubble dưới tên (y = rect.top() + senderHeight + spacing)
        y_top = rect.top() + senderRect.height() + spacing
        if sender == "me":
            # căn phải
            bubbleRect.moveTopRight(QPoint(rect.right() - margin, y_top))
        else:
            # căn trái
            bubbleRect.moveTopLeft(QPoint(rect.left() + margin, y_top))

        # vẽ tên người gửi ở phía trên bubble, màu đen
        painter.setFont(senderFont)
        painter.setPen(Qt.black)
        if sender == "me":
            sender_x = bubbleRect.right() - padding - senderRect.width()
        else:
            sender_x = bubbleRect.left() + padding
        # sender_y dùng baseline tương đối (chúng ta đặt baseline ở rect.top() + senderRect.height())
        sender_point = QPoint(sender_x, rect.top() + senderRect.height())
        painter.drawText(sender_point, sender)

        # vẽ bubble
        color = QColor("#A8E6CF") if sender == "me" else QColor("#D3D3D3")
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(bubbleRect, 10, 10)

        # vẽ text bên trong bubble
        painter.setFont(textFont)
        painter.setPen(Qt.black)
        realTextRect = QRect(bubbleRect.left() + padding,
                             bubbleRect.top() + padding,
                             textRect.width(),
                             textRect.height())
        painter.drawText(realTextRect, Qt.TextWordWrap, text)

        # vẽ time (giữ ở bottom-left của bubble)
        painter.setFont(timeFont)
        painter.setPen(Qt.darkGray)
        timePos = QPoint(bubbleRect.left() + padding,
                         bubbleRect.bottom() - padding)
        painter.drawText(timePos, timeShort)

        painter.restore()

    def sizeHint(self, option, index):
        data = index.data(Qt.DisplayRole)
        if not data:
            return super().sizeHint(option, index)

        if data["type"] == "date":
            return QSize(100, 25)

        # dùng cùng fonts như paint để tính kích thước
        senderFont = QFont("Arial", 8)
        textFont = QFont("Arial", 10)
        timeFont = QFont("Arial", 8)

        fmText = QFontMetrics(textFont)
        textRect = fmText.boundingRect(QRect(0, 0, 1000, 0), Qt.TextWordWrap, self.wrapTextByChar(data["text"]))

        fmSender = QFontMetrics(senderFont)
        senderRect = fmSender.boundingRect(data["sender"])

        fmTime = QFontMetrics(timeFont)
        timeRect = fmTime.boundingRect(data["time"].split(" ")[1])

        width = max(textRect.width(), senderRect.width(), timeRect.width()) + 2 * 8 + 10
        height = senderRect.height() + textRect.height() + timeRect.height() + 50

        return QSize(width, height)


# ---- Window ----
class ChatWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat - 1 model, nhiều dataset")
        self.setFixedWidth(600)

        self.model = ChatModel([
            {"type": "date", "date": "26/08/2025"},
            {"type": "message", "sender": "me", "text": "Hôm qua nè", "time": "26/08/2025 22:50"},
            {"type": "date", "date": "27/08/2025"},
            {"type": "message", "sender": "other", "text": "Hôm nay mới nè", "time": "27/08/2025 09:10"},
        ])
        self.view = QListView()
        self.view.setModel(self.model)
        self.view.setItemDelegate(ChatDelegate())
        self.input = QLineEdit()
        self.sendBtn = QPushButton("Send")
        
        self.sendBtn.clicked.connect(self.sendMessage)
        self.input.returnPressed.connect(self.sendMessage)

        layout = QVBoxLayout()
        entryLayout = QHBoxLayout()
        entryLayout.addWidget(self.input)
        entryLayout.addWidget(self.sendBtn)
        layout.addWidget(self.view)
        layout.addLayout(entryLayout)
        self.setLayout(layout)

        self.check = 0

    def sendMessage(self):
        text = self.input.text().strip()
        if text:
            now = datetime.now().strftime("%d/%m/%Y %H:%M")
            self.model.addMessage({"type": "message", "sender": "me", "text": text, "time": now})
            self.input.clear()
            self.view.scrollToBottom()

    def switchDataset(self):
        self.check = 1 - self.check
        self.model.switchDataset(self.check)
        self.view.scrollToBottom()



if __name__ == "__main__":
    app = QApplication([])
    win = ChatWidget()
    win.show()
    app.exec()
