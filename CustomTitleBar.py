from functools import partial
import os

from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QLabel,
    QPushButton, QWidget, QMenu,QHBoxLayout, 
    QSpacerItem, QSizePolicy, QMenuBar
)
from PyQt6.QtGui import QAction, QMouseEvent, QPixmap
from PyQt6.QtCore import Qt, QSize

class CustomTitleBar(QWidget):
    def __init__(self, main_window, settings):
        super().__init__()
        self.parent = main_window
        self.main_window = main_window
        self.settings = settings

        self.layout = QVBoxLayout()  # Use QHBoxLayout for horizontal layout

        self.title_layout = QHBoxLayout()

        # Title label with style
        if isinstance(self.parent, QMainWindow):
            self.title_label = QLabel('<span style="color: #ed2553;">n</span>Hentai GUI')
        else:
            self.title_label = QLabel('Cookies 🍪')

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

            # Add action for add preset
            set_add_preset = QAction("Add Preset", self)
            set_add_preset.triggered.connect(self.add_preset)
            options_menu.addAction(set_add_preset)

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
            self.preset_menu = menubar.addMenu("Presets")

            # Get preset names from settings
            self.populate_prest_menu()

            self.menuLayout = QHBoxLayout()
            self.menuLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.menuLayout.addWidget(menubar)

            self.layout.addLayout(self.menuLayout)
    
        self.setLayout(self.layout)

    def add_preset(self):
        self.main_window.add_preset()
        self.populate_prest_menu()

    def load_preset(self, preset_name):
        self.main_window.load_preset(preset_name)

    def populate_prest_menu(self):
        self.preset_menu.clear()

        preset_names = self.settings.childGroups()
        sorted_preset_names = sorted(preset_names, key=lambda x: x.lower())

        for preset_name in sorted_preset_names:
            cleaned_preset_name = preset_name.replace("Preset_", "").replace("-", " ")
            preset_menu_item = QAction(cleaned_preset_name, self)
            preset_menu_item.triggered.connect(partial(self.load_preset, cleaned_preset_name))
            self.preset_menu.addAction(preset_menu_item)

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