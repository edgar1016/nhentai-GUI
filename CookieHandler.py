import subprocess
import json

from PyQt6.QtWidgets import (
    QVBoxLayout, QLabel, QPushButton, 
    QLineEdit,QWidget,QMessageBox
)
from PyQt6.QtCore import QFile, Qt

from CustomTitleBar import CustomTitleBar

class CookieHandler(QWidget):

    def __init__(self, main_window, settings):
        super().__init__()
        self.main_window = main_window
        self.settings = settings
        
        self.cookie_command = "nhentai"
        self.user_agent_command = "nhentai"

        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.MSWindowsFixedSizeDialogHint | Qt.WindowType.FramelessWindowHint)

        self.initUI()

    def initUI(self):
        # Create a custom title bar
        custom_title_bar = CustomTitleBar(self, self.settings)
        style_file = QFile(":/resources/styles.qss")
        if style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            style_sheet = style_file.readAll()
            self.setStyleSheet(str(style_sheet, encoding="utf-8"))

        layout = QVBoxLayout()

        # Add the custom title bar to the layout
        layout.addWidget(custom_title_bar)

        self.cookie_extention_label = QLabel('Cookie Extension:', self)
        self.cookie_extention_le = QLineEdit(self)

        self.cookie_label = QLabel('Cookie:', self)
        self.cookie_le = QLineEdit(self)

        self.user_agent_label = QLabel('User-Agent:', self)
        self.user_agent_le = QLineEdit(self)

        self.btn = QPushButton('Submit', self)
        self.btn.clicked.connect(self.set_cookie)

        layout.addWidget(self.cookie_extention_label)
        layout.addWidget(self.cookie_extention_le)
        layout.addWidget(self.cookie_label)
        layout.addWidget(self.cookie_le)
        layout.addWidget(self.user_agent_label)
        layout.addWidget(self.user_agent_le)
        layout.addWidget(self.btn)

        self.setLayout(layout)

        self.setGeometry(300, 300, 300, 220)
        self.center()
        self.setWindowTitle('Cookies')

        self.show()
    
    def center(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()

        qr.moveCenter(cp)
        self.move(qr.topLeft())

    
    def set_cookie(self):
        if self.cookie_extention_le.text() != "":
            self.set_cookie_w_extension_data()
        elif (
                self.cookie_le.text() != "" 
                or self.user_agent_le.text() != ""
            ):
                self.set_cookie_manually()
        else:
                self.show_empty_fields_dialog()

    def show_empty_fields_dialog(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText("All fields are empty. Please enter some data.")
        msg.setWindowTitle("Empty Fields")
        msg.exec()

    def set_cookie_w_extension_data(self):
        input_data = self.cookie_extention_le.text()

        try:
            data = json.loads(input_data)
        except json.JSONDecodeError:
            print("Invalid JSON input.")
            return

        if "cookies" in data:
            cookies_data = data["cookies"]
            cookie_strings = [f'{cookie["name"]}={cookie["value"]}' for cookie in cookies_data]
            cookies_command = "; ".join(cookie_strings)
            self.cookie_command += (f' --cookie "{cookies_command}"')

        if "userAgent" in data:
            user_agent_data = data["userAgent"]
            self.user_agent_command += (f' --user-agent "{user_agent_data}"')

        if self.cookie_command != "nhentai":
            print(self.cookie_command)
            subprocess.Popen(self.cookie_command, shell=True)
        if self.user_agent_command != "nhentai":
            print(self.user_agent_command)
            subprocess.Popen(self.user_agent_command, shell=True)

        self.close()
    
    def set_cookie_manually(self):
        
        if self.cookie_le.text():
            self.cookie_command += (f" --cookie \"{self.cookie_le.text()}\"")
        if self.user_agent_le.text():
            self.user_agent_command += (f" --user-agent \"{self.user_agent_le.text()}\"")

        if self.cookie_command != "nhentai":
            print(self.cookie_command)
            subprocess.Popen(self.cookie_command, shell=True)
        if self.user_agent_command != "nhentai":
            print(self.user_agent_command)
            subprocess.Popen(self.user_agent_command, shell=True)

        self.close()