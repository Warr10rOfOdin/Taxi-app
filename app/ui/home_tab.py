
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class HomeTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("<h2>Velkommen til Voss Taxi Report Maker!</h2>"))
        layout.addWidget(QLabel("Bruk menyen for å navigere mellom rapportering og vaktlister."))
        self.setLayout(layout)
