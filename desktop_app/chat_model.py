from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QListView,
                               QLineEdit, QPushButton, QStyledItemDelegate, QHBoxLayout)
from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex, QRect, QSize, QPoint
from PySide6.QtGui import QPainter, QColor, QFont, QFontMetrics
from datetime import datetime


# ---- Model ----
class ChatModel(QAbstractListModel):
    def __init__(self, data, myName):
        super().__init__()
        self.myName = myName
        self.dictMessages = {}
        for group, lst in data.items():
            self.dictMessages[group] = self._convertListToInternal(lst)

        self.currentGroup = next(iter(self.dictMessages)) if self.dictMessages else None

    def _convertRawMsg(self, raw):
        if raw.get("type") in ("message", "date"):
            return raw

        dateStr = raw.get("date", "")
        try:
            dt = datetime.strptime(dateStr, "%Y/%m/%d %H:%M")
            timeFormated = dt.strftime("%d/%m/%Y %H:%M")
        except Exception:
            timeFormated = dateStr.replace("-", "/")

        senderName = raw.get("userName") or raw.get("sender") or "unknown"
        return {
            "type": "message",
            "sender": senderName,
            "text": raw.get("mesContent", raw.get("text", "")),
            "time": timeFormated
        }

    def _convertListToInternal(self, rawList):
        out = []
        lastDate = None
        for raw in rawList:
            item = self._convertRawMsg(raw)
            if item["type"] == "message":
                dateOnly = item["time"].split(" ")[0]
                if lastDate != dateOnly:
                    out.append({"type": "date", "date": dateOnly})
                    lastDate = dateOnly
                out.append(item)
            else:
                out.append(item)
                if item.get("date"):
                    lastDate = item["date"]
        return out

    def currentMessages(self):
        return self.dictMessages[self.currentGroup] if self.currentGroup else None

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.currentMessages()[index.row()]

    def rowCount(self, parent=None):
        return len(self.currentMessages())

    def addMessage(self, rawMsg, which):
        """rawMsg expected in new format {'mesID','mesContent','date','userName'}"""
        msg = self._convertRawMsg(rawMsg)
        target = self.dictMessages.setdefault(which, [])

        msgDate = msg["time"].split(" ")[0]
        needDateItem = False
        if target:
            last = None
            for i in range(len(target) - 1, -1, -1):
                if target[i].get("type") == "message":
                    last = target[i]
                    break
            if last is not None:
                lastData = last["time"].split(" ")[0]
                if lastData != msgDate:
                    needDateItem = True
            else:
                needDateItem = True
        else:
            needDateItem = True

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
        if which != self.currentGroup:
            if which not in self.dictMessages:
                self.dictMessages[which] = []
            self.currentGroup = which
            self.layoutChanged.emit()


