from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QScrollArea


class PanelInformacion(QScrollArea):
    """Panel lateral con los pasos del último algoritmo ejecutado."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.etiqueta = QLabel()
        fuente = QFont()
        fuente.setPointSize(12)
        self.etiqueta.setFont(fuente)
        self.etiqueta.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.etiqueta.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.setWidget(self.etiqueta)

    def mostrar(self, texto):
        self.etiqueta.setText(texto)

    def limpiar(self):
        self.etiqueta.clear()

    def texto(self):
        return self.etiqueta.text()
