from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget

from ui.estilos import CLAVES_DE_ARISTA, COLORES
from ui.tema import TEMAS, color_en_tema


class Leyenda(QWidget):
    """Muestras de color con su significado para el algoritmo mostrado."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout_entradas = QHBoxLayout(self)
        self.layout_entradas.setContentsMargins(0, 0, 0, 0)
        self.tema = TEMAS["claro"]
        self.entradas = []
        self._mostradas = []

    def mostrar(self, entradas):
        """``entradas`` es una lista de ``(clave de color, texto)``."""
        self.limpiar()
        for clave, texto in entradas:
            muestra = QLabel()
            color = color_en_tema(self.tema, COLORES[clave])
            if clave in CLAVES_DE_ARISTA:
                muestra.setFixedSize(18, 4)
                muestra.setStyleSheet(f"background: {color};")
            else:
                muestra.setFixedSize(12, 12)
                muestra.setStyleSheet(f"background: {color}; border-radius: 6px;")
            self.layout_entradas.addWidget(muestra)
            self.layout_entradas.addWidget(QLabel(texto))
            self.layout_entradas.addSpacing(10)
        self.layout_entradas.addStretch()
        self._mostradas = list(entradas)
        self.entradas = [texto for _, texto in entradas]

    def cambiar_tema(self, tema):
        self.tema = tema
        if self._mostradas:
            self.mostrar(self._mostradas)

    def limpiar(self):
        while self.layout_entradas.count():
            widget = self.layout_entradas.takeAt(0).widget()
            if widget is not None:
                widget.setParent(None)  # se quita ya: deleteLater lo dejaría visible hasta el próximo ciclo de eventos
                widget.deleteLater()
        self.entradas = []
        self._mostradas = []
