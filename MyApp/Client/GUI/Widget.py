from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QComboBox, QTabWidget, QAbstractItemView, QListWidget, QRadioButton, QButtonGroup, QCheckBox,QGroupBox,QGridLayout, QSizePolicy, QTextEdit, QLineEdit, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox, QLabel
class WidgetComboBox(QWidget):
    def __init__(self, app):
        super().__init__()
        self.setWindowTitle("QComboBox Demo")
        self.comboBox = QComboBox(self)

        #Add planets to the combobox
        self.comboBox.addItem("Earth")
        self.comboBox.addItem("Venus")
        self.comboBox.addItem("Mars")
        self.comboBox.addItem("Pluton")
        self.comboBox.addItem("Saturn")

        buttonCurrentValue = QPushButton("Current Value")
        buttonCurrentValue.clicked.connect(self.currentValue)

        buttonSetCurrent = QPushButton("Set Value")
        buttonSetCurrent.clicked.connect(self.setCurrent)

        buttonGetCurrent = QPushButton("Get Values")
        buttonGetCurrent.clicked.connect(self.getValues)

        QVBox = QVBoxLayout()
        QVBox.addWidget(self.comboBox)
        QVBox.addWidget(buttonCurrentValue)
        QVBox.addWidget(buttonSetCurrent)
        QVBox.addWidget(buttonGetCurrent)

        self.setLayout(QVBox)
        
    def currentValue(self):
        print(f"current item: {self.comboBox.currentText()}")
        print(f"current index: {self.comboBox.currentIndex()}")
    def setCurrent(self):
        self.comboBox.setCurrentIndex(2)
    def getValues(self):
        for i in range(self.comboBox.count()):
            print("index [",i,"] : ", self.comboBox.itemText(i))
            
class WidgetQTab(QWidget):
    def __init__(self, app):
        super().__init__()
        self.setWindowTitle("WidgetQTab")

        Qtab = QTabWidget()

        #Information
        widget_form = QWidget()
        label_full_name = QLabel("Full name :")
        line_edit_full_name = QLineEdit()
        form_layout = QHBoxLayout ()
        form_layout. addWidget(label_full_name)
        form_layout. addWidget(line_edit_full_name)
        widget_form. setLayout (form_layout)

        #Buttons
        widget_buttons = QWidget()
        button_1 = QPushButton("One")
        button_1.clicked.connect(self.button_1_clicked)
        button_2 = QPushButton("Two")
        button_3 = QPushButton("Three")
        buttons_layout = QVBoxLayout ()
        buttons_layout.addWidget(button_1)
        buttons_layout.addWidget(button_2)
        buttons_layout.addWidget(button_3)
        widget_buttons. setLayout(buttons_layout)

        Qtab.addTab(widget_form, "Information")
        Qtab.addTab(widget_buttons, "Buttons")
        
        layout = QHBoxLayout()
        layout.addWidget(Qtab)

        self.setLayout(layout)

    def button_1_clicked(self):
        print("Button 1 is clicked")

class WidgetSelection(QWidget):
    def __init__(self, app):
        super().__init__()
        self.setWindowTitle("WidgetSelection")

        self.list_widget = QListWidget(self)
        self.list_widget. setSelectionMode(QAbstractItemView.MultiSelection)
        self.list_widget. addItem("One")
        self.list_widget. addItems(["Two", "Three"])
        self.list_widget. currentItemChanged.connect(self.current_item_changed)
        self.list_widget. currentTextChanged.connect(self.current_text_changed)


        button_add_item = QPushButton("Add Item")
        button_add_item. clicked.connect(self.add_item)

        button_delete_item = QPushButton("Delete Item")
        button_delete_item.clicked.connect(self.delete_item)

        button_item_count = QPushButton("Item Count")
        button_item_count. clicked.connect(self.item_count)

        button_selected_items = QPushButton("Selected Items")
        button_selected_items. clicked.connect(self.selected_items)
        
        vlayout = QVBoxLayout ()
        vlayout.addWidget(self.list_widget)
        vlayout.addWidget(button_add_item)
        vlayout.addWidget(button_delete_item)
        vlayout.addWidget(button_item_count)
        vlayout.addWidget(button_selected_items)
        self.setLayout(vlayout)

    def current_item_changed(self, item):
        print("Current item : ", item.text())
    def current_text_changed(self, text):
        print("Current text changed : ",text)

    def add_item(self):
        self.list_widget.addItem("New Item")
    def item_count(self):
        print("Item count : ",self.list_widget.count())
    def delete_item(self):
        self.list_widget.takeItem(self.list_widget.currentRow())
    def selected_items(self):
        list = self.list_widget.selectedItems()
        for i in list :
            print(i.text())

