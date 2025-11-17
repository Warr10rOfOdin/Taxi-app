
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
class SjaforSubTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Vaktliste Sjåfør kommer her..."))
        self.setLayout(layout)