class ChatDelegate(QStyledItemDelegate):
    def __init__(self, myName, parent=None):
        super().__init__(parent)
        self.maxCharsPerLine = 50
        self.myName = myName

    def wrapTextByChar(self, text):
        lines = []
        for i in range(0, len(text), self.maxCharsPerLine):
            lines.append(text[i:i + self.maxCharsPerLine])
        return "\n".join(lines)

    def paint(self, painter, option, index):
        data = index.data(Qt.DisplayRole)
        if not data:
            return

        painter.save()
        rect = option.rect
        margin = 10
        padding = 8
        spacing = 4

        # date item
        if data["type"] == "date":
            painter.setFont(QFont("Arial", 9, QFont.Bold))
            painter.setPen(QColor("#555"))
            painter.drawText(rect, Qt.AlignCenter, data["date"])
            painter.restore()
            return

        text = self.wrapTextByChar(data["text"])
        sender = data["sender"]     
        is_me = (sender == self.myName)
        timeFull = data["time"]
        timeShort = timeFull.split(" ")[1] if " " in timeFull else timeFull

        # font
        senderFont = QFont("Arial", 8)
        textFont = QFont("Arial", 10)
        timeFont = QFont("Arial", 8)

        fmText = QFontMetrics(textFont)
        textRect = fmText.boundingRect(QRect(0, 0, 1000, 0), Qt.TextWordWrap, text)

        fmSender = QFontMetrics(senderFont)
        senderLabel = self.myName if is_me else sender   
        senderRect = fmSender.boundingRect(senderLabel)

        fmTime = QFontMetrics(timeFont)
        timeRect = fmTime.boundingRect(timeShort)

        bubbleW = max(textRect.width(), timeRect.width()) + 2 * padding
        bubbleH = textRect.height() + timeRect.height() + 3 * padding
        bubbleRect = QRect(0, 0, bubbleW, bubbleH)

        yTop = rect.top() + senderRect.height() + spacing
        if is_me:
            bubbleRect.moveTopRight(QPoint(rect.right() - margin, yTop))
        else:
            bubbleRect.moveTopLeft(QPoint(rect.left() + margin, yTop))

        painter.setFont(senderFont)
        painter.setPen(Qt.black)
        if is_me:
            senderX = bubbleRect.right() - padding - senderRect.width()
        else:
            senderX = bubbleRect.left() + padding
        senderPoint = QPoint(senderX, rect.top() + senderRect.height())
        painter.drawText(senderPoint, senderLabel)

        color = QColor("#A8E6CF") if is_me else QColor("#D3D3D3")
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(bubbleRect, 10, 10)

        painter.setFont(textFont)
        painter.setPen(Qt.black)
        realTextRect = QRect(bubbleRect.left() + padding,
                             bubbleRect.top() + padding,
                             textRect.width(),
                             textRect.height())
        painter.drawText(realTextRect, Qt.TextWordWrap, text)

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

        sender = data["sender"]
        is_me = (sender == self.myName)
        senderLabel = self.myName if is_me else sender

        senderFont = QFont("Arial", 8)
        textFont = QFont("Arial", 10)
        timeFont = QFont("Arial", 8)

        fmText = QFontMetrics(textFont)
        textRect = fmText.boundingRect(QRect(0, 0, 1000, 0), Qt.TextWordWrap, self.wrapTextByChar(data["text"]))

        fmSender = QFontMetrics(senderFont)
        senderRect = fmSender.boundingRect(senderLabel)

        fmTime = QFontMetrics(timeFont)
        timeRect = fmTime.boundingRect(data["time"].split(" ")[1] if " " in data["time"] else data["time"])

        width = max(textRect.width(), senderRect.width(), timeRect.width()) + 2 * 8 + 10
        height = senderRect.height() + textRect.height() + timeRect.height() + 50

        return QSize(width, height)


class ChatWidget(QWidget):
    def __init__(self, window, data, myName):
        super().__init__()
        self.setWindowTitle("Chat - 1 model, nhiều dataset")
        self.setFixedWidth(600)
        self._window = window
        self.myName = myName

        self.model = ChatModel(data, myName)

        self.view = QListView()
        self.view.setModel(self.model)
        self.view.setItemDelegate(ChatDelegate(self.myName))
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


    def sendMessage(self):
        text = self.input.text().strip()
        if text != "" and self.model.currentGroup is not None:
            nowDate = datetime.now()
            date_iso = nowDate.strftime("%Y/%m/%d %H:%M")
            msg = {
                "mesContent": text,
                "date": date_iso,
                "userName": self.myName,
                "groupName" : self.model.currentGroup
            }
            self.input.clear()
            self._window.sendMessage(msg)
            self.view.scrollToBottom()

    def recvMessage(self, msg):
        rawMsg = {"mesID" : 0, "mesContent" : msg["mesContent"], "date" : msg["date"], "userName" : msg["userName"]}
        groupName = msg["groupName"]
        self.model.addMessage(rawMsg, groupName)
        self.view.scrollToBottom()

    def switchDataset(self, which):
        self.model.switchDataset(which)
        self.view.scrollToBottom()