class WidgetBox(QWidget):
    def __init__(self, app):
        super().__init__()
        self.setWindowTitle("WidgetBox")

        #Checkboxes : operating system
        os = QGroupBox("Choose operating system")
        windows = QCheckBox("Windows")
        windows.toggled.connect(self.windows_box_toggled)

        linux = QCheckBox("Linux")
        linux. toggled.connect(self.linux_box_toggled)

        mac = QCheckBox("Mac")
        mac.toggled.connect(self.mac_box_toggled)

        osLayout = QVBoxLayout()
        osLayout.addWidget(windows)
        osLayout.addWidget(linux)
        osLayout.addWidget(mac)

        # check exclusive
        drinks = QGroupBox("Choose your drink")

        beer = QCheckBox("Beer")
        juice = QCheckBox("Juice")
        coffe = QCheckBox("Coffe")
        beer.setChecked(True)

        exclusive_button_group = QButtonGroup(self)
        exclusive_button_group.addButton(beer)
        exclusive_button_group.addButton(juice)
        exclusive_button_group. addButton(coffe)
        exclusive_button_group.setExclusive(True)
        drink_layout = QVBoxLayout()
        drink_layout.addWidget(beer)
        drink_layout.addWidget(juice)
        drink_layout. addWidget(coffe)
        #=>         
        drinks.setLayout(drink_layout)

        #Radio Button: Answers
        answers = QGroupBox ( "Choose Answer")
        answera = QRadioButton("A")
        answerb = QRadioButton("B")
        answerc = QRadioButton("C")
        answera. setChecked(True)

        answerslayout = QVBoxLayout()
        answerslayout.addWidget(answera)
        answerslayout.addWidget(answerb)
        answerslayout.addWidget(answerc)
        #=>
        answers.setLayout(answerslayout)

        #==>>
        os.setLayout(osLayout)
        layout = QVBoxLayout()
        layout.addWidget(os)
        layout.addWidget(drinks)
        layout.addWidget(answers)

        self.setLayout(layout)

    def windows_box_toggled(self, checked):
        if(checked):
            print("Windows box checked")
        else:
            print("Windows box unchecked")
    def linux_box_toggled(self, checked):
        if(checked):
           print("Linux box checked")
        else:
           print("Linux box unchecked")
    def mac_box_toggled(self, checked):
        if(checked):
           print("Mac box checked")
        else:
           print("Mac box unchecked")

class WidgetQGrid(QWidget):
    def __init__(self, app):
        super().__init__()
        self.setWindowTitle("WidgetQGridlayout")
        
        button1 = QPushButton("One")
        button2 = QPushButton("Two")
        button3 = QPushButton("Three")
        button4 = QPushButton("Four")
        button5 = QPushButton("Five")
        button6 = QPushButton("Six")
        button7 = QPushButton("Seven")

        gridLayout = QGridLayout()
        gridLayout.addWidget(button1,0,0)
        gridLayout.addWidget(button2,0,1,1,2) #Take up 1 row and 2 columns
        gridLayout.addWidget(button3,1,0,2,1) #Take up 2 rows and 1 column
        gridLayout.addWidget(button4,1,1)
        gridLayout.addWidget(button5,1,2)
        gridLayout.addWidget(button6,2,1)
        gridLayout.addWidget(button7,2,2)

        self.setLayout(gridLayout)

class WidgetStrengPolicy(QWidget):
    def __init__(self, app):
        super().__init__()
        self.setWindowTitle("WidgetStrengPolicy")

        inputText = QLabel("Input text here")
        inputTextEdit = QLineEdit()
        inputTextEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layOutH = QHBoxLayout()
        layOutH.addWidget(inputText)
        layOutH.addWidget(inputTextEdit)
        
        Button1 = QPushButton("Button1")
        Button2 = QPushButton("Button2")
        Button3 = QPushButton("Button3")
        
        layOutH2 = QHBoxLayout()
        layOutH2.addWidget(Button1,2)
        layOutH2.addWidget(Button2,1)
        layOutH2.addWidget(Button3,1)

        layOutV = QVBoxLayout()
        layOutV.addLayout(layOutH)
        layOutV.addLayout(layOutH2)

        self.setLayout(layOutV)
        
class WidgetImage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.setWindowTitle("WidgetImage")

        image = QLabel()
        image.setPixmap(QPixmap("image/action2"))

        layOutH = QHBoxLayout()
        layOutH.addWidget(image)

        self.setLayout(layOutH)

