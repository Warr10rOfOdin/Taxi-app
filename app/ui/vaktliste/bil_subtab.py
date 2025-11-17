
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
class BilSubTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Vaktliste Bil kommer her..."))
        self.setLayout(layout)
