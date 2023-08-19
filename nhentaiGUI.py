import sys
import subprocess
import re
import os

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel,
    QPushButton, QLineEdit, QCheckBox, QInputDialog,
    QFileDialog, QFrame, QHBoxLayout, QMessageBox,
    QComboBox
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
        self.ids_input_label.setStyleSheet("padding-left: 80px;")
        self.ids_input = QLineEdit("302294 317039")
        self.ids_input.setObjectName("ids_input")

        # Chech Boxes
        self.rm_origin_dir_checkbox = QCheckBox("Remove Original Directory")
        self.rm_origin_dir_checkbox.setObjectName("rm_origin_dir_checkbox")
        self.rm_origin_dir_checkbox.setMinimumWidth(200)

        self.save_history_checkbox = QCheckBox("Save Download History")
        self.save_history_checkbox.setObjectName("save_history_checkbox")
        self.save_history_checkbox.setMinimumWidth(200)

        self.favorites_checkbox = QCheckBox("Download Favorites")
        self.favorites_checkbox.setObjectName("favorites_checkbox")
        self.favorites_checkbox.setMinimumWidth(200)

        self.download_checkbox = QCheckBox("Download")
        self.download_checkbox.setObjectName("download_checkbox")
        self.download_checkbox.setMinimumWidth(110)

        self.move_to_folder_checkbox = QCheckBox("Move to Folder")
        self.move_to_folder_checkbox.setObjectName("move_to_folder_checkbox")
        self.move_to_folder_checkbox.setMinimumWidth(130)

        self.cbz_checkbox = QCheckBox("CBZ")
        self.cbz_checkbox.setObjectName("cbz_checkbox")
        self.cbz_checkbox.setMinimumWidth(70)

        self.pdf_checkbox = QCheckBox("PDF")
        self.pdf_checkbox.setObjectName("pdf_checkbox")
        self.pdf_checkbox.setMinimumWidth(80)

        self.dry_run_checkbox = QCheckBox("Dry Run")
        self.dry_run_checkbox.setObjectName("dry_run_checkbox")
        self.dry_run_checkbox.setMinimumWidth(130)

        self.html_checkbox = QCheckBox("HTML")
        self.html_checkbox.setObjectName("html_checkbox")
        self.html_checkbox.setMaximumWidth(90)

        self.no_html_checkbox = QCheckBox("No HTML")
        self.no_html_checkbox.setObjectName("no_html_checkbox")
        self.no_html_checkbox.setMaximumWidth(105)

        self.gen_main_checkbox = QCheckBox("Gen. Main")
        self.gen_main_checkbox.setObjectName("gen_main_checkbox")
        self.gen_main_checkbox.setMaximumWidth(110)

        self.meta_checkbox = QCheckBox("META")
        self.meta_checkbox.setObjectName("meta_checkbox")
        self.meta_checkbox.setMaximumWidth(70)

        self.regen_cbz_checkbox = QCheckBox("Regen CBZ")
        self.regen_cbz_checkbox.setObjectName("regen_cbz_checkbox")
        self.regen_cbz_checkbox.setMaximumWidth(135)

        self.search_checkbox = QCheckBox("Search")
        self.search_checkbox.setObjectName("search_checkbox")
        # self.search_checkbox.setMaximumWidth(135)

        # QLabels
        self.page_input_label = QLabel("Page Range \n(e.g. 1-6, 0 = all):")
        self.page_input_label.setMaximumWidth(100)

        self.delay_input_label = QLabel("Delay \n(seconds):")
        self.delay_input_label.setMaximumWidth(70)

        # QLineEdits
        self.page_input = QLineEdit("1-6")
        self.page_input.setObjectName("page_input")
        self.page_input.setMaximumWidth(50)

        self.delay_input = QLineEdit("1")
        self.delay_input.setObjectName("delay_input")
        self.delay_input.setMaximumWidth(50)

        self.format_input = QLineEdit('[%ag] - %p (%i)')
        self.format_input.setObjectName("format_input")
        self.output_input = QLineEdit("")
        self.output_input.setObjectName("output_input")

        # QComboBox
        self.sorting_combo_box = QComboBox()
        self.sorting_combo_box.addItems(['-','Recent','Popular','Popular Today','Popular Week'])
        self.sorting_combo_box.setMinimumWidth(130)

        # Add widgets to layout
        layout.addWidget(self.ids_input_label)

        # Create QHBoxLayout for the first row of input elements and checkboxes
        first_row_layout = QHBoxLayout()
        first_row_layout.addWidget(self.search_checkbox)
        first_row_layout.addWidget(self.ids_input)
        first_row_layout.addWidget(self.sorting_combo_box)
        layout.addLayout(first_row_layout)

        # Create QHBoxLayout for the first row of input elements and checkboxes
        second_row_layout = QHBoxLayout()
        second_row_layout.addWidget(self.rm_origin_dir_checkbox)
        second_row_layout.addSpacing(5)
        second_row_layout.addWidget(self.page_input_label)
        second_row_layout.addSpacing(5)
        second_row_layout.addWidget(self.delay_input_label)
        second_row_layout.addWidget(self.pdf_checkbox)
        layout.addLayout(second_row_layout)

        # Create QHBoxLayout for the second row of input elements and checkboxes
        third_row_layout = QHBoxLayout()
        third_row_layout.addWidget(self.save_history_checkbox)
        third_row_layout.addWidget(self.page_input)
        third_row_layout.addSpacing(60)
        third_row_layout.addWidget(self.delay_input)
        third_row_layout.addSpacing(20)
        third_row_layout.addWidget(self.dry_run_checkbox)
        third_row_layout.addStretch(1)
        layout.addLayout(third_row_layout)

        # Create QHBoxLayout for the third row of input elements and checkboxes
        fourth_row_layout = QHBoxLayout()
        fourth_row_layout.addWidget(self.favorites_checkbox)
        fourth_row_layout.addWidget(self.download_checkbox)
        fourth_row_layout.addWidget(self.cbz_checkbox)
        fourth_row_layout.addWidget(self.move_to_folder_checkbox)
        fourth_row_layout.addStretch(1)
        layout.addLayout(fourth_row_layout)

        # Create QHBoxLayout for the fourth row of input elements and checkboxes
        fifth_row_layout = QHBoxLayout()
        fifth_row_layout.addWidget(self.html_checkbox)
        fifth_row_layout.addWidget(self.no_html_checkbox)
        fifth_row_layout.addWidget(self.gen_main_checkbox)
        fifth_row_layout.addWidget(self.meta_checkbox)
        fifth_row_layout.addWidget(self.regen_cbz_checkbox)
        layout.addLayout(fifth_row_layout)


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
        self.save_ui_states()
        event.accept()

    def load_ui_states(self):
        # Load checkbox states
        checkboxes = [
            self.rm_origin_dir_checkbox, self.save_history_checkbox, self.favorites_checkbox,
            self.download_checkbox, self.cbz_checkbox, self.move_to_folder_checkbox,
            self.pdf_checkbox, self.dry_run_checkbox, self.html_checkbox, self.no_html_checkbox,
            self.gen_main_checkbox, self.meta_checkbox, self.regen_cbz_checkbox, self.search_checkbox
        ]
        for checkbox in checkboxes:
            checkbox.setChecked(self.settings.value(checkbox.objectName(), False, type=bool))

        # Load QLineEdit states
        line_edits = [
            (self.ids_input, "302294 317039"),
            (self.page_input, "1-6"),
            (self.delay_input, "1"),
            (self.format_input, "[%ag] - %p (%i)"),
            (self.output_input, "")
        ]
        for line_edit, default_value in line_edits:
            line_edit.setText(self.settings.value(line_edit.objectName(), default_value, type=str))

    def save_ui_states(self):
        # Save checkbox states
        checkboxes = [
            self.rm_origin_dir_checkbox, self.save_history_checkbox, self.favorites_checkbox,
            self.download_checkbox, self.cbz_checkbox, self.move_to_folder_checkbox,
            self.pdf_checkbox, self.dry_run_checkbox, self.html_checkbox, self.no_html_checkbox,
            self.gen_main_checkbox, self.meta_checkbox, self.regen_cbz_checkbox, self.search_checkbox
        ]
        for checkbox in checkboxes:
            self.settings.setValue(checkbox.objectName(), checkbox.isChecked())

        # Save QLineEdit states
        line_edits = [
            self.ids_input, self.page_input, self.delay_input, self.format_input, self.output_input
        ]
        for line_edit in line_edits:
            self.settings.setValue(line_edit.objectName(), line_edit.text())

    def run_commands(self):
        # Assemble the nhentai command based on user inputs
        commands = "nhentai"
        selected_sorting_option = self.sorting_combo_box.currentText()

        if self.ids_input.text() and not self.search_checkbox.isChecked():
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
            commands += " --html"
        if self.no_html_checkbox.isChecked():
            commands += " --no-html"
        if self.dry_run_checkbox.isChecked():
            commands += " --dry-run"   
        if self.gen_main_checkbox.isChecked():
            commands += " --gen-main"
        if self.meta_checkbox.isChecked():
            commands += " --meta"     
        if self.regen_cbz_checkbox.isChecked():
            commands += " --regenerate-cbz" 
        if self.search_checkbox.isChecked():
            commands += f" --search \"{self.ids_input.text()}\"" 
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
        if self.sorting_combo_box.currentText() != "-":
            if selected_sorting_option == 'Recent':
                commands += " --sorting=recent"
            elif selected_sorting_option == 'Popular':
                commands += " --sorting=popular"
            elif selected_sorting_option == 'Popular Today':
                commands += " --sorting=popular-today"
            elif selected_sorting_option == 'Popular Week':
                commands += " --sorting=popular-week"

        print(commands)

        # Open the terminal externally and run the commands
        subprocess.Popen(commands, shell=True)

    def run_specific_command(self, command):
        # Open the terminal externally and run the commands
        commands = (f"nhentai {command}")
        print(commands)
        subprocess.Popen(commands, shell=True)
        
    def add_preset(self):
        preset_name, ok = QInputDialog.getText(self, 'New Preset', 'Enter your preset name:')
        if ok:
            print(f"The preset {preset_name} was added!")
        else:
            return
        
        cleaned_preset_name = preset_name.replace(" ", "-")
        self.settings.beginGroup(f"Preset_{cleaned_preset_name}")

        self.save_ui_states()

        self.settings.endGroup()

    def load_preset(self, preset_name):
        cleaned_preset_name = preset_name.replace(" ", "-")
        self.settings.beginGroup(f"Preset_{cleaned_preset_name}")

        self.load_ui_states()

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

    def set_language(self):
        language, ok = QInputDialog.getText(self, 'Set Language', 'Enter Language:')
        if ok:
            command = (f" --language={language}")
            self.run_specific_command(command)
            print(f"The language {language} has been set!")
        else:
            return

    def clean_language(self):
        confirm = QMessageBox.question(self, "Confirmation", "Are you sure you want to do this?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                       QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            self.run_specific_command(" --clean-language")
        else:
            print("User canceled.")
            return
        
    def clean_download_history(self):
        confirm = QMessageBox.question(self, "Confirmation", "Are you sure you want to do this?\nThis cannot be undone: Delete All Download History",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                       QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            self.run_specific_command(" --clean-download-history")
        else:
            print("User canceled.")
            return
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())