class WidgetEditText(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("WidgetEditText")
        self.textEdit = QTextEdit()
        
        #button
        currentTextButton = QPushButton("CurrentText")
        currentTextButton.clicked.connect(self.surrentTextButtonClicked)

        copyButton = QPushButton("Copy")
        copyButton.clicked.connect(self.textEdit.copy)
        cutButton = QPushButton("Cut")
        cutButton.clicked.connect(self.textEdit.cut)
        pasteButton = QPushButton("Paste")
        pasteButton.clicked.connect(self.textEdit.paste)
        undoButton = QPushButton("Undo")
        undoButton.clicked.connect(self.textEdit.undo)      
        redoButton = QPushButton("Redo")
        redoButton.clicked.connect(self.textEdit.redo)     
        quitButton = QPushButton("Quit")
        quitButton.clicked.connect(self.quitApp)

        setPlainTextButton = QPushButton("Set plain Text")
        #setPlainTextButton.clicked.connect(self.setPlainText)

        setHtmlButton = QPushButton("Set html")
        #setHtmlButton.clicked.connect(self.setHtml)

        clearButton = QPushButton("Clear")
        #clearButton.clicked.connect(self.clearText)
        
        layOutH = QHBoxLayout()
        layOutH.addWidget(currentTextButton)
        layOutH.addWidget(copyButton)
        layOutH.addWidget(cutButton)
        layOutH.addWidget(pasteButton)
        layOutH.addWidget(undoButton)
        layOutH.addWidget(redoButton)
        layOutH.addWidget(quitButton)

        layOutV = QVBoxLayout()
        layOutV.addLayout(layOutH)
        layOutV.addWidget(self.textEdit)

        self.setLayout(layOutV)
    def quitApp(self):
        self.app.quit()
    def surrentTextButtonClicked(self):
        print("Current text: ", self.textEdit.toPlainText())

class WidgetInput(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Widget")

        usernameLabel = QLabel("Username: ")
        self.lineEdit = QLineEdit()
        #self.lineEdit.textChanged.connect(self.changeText)
        #self.lineEdit.cursorPositionChanged.connect(self.cursorPositionChanged)
        #self.lineEdit.editingFinished.connect(self.EditFinished)
        #self.lineEdit.returnPressed.connect(self.returnPress
        #self.lineEdit.selectionChanged.connect(self.selectionChanged)
        self.lineEdit.textEdited.connect(self.textEdited)

        button = QPushButton("Grab data")
        button.clicked.connect(self.buttonClicked)
        self.text_holder_label = QLabel("I AM HERE")

        layOutH = QHBoxLayout()
        layOutH.addWidget(usernameLabel)
        layOutH.addWidget(self.lineEdit)

        layOutV = QVBoxLayout()
        layOutV.addLayout(layOutH)
        layOutV.addWidget(button)
        layOutV.addWidget(self.text_holder_label)

        self.setLayout(layOutV)

    def buttonClicked(self):
        self.text_holder_label.setText(self.lineEdit.text())
    def changeText(self):
        self.text_holder_label.setText(self.lineEdit.text())
    def cursorPositionChanged1(self, old, new):
        print(f"old position: {old} - new position: {new}")  
    def EditFinished(self):
        print("edit finished!")
    def returnPress(self):
        print("return press")
    def selectionChanged(self):
        print("Selection changed: ", self.lineEdit.selectedText())
    def textEdited(self, newtext):
        print("Text edited. New text: ", newtext)

class WidgetAlram(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QMessageBox")

        buttonHard = QPushButton("Hard")
        buttonHard.clicked.connect(self.buttonClickedHard)

        buttonCritial = QPushButton("Critical")
        buttonCritial.clicked.connect(self.buttonClickedCritical)

        buttonQuestion = QPushButton("Question")
        buttonQuestion.clicked.connect(self.buttonClickedQuestion)

        buttoninf = QPushButton("information")
        buttoninf.clicked.connect(self.buttonClickedInf)

        buttonWarning = QPushButton("Warning")
        buttonWarning.clicked.connect(self.buttonClickedWarning)

        buttonAbout = QPushButton("About")
        buttonAbout.clicked.connect(self.buttonClickedAbout)

        #set up layout
        layout = QVBoxLayout()
        layout.addWidget(buttonHard)
        layout.addWidget(buttonCritial)
        layout.addWidget(buttonQuestion)
        layout.addWidget(buttoninf)
        layout.addWidget(buttonWarning)
        layout.addWidget(buttonAbout)
        self.setLayout(layout)

    def buttonClickedHard(self):
        message = QMessageBox()
        message.setMinimumSize(700,200)
        message. setWindowTitle("Message Title")
        message. setText("Something happened")
        message.setInformativeText("Do you want to do something about it ?")
        message.setIcon(QMessageBox.Critical)
        message. setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        message. setDefaultButton(QMessageBox.Ok)
        ret = message. exec()

        if ret == QMessageBox.Ok :
           print("User chose OK")
        else:
           print ( "user chose Cancel")

    def buttonClickedCritical(self):
        ret = QMessageBox.critical(self,"warning warning",
                                      "Do you want to do something about it ?",
                                      QMessageBox.Ok | QMessageBox.Cancel)
        if ret == QMessageBox.Ok :
           print("User chose OK")
        else:
           print ( "user chose Cancel")

    def buttonClickedQuestion(self):
        print("Question")
    def buttonClickedInf(self):
        print("information")
    def buttonClickedWarning(self):
        print("Warning")
    def buttonClickedAbout(self):
        print("About")