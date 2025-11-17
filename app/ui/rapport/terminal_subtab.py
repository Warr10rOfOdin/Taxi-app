
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
class TerminalSubTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Terminal rapport kommer her..."))
        self.setLayout(layout)
