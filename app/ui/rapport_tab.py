from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from .rapport.skift_subtab import SkiftSubTab
from .rapport.lonn_subtab import LonnSubTab
from .rapport.terminal_subtab import TerminalSubTab

class RapportTab(QWidget):
    def __init__(self, settings_tab):
        super().__init__()
        layout = QVBoxLayout()
        tabs = QTabWidget()
        tabs.addTab(SkiftSubTab(settings_tab), "Skift")
        tabs.addTab(LonnSubTab(settings_tab), "Lønn")
        tabs.addTab(TerminalSubTab(), "Terminal")
        layout.addWidget(tabs)
        self.setLayout(layout)