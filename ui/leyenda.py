from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget

from ui.estilos import CLAVES_DE_ARISTA, COLORES


class Leyenda(QWidget):
    """Muestras de color con su significado para el algoritmo mostrado."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout_entradas = QHBoxLayout(self)
        self.layout_entradas.setContentsMargins(0, 0, 0, 0)
        self.entradas = []

    def mostrar(self, entradas):
        """``entradas`` es una lista de ``(clave de color, texto)``."""
        self.limpiar()
        for clave, texto in entradas:
            muestra = QLabel()
            if clave in CLAVES_DE_ARISTA:
                muestra.setFixedSize(18, 4)
                muestra.setStyleSheet(f"background: {COLORES[clave]};")
            else:
                muestra.setFixedSize(12, 12)
                muestra.setStyleSheet(f"background: {COLORES[clave]}; border-radius: 6px;")
            self.layout_entradas.addWidget(muestra)
            self.layout_entradas.addWidget(QLabel(texto))
            self.layout_entradas.addSpacing(10)
        self.layout_entradas.addStretch()
        self.entradas = [texto for _, texto in entradas]

    def limpiar(self):
        while self.layout_entradas.count():
            widget = self.layout_entradas.takeAt(0).widget()
            if widget is not None:
                widget.setParent(None)  # se quita ya: deleteLater lo dejaría visible hasta el próximo ciclo de eventos
                widget.deleteLater()
        self.entradas = []
