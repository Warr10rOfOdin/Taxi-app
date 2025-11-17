
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from .vaktliste.bil_subtab import BilSubTab
from .vaktliste.sjafor_subtab import SjaforSubTab

class VaktlisteTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        tabs = QTabWidget()
        tabs.addTab(BilSubTab(), "Vaktliste Bil")
        tabs.addTab(SjaforSubTab(), "Vaktliste Sjåfør")
        layout.addWidget(tabs)
        self.setLayout(layout)
