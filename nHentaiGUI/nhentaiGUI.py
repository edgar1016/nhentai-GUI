import sys
import subprocess
import re
import os
import resources_rc

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel,
    QPushButton, QLineEdit, QCheckBox, QInputDialog,
    QFileDialog, QFrame, QHBoxLayout, QMessageBox,
    QComboBox
)
from PyQt6.QtCore import QSettings, QFile, Qt, QCoreApplication
from PyQt6.QtGui import QIcon

from CustomTitleBar import CustomTitleBar
from CookieHandler import CookieHandler


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMenuBar(None)
        self.cookieHandler = None


        
        QCoreApplication.setOrganizationName("Edgar1016")
        QCoreApplication.setApplicationName("nHentai_GUI")

        # INI use for python
        script_directory = os.path.dirname(os.path.abspath(__file__))
        settings_file = os.path.join(script_directory, "settings.ini")
        self.settings = QSettings(settings_file, QSettings.Format.IniFormat)  # Create a QSettings instance


        # INI use for built exe
        # executable_path = sys.executable
        # settings_file = os.path.join(os.path.dirname(executable_path), "settings.ini")
        # self.settings = QSettings(settings_file, QSettings.Format.IniFormat)  # Create a QSettings instance

        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)

        self.init_ui()


    def init_ui(self):
        # Create the custom title bar and add it to the layout
        custom_title_bar = CustomTitleBar(self, self.settings)
        self.file_name = None

        self.setWindowTitle("nHentai GUI")
        icon = QIcon(":/resources/favicon.ico")
        self.setWindowIcon(icon)
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

        self.file_button = QPushButton("Select File")
        self.file_button.setObjectName("file_button")
        self.file_button.clicked.connect(self.use_file)
        self.file_button.setEnabled(False)

        self.ids_input = QLineEdit("")
        self.ids_input.setObjectName("ids_input")
        self.ids_input.setPlaceholderText("IDs (e.g., 317039 or #302294 )")

        # Chech Boxes
        self.rm_origin_dir_checkbox = QCheckBox("Remove Original Directory")
        self.rm_origin_dir_checkbox.setObjectName("rm_origin_dir_checkbox")
        self.rm_origin_dir_checkbox.setToolTip("Remove downloaded doujinshi dir when generated CBZ or PDF file")
        self.rm_origin_dir_checkbox.setMinimumWidth(200)

        self.save_history_checkbox = QCheckBox("Save Download History")
        self.save_history_checkbox.setObjectName("save_history_checkbox")
        self.save_history_checkbox.setToolTip("Save downloaded doujinshis, whose will be skipped if you re-download them")
        self.save_history_checkbox.setMinimumWidth(200)
        
        self.artist_checkbox = QCheckBox("Artist")
        self.artist_checkbox.setObjectName("artist_checkbox")
        self.artist_checkbox.setToolTip("List doujinshi by artist name")
        self.artist_checkbox.setMinimumWidth(90)
        self.artist_checkbox.stateChanged.connect(self.artist_checkbox_state_changed)

        self.favorites_checkbox = QCheckBox("Favorites")
        self.favorites_checkbox.setObjectName("favorites_checkbox")
        self.favorites_checkbox.setToolTip("List or download your favorites")
        self.favorites_checkbox.setMinimumWidth(104)

        self.download_checkbox = QCheckBox("Download")
        self.download_checkbox.setObjectName("download_checkbox")
        self.download_checkbox.setToolTip("Download doujinshi (from search results)")
        self.download_checkbox.setMinimumWidth(110)

        self.move_to_folder_checkbox = QCheckBox("Move to Folder")
        self.move_to_folder_checkbox.setObjectName("move_to_folder_checkbox")
        self.move_to_folder_checkbox.setToolTip("When generating CBZ or PDF file removes files in doujinshi directory then move new archive to a folder with same name")
        self.move_to_folder_checkbox.setMinimumWidth(130)

        self.cbz_checkbox = QCheckBox("CBZ")
        self.cbz_checkbox.setObjectName("cbz_checkbox")
        self.cbz_checkbox.setToolTip("Generate Comic Book CBZ File")
        self.cbz_checkbox.setMinimumWidth(70)

        self.pdf_checkbox = QCheckBox("PDF")
        self.pdf_checkbox.setObjectName("pdf_checkbox")
        self.pdf_checkbox.setToolTip("Generate PDF file")
        self.pdf_checkbox.setMinimumWidth(130)

        self.dry_run_checkbox = QCheckBox("Dry Run")
        self.dry_run_checkbox.setObjectName("dry_run_checkbox")
        self.dry_run_checkbox.setToolTip("Dry run, skips file download for reference")
        self.dry_run_checkbox.setMinimumWidth(130)

        self.show_checkbox = QCheckBox("Show")
        self.show_checkbox.setObjectName("show_checkbox")
        self.show_checkbox.setToolTip("Only shows the doujinshi information")
        self.show_checkbox.setMaximumWidth(90)

        self.no_html_checkbox = QCheckBox("No HTML")
        self.no_html_checkbox.setObjectName("no_html_checkbox")
        self.no_html_checkbox.setToolTip("Don't generate HTML after downloading")
        self.no_html_checkbox.setMaximumWidth(104)

        self.gen_main_checkbox = QCheckBox("Gen. Main")
        self.gen_main_checkbox.setObjectName("gen_main_checkbox")
        self.gen_main_checkbox.setToolTip("Generate a main viewer contain all the doujin in the folder") #TODO Might needs to reword this
        self.gen_main_checkbox.setMaximumWidth(110)

        self.meta_checkbox = QCheckBox("META")
        self.meta_checkbox.setObjectName("meta_checkbox")
        self.meta_checkbox.setToolTip("Generate a metadata file in doujinshi format")
        self.meta_checkbox.setMaximumWidth(70)

        self.regen_cbz_checkbox = QCheckBox("Regen CBZ")
        self.regen_cbz_checkbox.setObjectName("regen_cbz_checkbox")
        self.regen_cbz_checkbox.setToolTip("Regenerate the cbz or pdf file if exists")
        self.regen_cbz_checkbox.setMaximumWidth(135)

        self.search_checkbox = QCheckBox("Search")
        self.search_checkbox.setObjectName("search_checkbox")
        self.search_checkbox.setToolTip("Search doujinshi by keyword")
        self.search_checkbox.stateChanged.connect(self.search_checkbox_state_changed)

        self.file_checkbox = QCheckBox("File: ")
        self.file_checkbox.setObjectName("file_checkbox")
        self.file_checkbox.setToolTip("Read gallery IDs from file.")
        self.file_checkbox.stateChanged.connect(self.file_checkbox_state_changed)
        self.file_checkbox.setMaximumWidth(90)

        # QLabels
        self.page_input_label = QLabel("Page \nRange:")
        self.page_input_label.setMaximumWidth(100)

        self.delay_input_label = QLabel("Delay \n(seconds):")
        self.delay_input_label.setMaximumWidth(70)

        self.thereads_input_label = QLabel("\nThreads:")
        self.thereads_input_label.setMaximumWidth(70)

        # QLineEdits
        self.page_input = QLineEdit("")
        self.page_input.setObjectName("page_input")
        self.page_input.setToolTip("(e.g. 1-6, 0 = all)")
        self.page_input.setMaximumWidth(50)

        self.delay_input = QLineEdit("1")
        self.delay_input.setObjectName("delay_input")
        self.delay_input.setToolTip("Delay between downloading each doujinshi\n to avoid being timed out.")
        self.delay_input.setMaximumWidth(54)

        self.threads_input = QLineEdit("")
        self.threads_input.setObjectName("threads_input")
        self.threads_input.setToolTip("Thread count for downloading doujinshi")
        self.threads_input.setMaximumWidth(70)

        self.format_input = QLineEdit('')
        self.format_input.setObjectName("format_input")
        tooltip_text = (
            "%i: Doujinshi ID\n"
            "%t: Doujinshi name\n"
            "%s: Doujinshi subtitle (translated name)\n"
            "%a: Doujinshi author(s)\n"
            "%g: Doujinshi group(s)\n"
            "%p: Doujinshi pretty name\n"
            "%ag: Doujinshi author(s) or group(s)"
        )
        self.format_input.setToolTip(tooltip_text)
        self.format_input.setPlaceholderText("[%ag] - %p (%i)")

        self.output_input = QLineEdit("")
        self.output_input.setObjectName("output_input")

        # QComboBox
        self.sorting_combo_box = QComboBox()
        self.sorting_combo_box.addItems(['-','Recent','Popular','Popular Today','Popular Week'])
        self.sorting_combo_box.setObjectName("sorting_combo_box")
        self.sorting_combo_box.setToolTip("Sorting order of doujinshi (recent / popular /popular-[today|week])")
        self.sorting_combo_box.setMinimumWidth(130)

        # Add widgets to layout

        # Create QHBoxLayout for the first row
        first_row_layout = QHBoxLayout()
        first_row_layout.addWidget(self.search_checkbox)
        first_row_layout.addWidget(self.ids_input)
        first_row_layout.addWidget(self.sorting_combo_box)
        layout.addLayout(first_row_layout)

        # Create QHBoxLayout for the second row
        second_row_layout = QHBoxLayout()
        second_row_layout.addWidget(self.rm_origin_dir_checkbox)
        second_row_layout.addWidget(self.page_input_label)
        second_row_layout.addWidget(self.delay_input_label)
        second_row_layout.addWidget(self.thereads_input_label)
        second_row_layout.addSpacing(16)
        second_row_layout.addWidget(self.pdf_checkbox)
        layout.addLayout(second_row_layout)

        # Create QHBoxLayout for the third row
        third_row_layout = QHBoxLayout()
        third_row_layout.addWidget(self.save_history_checkbox)
        third_row_layout.addWidget(self.page_input)
        third_row_layout.addWidget(self.delay_input)
        third_row_layout.addWidget(self.threads_input)
        third_row_layout.addWidget(self.dry_run_checkbox)
        third_row_layout.addStretch(1)
        layout.addLayout(third_row_layout)

        # Create QHBoxLayout for the fourth row
        fourth_row_layout = QHBoxLayout()
        fourth_row_layout.addWidget(self.artist_checkbox)
        fourth_row_layout.addWidget(self.favorites_checkbox)
        fourth_row_layout.addWidget(self.download_checkbox)
        fourth_row_layout.addWidget(self.cbz_checkbox)
        fourth_row_layout.addWidget(self.move_to_folder_checkbox)
        fourth_row_layout.addStretch(1)
        layout.addLayout(fourth_row_layout)

        # Create QHBoxLayout for the fifth row
        fifth_row_layout = QHBoxLayout()
        fifth_row_layout.addWidget(self.show_checkbox)
        fifth_row_layout.addWidget(self.no_html_checkbox)
        fifth_row_layout.addWidget(self.gen_main_checkbox)
        fifth_row_layout.addWidget(self.meta_checkbox)
        fifth_row_layout.addWidget(self.regen_cbz_checkbox)
        layout.addLayout(fifth_row_layout)

        # Create QHBoxLayout for the sixth row
        sixth_row_layout = QHBoxLayout()
        sixth_row_layout.addWidget(self.file_checkbox)
        sixth_row_layout.addWidget(self.file_button)
        layout.addLayout(sixth_row_layout)

        # Add inputs to the QVBoxLayout
        layout.addWidget(QLabel("Format:"))
        layout.addWidget(self.format_input)
        layout.addWidget(QLabel("Output Folder:"))
        layout.addWidget(self.output_input)
        layout.addWidget(self.run_button)

        self.load_ui_states()

        style_file = QFile(":/resources/styles.qss")
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
            self.pdf_checkbox, self.dry_run_checkbox, self.show_checkbox, self.no_html_checkbox,
            self.gen_main_checkbox, self.meta_checkbox, self.regen_cbz_checkbox, self.search_checkbox,
            self.file_checkbox, self.artist_checkbox
        ]
        for checkbox in checkboxes:
            checkbox.setChecked(self.settings.value(checkbox.objectName(), False, type=bool))

        # Load QLineEdit states
        line_edits = [
            (self.ids_input, ""),
            (self.page_input, ""),
            (self.delay_input, "1"),
            (self.format_input, ""),
            (self.output_input, ""),
            (self.threads_input, "")
        ]
        for line_edit, default_value in line_edits:
            line_edit.setText(self.settings.value(line_edit.objectName(), default_value, type=str))



        combo_boxes = [
            self.sorting_combo_box
        ]
        for cbBox in combo_boxes:
            cbBox.setCurrentIndex(self.settings.value(cbBox.objectName(), cbBox.setCurrentIndex(0), type=int))


    def save_ui_states(self):
        # Save checkbox states
        checkboxes = [
            self.rm_origin_dir_checkbox, self.save_history_checkbox, self.favorites_checkbox,
            self.download_checkbox, self.cbz_checkbox, self.move_to_folder_checkbox,
            self.pdf_checkbox, self.dry_run_checkbox, self.show_checkbox, self.no_html_checkbox,
            self.gen_main_checkbox, self.meta_checkbox, self.regen_cbz_checkbox, self.search_checkbox,
            self.file_checkbox, self.artist_checkbox
        ]
        for checkbox in checkboxes:
            self.settings.setValue(checkbox.objectName(), checkbox.isChecked())

        # Save QLineEdit states
        line_edits = [
            self.ids_input, 
            self.page_input, 
            self.delay_input, 
            self.format_input, 
            self.output_input, 
            self.threads_input
        ]
        for line_edit in line_edits:
            self.settings.setValue(line_edit.objectName(), line_edit.text())

        # Save QComboBox states
        combo_boxes = [
            self.sorting_combo_box
        ]
        for cbBox in combo_boxes:
            self.settings.setValue(cbBox.objectName(), cbBox.currentIndex())

    def run_commands(self):
        # Assemble the nhentai command based on user inputs
        commands = "nhentai"
        selected_sorting_option = self.sorting_combo_box.currentText()

        if self.ids_input.text() and not self.search_checkbox.isChecked() and not self.artist_checkbox.isChecked():
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
        if self.show_checkbox.isChecked():
            commands += " --show"
        if self.no_html_checkbox.isChecked():
            commands += " --no-html"
        if self.dry_run_checkbox.isChecked():
            commands += " --dry-run"   
        if self.gen_main_checkbox.isChecked():
            commands += " --gen-main"
        if self.meta_checkbox.isChecked():
            commands += " --meta"     
        if self.regen_cbz_checkbox.isChecked():
            commands += " --regenerate" 
        if self.file_checkbox.isChecked() and self.file_name is not None:
            commands += f" --file=\"{self.file_name}\"" 
        if self.search_checkbox.isChecked():
            commands += f" --search \"{self.ids_input.text()}\""    
        if self.artist_checkbox.isChecked():
            cleaned_output_text = self.ids_input.text().replace(" ", "-")
            commands += f" --artist=\"{cleaned_output_text}\""
        if self.page_input.text():
            if self.page_input.text() == "0":
                commands += f" --page-all"
            else:
                commands += f" --page={self.page_input.text()}"
        if self.download_checkbox.isChecked():
            commands += " --download"
        if self.delay_input.text():
            commands += f" --delay {self.delay_input.text()}"
        if self.threads_input.text():
            commands += f" --threads={self.threads_input.text()}"
        if self.cbz_checkbox.isChecked():
            commands += " --cbz"
        if self.move_to_folder_checkbox.isChecked():
            commands += " --move-to-folder"
        if self.format_input.text():
            commands += f' --format "{self.format_input.text()}"'

        if not self.output_input.text() and not self.settings.value("default_doujins_folder"):
            QMessageBox.critical(self, "Error", "Please provide an output path or set the default doujins folder.")
            return
        else:
            commands += f' --output "{self.output_command()}"'

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

    def output_command(self):
        cleaned_output_text = re.sub(r'[\\/*?:"<>|]', "-", self.output_input.text().strip())
        default_folder = self.settings.value("default_doujins_folder")
        output_path = default_folder if default_folder and not self.output_input.text() else self.output_input.text()
        
        if default_folder and self.output_input.text():
            output_path = f'{default_folder}/{cleaned_output_text}/'

        return output_path
        
    def add_preset(self):
        preset_name, ok = QInputDialog.getText(self, 'New Preset', 'Enter your preset name:')
        if ok:
            print(f"The preset {preset_name} was added!")
        else:
            return
        
        cleaned_preset_name = preset_name.replace(" ", "-")

        # Create a presents group in the settings.ini
        self.settings.beginGroup(f"Preset_{cleaned_preset_name}")

        self.save_ui_states()

        self.settings.endGroup()

    def load_preset(self, preset_name):
        cleaned_preset_name = preset_name.replace(" ", "-")

        # Load the presents group in the settings.ini
        self.settings.beginGroup(f"Preset_{cleaned_preset_name}")

        self.load_ui_states()

        self.settings.endGroup()

    def update_preset(self):
        preset_names = self.settings.childGroups()
        sorted_preset_names = sorted(preset_names, key=lambda x: x.lower())
        presentable_presets = [preset.replace("Preset_", "").replace("-", " ") for preset in sorted_preset_names]

        input_dialog = QInputDialog()
        input_dialog.setWindowTitle("Update Preset")
        input_dialog.setLabelText("Select a Preset")
        input_dialog.setOkButtonText("Update")

        style_file = QFile(":/resources/styles.qss")
        if style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            style_sheet = style_file.readAll()
            input_dialog.setStyleSheet(str(style_sheet, encoding="utf-8"))

        input_dialog.setOption(QInputDialog.InputDialogOption.UseListViewForComboBoxItems)
        input_dialog.setComboBoxItems(presentable_presets)

        if input_dialog.exec() == 1:
            selected_preset = input_dialog.textValue()
            cleaned_preset_name = selected_preset.replace(" ", "-")

            self.settings.beginGroup(f"Preset_{cleaned_preset_name}")
            self.save_ui_states()
            self.settings.endGroup()

    def set_default_directory(self):
        default_dir = QFileDialog.getExistingDirectory(self, "Select Default Directory")
        if default_dir:
            self.settings.setValue("default_doujins_folder", default_dir)

    def open_default_directory(self):
        default_folder = self.settings.value("default_doujins_folder")
        
        if not default_folder:
            QMessageBox.critical(self, "Error", "Default doujins folder is not set.")
            return
        
        if not os.path.exists(default_folder):
            QMessageBox.critical(self, "Error", "Default doujins folder does not exist.")
            return

        try:
            if sys.platform == "win32":
                os.startfile(default_folder)  # For Windows
            elif sys.platform == "Darwin": 
                subprocess.Popen(["open", default_folder]) # macOS
            else:  
                subprocess.Popen(["xdg-open", default_folder]) # Linux
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open directory: {str(e)}")
    
    def set_cookie(self):
        if self.cookieHandler is None or not self.cookieHandler.isVisible():
            self.cookieHandler = CookieHandler(self, self.settings)  # Pass MainWindow instance to CookieHandler
        self.cookieHandler.show()

    def set_language(self):
        items = ['english','chinese','japanese','translated',]

        # Combo Box to choose between the language constants
        language, ok = QInputDialog.getItem(self, 'Set Language', 'Enter Language:', items)

        if ok:
            command = (f" --language={language}")
            self.run_specific_command(command)
        else:
            return
        
    def search_checkbox_state_changed(self, state):
        self.ids_input.clear()

        if state == 2:
            if self.artist_checkbox.isChecked():
                self.artist_checkbox.setChecked(False)

            self.ids_input.setPlaceholderText("Search:")
        else:
            self.ids_input.setPlaceholderText("IDs (e.g., 302294 or #317039)")

    def artist_checkbox_state_changed(self, state):
        self.ids_input.clear()

        if state == 2:
            if self.search_checkbox.isChecked():
                self.search_checkbox.setChecked(False)
                
            self.ids_input.setPlaceholderText("Artist:")
        else:
            self.ids_input.setPlaceholderText("IDs (e.g., 302294 or #317039)")

    def file_checkbox_state_changed(self, state):
        if state == 2:
            self.file_button.setEnabled(True)
        else:
            self.file_button.setEnabled(False)

    def use_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select .txt File", "", "Text Files (*.txt);;All Files (*)")

        if file_name:
            self.file_button.setText(f"\"{file_name}\"")
            self.file_name = file_name
        else:
            self.file_button.setText("Select File")
            self.file_name = None

    def clean_language(self):
        # TODO this is currently none functional in the nhentai package
        confirm = QMessageBox.question(self, "Confirmation", "Are you sure you want to do this?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                       QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            self.run_specific_command(" --clean-language")
        else:
            print("User canceled.")
            return
        
    def clean_download_history(self):
        confirm = QMessageBox.question(self, "Confirmation", 
                                       "Are you sure you want to do this?\nThis cannot be undone: Delete All Download History",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                       QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            self.run_specific_command(" --clean-download-history")
        else:
            print("User canceled.")
            return
    
    def resource_path(self, relative_path):
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())