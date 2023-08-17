import sys
import subprocess
import re
import os

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel,
    QPushButton, QLineEdit, QCheckBox, QWidget,
    QFileDialog, QFrame, QHBoxLayout
)
from PyQt6.QtCore import QSettings, QFile, Qt

from CustomTitleBar import CustomTitleBar
from CookieHandler import CookieHandler


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMenuBar(None)
        self.cookieHandler = None
        
        # Get the directory of the script
        script_directory = os.path.dirname(os.path.abspath(__file__))

        # Determine the path for the settings file (INI) in the script's directory
        settings_file = os.path.join(script_directory, "settings.ini")
        self.settings = QSettings(settings_file, QSettings.Format.IniFormat)  # Create a QSettings instance

        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.MSWindowsFixedSizeDialogHint | Qt.WindowType.FramelessWindowHint)

        self.init_ui()


    def init_ui(self):
        # Create the custom title bar and add it to the layout
        custom_title_bar = CustomTitleBar(self)

        self.setWindowTitle("nHentai GUI")
        self.setGeometry(100, 100, 510, 300)
        self.center()

        layout = QVBoxLayout()

        layout.addWidget(custom_title_bar)

        # Create a container widget (QFrame) for the central widget
        central_container = QFrame()
        central_container.setObjectName("centralContainer")
        central_container.setLayout(layout)  # Set the layout for the container
        self.setCentralWidget(central_container)  # Set the container as the central widget

        self.run_button = QPushButton("Run Commands")
        self.run_button.clicked.connect(self.run_commands)

        # Elements for nhentai commands
        self.ids_input_label = QLabel("IDs (e.g., 302294 317039):")
        self.ids_input = QLineEdit(self.settings.value("ids_input", "302294 317039"))

        self.rm_origin_dir_checkbox = QCheckBox("Remove Original Directory")
        self.rm_origin_dir_checkbox.setMaximumWidth(200)
        self.save_history_checkbox = QCheckBox("Save Download History")
        self.save_history_checkbox.setMinimumWidth(200)
        self.favorites_checkbox = QCheckBox("Download Favorites")
        self.favorites_checkbox.setMinimumWidth(200)
        self.page_input_label = QLabel("Page Range \n(e.g. 1-6, 0 = all):")
        self.page_input_label.setMaximumWidth(100)
        self.page_input = QLineEdit(self.settings.value("page_input", "1-6"))
        self.page_input.setMaximumWidth(50)
        self.download_checkbox = QCheckBox("Download")
        self.download_checkbox.setMinimumWidth(110)
        self.delay_input_label = QLabel("Delay \n(seconds):")
        self.delay_input = QLineEdit(self.settings.value("delay_input", "1"))
        self.delay_input.setMaximumWidth(50)
        self.cbz_checkbox = QCheckBox("CBZ")
        self.cbz_checkbox.setMinimumWidth(70)
        self.move_to_folder_checkbox = QCheckBox("Move to Folder")
        self.move_to_folder_checkbox.setMinimumWidth(130)

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
        first_row_layout.addSpacing(10)
        first_row_layout.addWidget(self.delay_input_label)
        layout.addLayout(first_row_layout)

        # Create QHBoxLayout for the second row of input elements and checkboxes
        second_row_layout = QHBoxLayout()
        second_row_layout.addWidget(self.save_history_checkbox)
        second_row_layout.addWidget(self.page_input)
        second_row_layout.addSpacing(60)
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
            self.cookieHandler = CookieHandler(self)  # Pass MainWindow instance to CookieHandler
        self.cookieHandler.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())