import sys
import subprocess
import re
import os
import json

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel,
    QPushButton, QLineEdit, QCheckBox, QWidget,
    QFileDialog, QMenu, QMessageBox, QFrame, QHBoxLayout, 
    QSpacerItem, QSizePolicy, QMenuBar
)
from PyQt6.QtGui import QAction, QMouseEvent, QPixmap
from PyQt6.QtCore import QSettings, QFile, Qt, QSize

class CustomTitleBar(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.parent = main_window
        self.main_window = main_window

        self.layout = QVBoxLayout()  # Use QHBoxLayout for horizontal layout

        self.title_layout = QHBoxLayout()

        # Title label with style
        self.title_label = QLabel('<span style="color: #ed2553;">n</span>Hentai GUI')
        self.title_label.setObjectName("TitleLabel")  # Apply a style object name

        # Icon for the title label
        self.title_icon = QLabel()
        self.title_icon.setFixedSize(30, 30)
        
        # Icon for the title label
        self.title_icon = QLabel()
        icon_path = os.path.join(os.path.dirname(__file__), "resources", "nHentai.svg")  # Path to the icon
        icon = QPixmap(icon_path)
        self.title_icon.setPixmap(icon.scaled(QSize(40, 20)))  # Set the size of the icon

        # Adjust the margins and spacing for the title_label and icon
        self.title_layout.setContentsMargins(0, 0, 0, 0)  # Reset margins to zero
        self.title_layout.setSpacing(-5)  # Adjust spacing between elements

        # Add the title_icon and title_label with a stretch between them to push them to the left
        self.title_layout.addWidget(self.title_icon)  # Add the title_icon
        self.title_layout.addStretch(0)  # Add a stretch between the icon and title_label
        self.title_layout.addWidget(self.title_label)  # Add the title_label

        # Add the title_label with a stretch after it to push it to the left
        self.title_layout.addWidget(self.title_label)  # Add the title_label
        self.title_layout.addStretch(1)  # Add a stretch after the title_label

        # Spacer to push buttons to the right
        self.title_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed))

        # Minimize button with style
        self.minimize_button = QPushButton("─")
        self.minimize_button.setObjectName("MinimizeButton")  # Apply a style object name
        self.minimize_button.setFixedHeight(30)
        self.minimize_button.setFixedWidth(30)
        self.minimize_button.clicked.connect(self.minimize_window)
        self.title_layout.addWidget(self.minimize_button)

        # Maximize/Restore button with style
        self.maximize_restore_button = QPushButton("□")
        self.maximize_restore_button.setObjectName("MaximizeRestoreButton")  # Apply a style object name
        self.maximize_restore_button.setFixedHeight(30)
        self.maximize_restore_button.setFixedWidth(30)
        self.maximize_restore_button.clicked.connect(self.toggle_maximize_restore)
        self.title_layout.addWidget(self.maximize_restore_button)

        # Close button with style
        self.close_button = QPushButton("✕")
        self.close_button.setObjectName("CloseButton")  # Apply a style object name
        self.close_button.setFixedHeight(30)
        self.close_button.setFixedWidth(30)
        self.close_button.clicked.connect(self.close_window)
        self.title_layout.addWidget(self.close_button)

        self.layout.addLayout(self.title_layout)

        if isinstance(self.parent, QMainWindow):
            # Create the menu bar
            menubar = QMenuBar(self)
            file_menu = menubar.addMenu("File")
            options_menu = QMenu("Options", self)
            file_menu.addMenu(options_menu)

            # Add action for setting cookie
            set_cookie_action = QAction("Set Cookie", self)
            set_cookie_action.triggered.connect(self.set_cookie)
            options_menu.addAction(set_cookie_action)

            # Add an action for setting default directory
            set_default_dir_action = QAction("Set Default Directory", self)
            set_default_dir_action.triggered.connect(self.set_default_directory)
            options_menu.addAction(set_default_dir_action)

            # Add action for opening default directory
            open_default_directory_action = QAction("Open Default Directory", self)
            open_default_directory_action.triggered.connect(self.open_default_directory)
            file_menu.addAction(open_default_directory_action)

            # Adds presets to the menu bar
            preset_menu = menubar.addMenu("Presets")

            # Favorites Preset
            favoritesPresetMenu = QAction("Favorites Preset", self)
            favoritesPresetMenu.triggered.connect(self.favoritesPreset)
            preset_menu.addAction(favoritesPresetMenu)

            # Same Series Preset
            sameSeriesPresetMenu = QAction("Same Series Preset",self)
            sameSeriesPresetMenu.triggered.connect(self.sameSeriesPreset)
            preset_menu.addAction(sameSeriesPresetMenu)

            # Multiple Preset
            multiplePresetMenu = QAction("Multiple Preset",self)
            multiplePresetMenu.triggered.connect(self.multiplePreset)
            preset_menu.addAction(multiplePresetMenu)

            self.menuLayout = QHBoxLayout()
            self.menuLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.menuLayout.addWidget(menubar)

            self.layout.addLayout(self.menuLayout)
    
        self.setLayout(self.layout)

    def toggle_maximize_restore(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
        else:
            self.parent().showMaximized()

    def set_cookie(self):
        self.main_window.set_cookie()

    def set_default_directory(self):
        self.main_window.set_default_directory()

    def open_default_directory(self):
        self.main_window.open_default_directory()

    def favoritesPreset(self):
        self.main_window.favoritesPreset()

    def sameSeriesPreset(self):
        self.main_window.sameSeriesPreset()

    def multiplePreset(self):
        self.main_window.multiplePreset()
    
    # Implement mouse event handlers to enable window dragging
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.drag_start_position
            new_pos = self.parent.pos() + delta
            self.parent.move(new_pos)
            self.drag_start_position = event.globalPosition().toPoint()  # Update the drag start position
            event.accept()

    def minimize_window(self):
        self.parent.showMinimized()
    
    def close_window(self):
        self.parent.close()

class CookieHandler(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.cookie_command = "nhentai"
        self.user_agent_command = "nhentai"

        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.MSWindowsFixedSizeDialogHint | Qt.WindowType.FramelessWindowHint)

    def initUI(self):
        # Create a custom title bar
        custom_title_bar = CustomTitleBar(self)

        style_file = QFile("styles.qss")
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
        msg.setIcon(QMessageBox.Icon.Warning)  # Use the correct enum value for the warning icon
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMenuBar(None)
        
        # Get the directory of the script
        script_directory = os.path.dirname(os.path.abspath(__file__))

        # Determine the path for the settings file (INI) in the script's directory
        settings_file = os.path.join(script_directory, "settings.ini")
        self.settings = QSettings(settings_file, QSettings.Format.IniFormat)  # Create a QSettings instance

        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.MSWindowsFixedSizeDialogHint | Qt.WindowType.FramelessWindowHint)

        self.cookieHandler = None

        self.init_ui()


    def init_ui(self):
        # Create the custom title bar and add it to the layout
        custom_title_bar = CustomTitleBar(self)

        self.setWindowTitle("nHentai GUI")
        self.setGeometry(80, 100, 500, 300)
        self.center()

        layout = QVBoxLayout()

        layout.addWidget(custom_title_bar)

        # Create a container widget (QFrame) for the central widget
        central_container = QFrame()
        central_container.setObjectName("centralContainer")

        self.central_widget = QWidget()
        self.central_widget.setLayout(layout)
        central_container.setLayout(layout)  # Set the layout for the container

        self.setCentralWidget(central_container)  # Set the container as the central widget

        self.run_button = QPushButton("Run Commands")
        self.run_button.clicked.connect(self.run_commands)

        # Elements for nhentai commands
        self.ids_input_label = QLabel("IDs (e.g., 302294 317039):")
        self.ids_input = QLineEdit(self.settings.value("ids_input", "302294 317039"))

        self.rm_origin_dir_checkbox = QCheckBox("Remove Original Directory")
        self.rm_origin_dir_checkbox.setFixedWidth(170)
        self.save_history_checkbox = QCheckBox("Save Download History")
        self.save_history_checkbox.setFixedWidth(170)
        self.favorites_checkbox = QCheckBox("Download Favorites")
        self.favorites_checkbox.setFixedWidth(170)
        self.page_input_label = QLabel("Page Range (e.g., 1-6):")
        self.page_input_label.setFixedWidth(120)
        self.page_input = QLineEdit(self.settings.value("page_input", "1-6"))
        self.page_input.setFixedWidth(50)
        self.download_checkbox = QCheckBox("Download")
        self.download_checkbox.setFixedWidth(120)
        self.delay_input_label = QLabel("Delay (seconds):")
        self.delay_input = QLineEdit(self.settings.value("delay_input", "1"))
        self.delay_input.setFixedWidth(50)
        self.cbz_checkbox = QCheckBox("CBZ")
        self.cbz_checkbox.setFixedWidth(90)
        self.move_to_folder_checkbox = QCheckBox("Move to Folder")
        self.move_to_folder_checkbox.setFixedWidth(120)

        self.format_input = QLineEdit(self.settings.value("format_input", '[%ag] - %p (%i)'))
        self.output_input = QLineEdit(self.settings.value("output_input", ""))

        # Load checkbox states
        self.rm_origin_dir_checkbox.setChecked(self.settings.value("rm_origin_dir_checkbox", False, type=bool))
        self.save_history_checkbox.setChecked(self.settings.value("save_history_checkbox", False, type=bool))
        self.favorites_checkbox.setChecked(self.settings.value("favorites_checkbox", False, type=bool))
        self.download_checkbox.setChecked(self.settings.value("download_checkbox", False, type=bool))
        self.cbz_checkbox.setChecked(self.settings.value("cbz_checkbox", False, type=bool))
        self.move_to_folder_checkbox.setChecked(self.settings.value("move_to_folder_checkbox", False, type=bool))

        # Add widgets to layout
        layout.addWidget(self.ids_input_label)
        layout.addWidget(self.ids_input)

        # Create QHBoxLayout for the first row of input elements and checkboxes
        first_row_layout = QHBoxLayout()
        first_row_layout.addWidget(self.rm_origin_dir_checkbox)
        first_row_layout.addWidget(self.page_input_label)
        first_row_layout.addWidget(self.delay_input_label)
        layout.addLayout(first_row_layout)

        # Create QHBoxLayout for the second row of input elements and checkboxes
        second_row_layout = QHBoxLayout()
        second_row_layout.addWidget(self.save_history_checkbox)
        second_row_layout.addWidget(self.page_input)
        second_row_layout.addSpacing(70)
        second_row_layout.addWidget(self.delay_input)
        
        second_row_layout.addStretch(1)
        layout.addLayout(second_row_layout)

        # Create QHBoxLayout for the third row of input elements and checkboxes
        third_row_layout = QHBoxLayout()
        third_row_layout.addWidget(self.favorites_checkbox)
        third_row_layout.addWidget(self.download_checkbox)
        third_row_layout.addWidget(self.cbz_checkbox)
        third_row_layout.addWidget(self.move_to_folder_checkbox)
        third_row_layout.addStretch(1)
        layout.addLayout(third_row_layout)

        layout.addWidget(QLabel("Format:"))
        layout.addWidget(self.format_input)
        layout.addWidget(QLabel("Output Folder:"))
        layout.addWidget(self.output_input)
        layout.addWidget(self.run_button)

        # Options #

        style_file = QFile("styles.qss")
        if style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            style_sheet = style_file.readAll()
            self.setStyleSheet(str(style_sheet, encoding="utf-8"))

    def center(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()

        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        # Save the current state of elements to the QSettings
        self.settings.setValue("ids_input", self.ids_input.text())
        self.settings.setValue("page_input", self.page_input.text())
        self.settings.setValue("delay_input", self.delay_input.text())
        self.settings.setValue("format_input", self.format_input.text())
        self.settings.setValue("output_input", self.output_input.text())

        if not (self.settings.contains("default_doujins_folder")):
            self.settings.setValue("default_doujins_folder", "C:/Doujins/")

        # Save checkbox states
        self.settings.setValue("rm_origin_dir_checkbox", self.rm_origin_dir_checkbox.isChecked())
        self.settings.setValue("save_history_checkbox", self.save_history_checkbox.isChecked())
        self.settings.setValue("favorites_checkbox", self.favorites_checkbox.isChecked())
        self.settings.setValue("download_checkbox", self.download_checkbox.isChecked())
        self.settings.setValue("cbz_checkbox", self.cbz_checkbox.isChecked())
        self.settings.setValue("move_to_folder_checkbox", self.move_to_folder_checkbox.isChecked())

        event.accept()

    def run_commands(self):
        # Assemble the nhentai command based on user inputs
        commands = "nhentai"
        if self.ids_input.text():
            cleaned_output_text = self.ids_input.text().replace("#","")
            commands += f" --id {cleaned_output_text}"
        if self.rm_origin_dir_checkbox.isChecked():
            commands += (" --rm-origin-dir")
        if self.save_history_checkbox.isChecked():
            commands += " --save-download-history"
        if self.favorites_checkbox.isChecked():
            commands += " --favorites"
        if self.page_input.text():
            if self.page_input.text() == "0":
                commands += f" --page-all"
            else:
                commands += f" --page={self.page_input.text()}"
        if self.download_checkbox.isChecked():
            commands += " --download"
        if self.delay_input.text():
            commands += f" --delay {self.delay_input.text()}"
        if self.cbz_checkbox.isChecked():
            commands += " --cbz"
        if self.move_to_folder_checkbox.isChecked():
            commands += " --move-to-folder"
        if self.format_input.text():
            commands += f' --format "{self.format_input.text()}"'
        if self.output_input.text():
            cleaned_output_text = re.sub(r'[\\/*?:"<>|]',"-",self.output_input.text())
            commands += f' --output "{self.settings.value("default_doujins_folder", "C:/Doujins")}/"{cleaned_output_text}/"'
        else:
            commands += f' --output "{self.settings.value("default_doujins_folder", "C:/Doujins")}"'

        print(commands)

        # Open the terminal externally and run the commands
        subprocess.Popen(commands, shell=True)

    def favoritesPreset(self):
        # Apply favoritesPreset settings
        self.ids_input.setText("")
        self.rm_origin_dir_checkbox.setChecked(False)
        self.save_history_checkbox.setChecked(True)
        self.favorites_checkbox.setChecked(True)
        self.page_input.setText("1-6")
        self.download_checkbox.setChecked(True)
        self.delay_input.setText("1")
        self.cbz_checkbox.setChecked(True)
        self.move_to_folder_checkbox.setChecked(True)
        self.format_input.setText('[%ag] - %p (%i)')
        self.output_input.setText('')

    def sameSeriesPreset(self):
        # Apply Same Series Preset settings
        # self.ids_input.setText("")
        self.rm_origin_dir_checkbox.setChecked(True)
        self.save_history_checkbox.setChecked(False)
        self.favorites_checkbox.setChecked(False)
        self.page_input.setText("")
        self.download_checkbox.setChecked(False)
        self.delay_input.setText("1")
        self.cbz_checkbox.setChecked(True)
        self.move_to_folder_checkbox.setChecked(False)
        self.format_input.setText('[%ag] - %p (%i)')
        self.output_input.setText('')

    def multiplePreset(self):
        # self.ids_input.setText("")
        self.rm_origin_dir_checkbox.setChecked(False)
        self.save_history_checkbox.setChecked(True)
        self.favorites_checkbox.setChecked(False)
        self.page_input.setText("")
        self.download_checkbox.setChecked(True)
        self.delay_input.setText("1")
        self.cbz_checkbox.setChecked(True)
        self.move_to_folder_checkbox.setChecked(True)
        self.format_input.setText('[%ag] - %p (%i)')
        self.output_input.setText('')

    def set_default_directory(self):
        # Open a file dialog to choose the default directory
        default_dir = QFileDialog.getExistingDirectory(self, "Select Default Directory")
        if default_dir:
            self.settings.setValue("default_doujins_folder", default_dir)

    def open_default_directory(self):
        path = os.path.realpath(self.settings.value("default_doujins_folder"))
        os.startfile(path)
    
    def set_cookie(self):
        if self.cookieHandler is None or not self.cookieHandler.isVisible():
            self.cookieHandler = CookieHandler()
        self.cookieHandler.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())