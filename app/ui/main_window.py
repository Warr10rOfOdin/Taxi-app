from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QStackedWidget, QFrame, QListWidget, QListWidgetItem, QTreeWidget, QTreeWidgetItem
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QRect, QEasingCurve

from .home_tab import HomeTab
from .rapport_tab import RapportTab
from .vaktliste_tab import VaktlisteTab
from .settings_tab import SettingsTab
from .themes import sith_dark_stylesheet

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Voss Taxi Report Maker")
        self.setMinimumSize(1200, 700)
        self.setStyleSheet("QMainWindow { background: white; }")

        # --- Make SettingsTab first ---
        self.settings_tab = SettingsTab()

        # Central widget & layout
        central_widget = QWidget()
        central_layout = QHBoxLayout(central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar (hidden when using hamburger menu)
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(180)
        self.sidebar.setStyleSheet("background:#183872;color:white;font-size:18px;")
        self.sidebar.addItem(QListWidgetItem(QIcon(), "🏠  Home"))
        self.sidebar.addItem(QListWidgetItem(QIcon(), "📄  Rapport"))
        self.sidebar.addItem(QListWidgetItem(QIcon(), "📅  Vaktliste"))
        self.sidebar.addItem(QListWidgetItem(QIcon(), "⚙️  Settings"))
        self.sidebar.setCurrentRow(0)
        self.sidebar.hide()

        # Topbar
        topbar = QHBoxLayout()
        # Hamburger button (open)
        self.hamburger_btn = QPushButton("≡")
        self.hamburger_btn.setFixedSize(40, 40)
        self.hamburger_btn.setStyleSheet("font-size:28px;background:transparent;color:#FFD600;")
        self.hamburger_btn.clicked.connect(self.toggle_drawer)

        logo = QLabel("🚖 VOSS TAXI")
        logo.setStyleSheet("font-size:28px;font-weight:bold;padding:8px;color:#FFD600;")
        topbar.addWidget(self.hamburger_btn)
        topbar.addWidget(logo)
        topbar.addStretch()
        # Language and dark mode switchers
        lang_btn = QPushButton("EN")
        self.dark_btn = QPushButton("🌙")
        self.dark_btn.setCheckable(True)
        self.dark_btn.clicked.connect(self.toggle_dark_mode)
        topbar.addWidget(lang_btn)
        topbar.addWidget(self.dark_btn)

        topbar_widget = QWidget()
        topbar_widget.setLayout(topbar)
        topbar_widget.setFixedHeight(60)
        topbar_widget.setStyleSheet("background:#1A237E;")

        # Main pages
        self.pages = QStackedWidget()
        self.home_tab = HomeTab()
        self.rapport_tab = RapportTab(self.settings_tab)  # <--- Pass settings_tab here!
        self.vaktliste_tab = VaktlisteTab()
        # self.settings_tab already exists
        self.pages.addWidget(self.home_tab)
        self.pages.addWidget(self.rapport_tab)
        self.pages.addWidget(self.vaktliste_tab)
        self.pages.addWidget(self.settings_tab)

        # Connect settings tab signal for dark mode
        self.settings_tab.dark_mode_toggled.connect(self.set_dark_mode_from_settings)

        # Layout assembly
        right = QVBoxLayout()
        right.addWidget(topbar_widget)
        right.addWidget(self.pages)

        # Drawer overlay
        self.drawer_overlay = QWidget(central_widget)
        self.drawer_overlay.setStyleSheet("background:rgba(0,0,0,0.2);")
        self.drawer_overlay.hide()
        self.drawer_overlay.setGeometry(0, 0, self.width(), self.height())
        self.drawer_overlay.mousePressEvent = self.hide_drawer

        # Drawer (slide menu)
        self.drawer = QFrame(central_widget)
        self.drawer.setFixedWidth(300)
        self.drawer.setGeometry(-300, 0, 300, self.height())
        self.drawer.setStyleSheet("background:#183872;color:white;")
        drawer_layout = QVBoxLayout(self.drawer)
        drawer_layout.setContentsMargins(0, 0, 0, 0)
        drawer_layout.setSpacing(0)

        # Drawer top bar with hamburger for closing
        drawer_topbar = QHBoxLayout()
        drawer_hamburger_btn = QPushButton("≡")
        drawer_hamburger_btn.setFixedSize(40, 40)
        drawer_hamburger_btn.setStyleSheet("font-size:28px;background:transparent;color:#FFD600;")
        drawer_hamburger_btn.clicked.connect(self.toggle_drawer)
        drawer_logo = QLabel("VOSS TAXI")
        drawer_logo.setStyleSheet("font-size:22px;font-weight:bold;padding:8px;color:#FFD600;")
        drawer_topbar.addWidget(drawer_hamburger_btn)
        drawer_topbar.addWidget(drawer_logo)
        drawer_topbar.addStretch()

        drawer_topbar_widget = QWidget()
        drawer_topbar_widget.setLayout(drawer_topbar)
        drawer_topbar_widget.setFixedHeight(48)
        drawer_topbar_widget.setStyleSheet("background: #1A237E;")

        drawer_layout.addWidget(drawer_topbar_widget)

        # Drawer tree menu
        self.drawer_tree = QTreeWidget()
        self.drawer_tree.setHeaderHidden(True)
        self.drawer_tree.setStyleSheet("background:transparent;font-size:18px;color:white; padding-left:10px;")

        # Home
        home_item = QTreeWidgetItem(["🏠 Home"])
        rapport_item = QTreeWidgetItem(["📄 Rapport"])
        rapport_item.addChild(QTreeWidgetItem(["Skift"]))
        rapport_item.addChild(QTreeWidgetItem(["Lønn"]))
        rapport_item.addChild(QTreeWidgetItem(["Terminal"]))
        vaktliste_item = QTreeWidgetItem(["📅 Vaktliste"])
        vaktliste_item.addChild(QTreeWidgetItem(["Vaktliste Bil"]))
        vaktliste_item.addChild(QTreeWidgetItem(["Vaktliste Sjåfør"]))
        settings_item = QTreeWidgetItem(["⚙️ Settings"])

        self.drawer_tree.addTopLevelItem(home_item)
        self.drawer_tree.addTopLevelItem(rapport_item)
        self.drawer_tree.addTopLevelItem(vaktliste_item)
        self.drawer_tree.addTopLevelItem(settings_item)
        self.drawer_tree.collapseItem(rapport_item)
        self.drawer_tree.collapseItem(vaktliste_item)

        self.drawer_tree.itemClicked.connect(self.drawer_navigate)

        drawer_layout.addWidget(self.drawer_tree)
        drawer_layout.addStretch()

        central_layout.addLayout(right)

        self.setCentralWidget(central_widget)

        # Animation for drawer
        self.drawer_anim = QPropertyAnimation(self.drawer, b"geometry")
        self.drawer_anim.setDuration(200)
        self.drawer_anim.setEasingCurve(QEasingCurve.OutCubic)

        self.resizeEvent = self.on_resize

    # ... rest of your methods unchanged ...
    def toggle_drawer(self):
        if self.drawer.x() < 0:
            self.drawer_overlay.setGeometry(0, 0, self.width(), self.height())
            self.drawer_overlay.show()
            self.drawer.raise_()
            self.drawer_anim.stop()
            self.drawer_anim.setStartValue(QRect(-300, 0, 300, self.height()))
            self.drawer_anim.setEndValue(QRect(0, 0, 300, self.height()))
            self.drawer_anim.start()
        else:
            self.drawer_anim.stop()
            self.drawer_anim.setStartValue(QRect(0, 0, 300, self.height()))
            self.drawer_anim.setEndValue(QRect(-300, 0, 300, self.height()))
            self.drawer_anim.start()
            self.drawer_overlay.hide()

    def hide_drawer(self, event=None):
        if self.drawer.x() >= 0:
            self.drawer_anim.stop()
            self.drawer_anim.setStartValue(QRect(0, 0, 300, self.height()))
            self.drawer_anim.setEndValue(QRect(-300, 0, 300, self.height()))
            self.drawer_anim.start()
            self.drawer_overlay.hide()

    def drawer_navigate(self, item, _):
        txt = item.text(0)
        parent = item.parent()
        if parent:
            ptxt = parent.text(0)
            if ptxt.startswith("📄"):
                if txt == "Skift":
                    self.sidebar.setCurrentRow(1)
                    self.pages.setCurrentIndex(1)
                    self.pages.currentWidget().children()[1].setCurrentIndex(0)
                elif txt == "Lønn":
                    self.sidebar.setCurrentRow(1)
                    self.pages.setCurrentIndex(1)
                    self.pages.currentWidget().children()[1].setCurrentIndex(1)
                elif txt == "Terminal":
                    self.sidebar.setCurrentRow(1)
                    self.pages.setCurrentIndex(1)
                    self.pages.currentWidget().children()[1].setCurrentIndex(2)
            elif ptxt.startswith("📅"):
                if txt == "Vaktliste Bil":
                    self.sidebar.setCurrentRow(2)
                    self.pages.setCurrentIndex(2)
                    self.pages.currentWidget().children()[1].setCurrentIndex(0)
                elif txt == "Vaktliste Sjåfør":
                    self.sidebar.setCurrentRow(2)
                    self.pages.setCurrentIndex(2)
                    self.pages.currentWidget().children()[1].setCurrentIndex(1)
        else:
            if txt.startswith("🏠"):
                self.sidebar.setCurrentRow(0)
                self.pages.setCurrentIndex(0)
            elif txt.startswith("📄"):
                self.sidebar.setCurrentRow(1)
                self.pages.setCurrentIndex(1)
            elif txt.startswith("📅"):
                self.sidebar.setCurrentRow(2)
                self.pages.setCurrentIndex(2)
            elif txt.startswith("⚙️"):
                self.sidebar.setCurrentRow(3)
                self.pages.setCurrentIndex(3)
        self.hide_drawer()

    def on_resize(self, event):
        self.drawer.setFixedHeight(self.height())
        self.drawer_overlay.setGeometry(0, 0, self.width(), self.height())
        if self.drawer.x() >= 0:
            self.drawer.setGeometry(0, 0, 300, self.height())
        else:
            self.drawer.setGeometry(-300, 0, 300, self.height())
        QWidget.resizeEvent(self, event)

    def toggle_dark_mode(self):
        is_dark = self.dark_btn.isChecked()
        self.apply_dark_mode(is_dark)
        # Sync settings checkbox if toggled from topbar
        self.settings_tab.dark_checkbox.setChecked(is_dark)

    def set_dark_mode_from_settings(self, checked):
        self.apply_dark_mode(checked)
        self.dark_btn.setChecked(checked)
        self.dark_btn.setText("☀️" if checked else "🌙")

    def apply_dark_mode(self, enabled):
        if enabled:
            self.setStyleSheet(sith_dark_stylesheet())
            self.dark_btn.setText("☀️")
        else:
            self.setStyleSheet("")
            self.dark_btn.setText("🌙")
