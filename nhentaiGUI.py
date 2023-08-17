import sys
import subprocess
import re
import os

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel,
    QPushButton, QLineEdit, QCheckBox, QInputDialog,
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
        custom_title_bar = CustomTitleBar(self, self.settings)

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
        self.ids_input = QLineEdit("302294 317039")

        # Chech Boxes
        self.rm_origin_dir_checkbox = QCheckBox("Remove Original Directory")
        self.rm_origin_dir_checkbox.setMaximumWidth(200)

        self.save_history_checkbox = QCheckBox("Save Download History")
        self.save_history_checkbox.setMinimumWidth(200)

        self.favorites_checkbox = QCheckBox("Download Favorites")
        self.favorites_checkbox.setMinimumWidth(200)

        self.download_checkbox = QCheckBox("Download")
        self.download_checkbox.setMinimumWidth(110)

        self.move_to_folder_checkbox = QCheckBox("Move to Folder")
        self.move_to_folder_checkbox.setMinimumWidth(130)

        self.cbz_checkbox = QCheckBox("CBZ")
        self.cbz_checkbox.setMinimumWidth(70)

        self.pdf_checkbox = QCheckBox("PDF")
        self.pdf_checkbox.setMinimumWidth(80)

        self.dry_run_checkbox = QCheckBox("Dry Run")
        self.dry_run_checkbox.setMinimumWidth(130)

        self.html_checkbox = QCheckBox("HTML")
        self.html_checkbox.setMinimumWidth(130)

        self.no_html_checkbox = QCheckBox("No HTML")
        self.no_html_checkbox.setMinimumWidth(130)

        self.gen_main_checkbox = QCheckBox("Gen. Main")
        self.gen_main_checkbox.setMinimumWidth(130)

        self.meta_checkbox = QCheckBox("META")
        self.meta_checkbox.setMinimumWidth(130)

        # QLabels
        self.page_input_label = QLabel("Page Range \n(e.g. 1-6, 0 = all):")
        self.page_input_label.setMaximumWidth(100)

        self.delay_input_label = QLabel("Delay \n(seconds):")
        self.delay_input_label.setMaximumWidth(70)
       
        # QLineEdits
        self.page_input = QLineEdit("1-6")
        self.page_input.setMaximumWidth(50)

        self.delay_input = QLineEdit("1")
        self.delay_input.setMaximumWidth(50)

        self.format_input = QLineEdit('[%ag] - %p (%i)')
        self.output_input = QLineEdit("")

        # Add widgets to layout
        layout.addWidget(self.ids_input_label)
        layout.addWidget(self.ids_input)

        # Create QHBoxLayout for the first row of input elements and checkboxes
        first_row_layout = QHBoxLayout()
        first_row_layout.addWidget(self.rm_origin_dir_checkbox)
        first_row_layout.addSpacing(5)
        first_row_layout.addWidget(self.page_input_label)
        first_row_layout.addSpacing(10)
        first_row_layout.addWidget(self.delay_input_label)
        first_row_layout.addWidget(self.pdf_checkbox)
        layout.addLayout(first_row_layout)

        # Create QHBoxLayout for the second row of input elements and checkboxes
        second_row_layout = QHBoxLayout()
        second_row_layout.addWidget(self.save_history_checkbox)
        second_row_layout.addWidget(self.page_input)
        second_row_layout.addSpacing(60)
        second_row_layout.addWidget(self.delay_input)
        second_row_layout.addSpacing(20)
        second_row_layout.addWidget(self.dry_run_checkbox)
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

        # TODO fourth row with more options
        # TODO think about better places to put settings 
        fourth_row_layout = QHBoxLayout()
        fourth_row_layout.addWidget(self.html_checkbox)
        fourth_row_layout.addWidget(self.no_html_checkbox)
        fourth_row_layout.addWidget(self.gen_main_checkbox)
        fourth_row_layout.addWidget(self.meta_checkbox)
        layout.addLayout(fourth_row_layout)


        layout.addWidget(QLabel("Format:"))
        layout.addWidget(self.format_input)
        layout.addWidget(QLabel("Output Folder:"))
        layout.addWidget(self.output_input)
        layout.addWidget(self.run_button)

        self.load_ui_states()

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
        self.settings.setValue("pdf_checkbox", self.pdf_checkbox.isChecked())
        self.settings.setValue("dry_run_checkbox", self.dry_run_checkbox.isChecked())
        self.settings.setValue("html_checkbox", self.html_checkbox.isChecked())
        self.settings.setValue("no_html_checkbox", self.no_html_checkbox.isChecked())
        self.settings.setValue("gen_main_checkbox", self.gen_main_checkbox.isChecked())
        self.settings.setValue("meta_checkbox", self.meta_checkbox.isChecked())

        event.accept()

    def load_ui_states(self):
        # Load checkbox states
        self.rm_origin_dir_checkbox.setChecked(self.settings.value("rm_origin_dir_checkbox", False, type=bool))
        self.save_history_checkbox.setChecked(self.settings.value("save_history_checkbox", False, type=bool))
        self.favorites_checkbox.setChecked(self.settings.value("favorites_checkbox", False, type=bool))
        self.download_checkbox.setChecked(self.settings.value("download_checkbox", False, type=bool))
        self.cbz_checkbox.setChecked(self.settings.value("cbz_checkbox", False, type=bool))
        self.move_to_folder_checkbox.setChecked(self.settings.value("move_to_folder_checkbox", False, type=bool))
        self.pdf_checkbox.setChecked(self.settings.value("pdf_checkbox", False, type=bool))
        self.dry_run_checkbox.setChecked(self.settings.value("dry_run_checkbox", False, type=bool))
        self.html_checkbox.setChecked(self.settings.value("html_checkbox", False, type=bool))
        self.no_html_checkbox.setChecked(self.settings.value("no_html_checkbox", False, type=bool))
        self.gen_main_checkbox.setChecked(self.settings.value("gen_main_checkbox", False, type=bool))
        self.meta_checkbox.setChecked(self.settings.value("meta_checkbox", False, type=bool))

        # Load QLineEdit states
        self.ids_input.setText(self.settings.value("ids_input", "302294 317039", type=str))
        self.page_input.setText(self.settings.value("page_input", "1-6", type=str))
        self.delay_input.setText(self.settings.value("delay_input", "1", type=str))
        self.format_input.setText(self.settings.value("format_input", "[%ag] - %p (%i)", type=str))
        self.output_input.setText(self.settings.value("output_input", "", type=str))

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
        if self.pdf_checkbox.isChecked():
            commands += " --pdf"
        if self.html_checkbox.isChecked():
            commands += " --pdf"
        if self.no_html_checkbox.isChecked():
            commands += " --html"
        if self.dry_run_checkbox.isChecked():
            commands += " --no-html"   
        if self.gen_main_checkbox.isChecked():
            commands += " --gen-main"
        if self.meta_checkbox.isChecked():
            commands += " --meta"     
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
            commands += f' --output "{self.settings.value("default_doujins_folder", "C:/Doujins")}/{cleaned_output_text}/"'
        else:
            commands += f' --output "{self.settings.value("default_doujins_folder", "C:/Doujins")}"'

        print(commands)

        # Open the terminal externally and run the commands
        subprocess.Popen(commands, shell=True)
        
    def add_preset(self):
        preset_name, ok = QInputDialog.getText(self, 'New Preset', 'Enter your preset name:')
        if ok:
            print(f"The preset {preset_name} was added!")
        else:
            return
        
        cleaned_preset_name = preset_name.replace(" ", "-")
        self.settings.beginGroup(f"Preset_{cleaned_preset_name}")

        self.settings.setValue("rm_origin_dir_checkbox", self.rm_origin_dir_checkbox.isChecked())
        self.settings.setValue("save_history_checkbox", self.save_history_checkbox.isChecked())
        self.settings.setValue("favorites_checkbox", self.favorites_checkbox.isChecked())
        self.settings.setValue("download_checkbox", self.download_checkbox.isChecked())
        self.settings.setValue("cbz_checkbox", self.cbz_checkbox.isChecked())
        self.settings.setValue("move_to_folder_checkbox", self.move_to_folder_checkbox.isChecked())
        self.settings.setValue("pdf_checkbox", self.pdf_checkbox.isChecked())
        self.settings.setValue("dry_run_checkbox", self.dry_run_checkbox.isChecked())
        self.settings.setValue("html_checkbox", self.html_checkbox.isChecked())
        self.settings.setValue("no_html_checkbox", self.no_html_checkbox.isChecked())
        self.settings.setValue("gen_main_checkbox", self.gen_main_checkbox.isChecked())
        self.settings.setValue("meta_checkbox", self.meta_checkbox.isChecked())

        self.settings.setValue("page_input", self.page_input.text())
        self.settings.setValue("delay_input", self.delay_input.text())
        self.settings.setValue("format_input", self.format_input.text())

        self.settings.endGroup()

    def load_preset(self, preset_name):
        cleaned_preset_name = preset_name.replace(" ", "-")
        self.settings.beginGroup(f"Preset_{cleaned_preset_name}")

        self.rm_origin_dir_checkbox.setChecked(self.settings.value("rm_origin_dir_checkbox", False, type=bool))
        self.save_history_checkbox.setChecked(self.settings.value("save_history_checkbox", False, type=bool))
        self.favorites_checkbox.setChecked(self.settings.value("favorites_checkbox", False, type=bool))
        self.download_checkbox.setChecked(self.settings.value("download_checkbox", False, type=bool))
        self.cbz_checkbox.setChecked(self.settings.value("cbz_checkbox", False, type=bool))
        self.move_to_folder_checkbox.setChecked(self.settings.value("move_to_folder_checkbox", False, type=bool))
        self.pdf_checkbox.setChecked(self.settings.value("pdf_checkbox", False, type=bool))
        self.dry_run_checkbox.setChecked(self.settings.value("dry_run_checkbox", False, type=bool))
        self.html_checkbox.setChecked(self.settings.value("html_checkbox", False, type=bool))
        self.no_html_checkbox.setChecked(self.settings.value("no_html_checkbox", False, type=bool))
        self.gen_main_checkbox.setChecked(self.settings.value("gen_main_checkbox", False, type=bool))
        self.meta_checkbox.setChecked(self.settings.value("meta_checkbox", False, type=bool))

        self.page_input.setText(self.settings.value("page_input", "1-6", type=str))
        self.delay_input.setText(self.settings.value("delay_input", "1", type=str))
        self.format_input.setText(self.settings.value("format_input", "[%ag] - %p (%i)", type=str))

        self.settings.endGroup()

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
            self.cookieHandler = CookieHandler(self, self.settings)  # Pass MainWindow instance to CookieHandler
        self.cookieHandler.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())