from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import (QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QHBoxLayout, QInputDialog,
                             QLabel, QLineEdit, QMessageBox, QPushButton, QSpinBox)

from modelo.generacion import MAXIMO_NODOS, maximo_de_aristas

VALOR_MAXIMO = 999999
TODOS_LOS_NODOS = "Todos los nodos"


class DialogoEnteros(QDialog):
    """Diálogo de una fila con campos enteros validados y un botón Aceptar.

    ``campos`` es una lista de ``(etiqueta, valor_minimo)``. Al aceptar, ``valores``
    contiene los enteros ingresados en el mismo orden.
    """

    def __init__(self, titulo, campos, mensaje_error, parent=None):
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.mensaje_error = mensaje_error
        self.valores = None
        self.editores = []
        layout = QHBoxLayout(self)
        for etiqueta, minimo in campos:
            editor = QLineEdit(self)
            editor.setValidator(QIntValidator(minimo, VALOR_MAXIMO, editor))
            layout.addWidget(QLabel(etiqueta))
            layout.addWidget(editor)
            self.editores.append(editor)
        btn_aceptar = QPushButton("Aceptar", self)
        btn_aceptar.setDefault(True)
        btn_aceptar.clicked.connect(self.aceptar_valores)
        layout.addWidget(btn_aceptar)

    def aceptar_valores(self):
        if all(editor.hasAcceptableInput() for editor in self.editores):
            self.valores = [int(editor.text()) for editor in self.editores]
            self.accept()
        else:
            QMessageBox.warning(self, "Alerta", self.mensaje_error)


class DialogoArista(DialogoEnteros):
    def __init__(self, parent=None):
        super().__init__(
            "Ingresar Arista",
            [("Nodo Padre:", 1), ("Nodo Hijo:", 1), ("Peso:", -VALOR_MAXIMO)],
            "Los nodos deben ser enteros positivos y el peso un número entero.",
            parent,
        )


class DialogoInicioDestino(QDialog):
    """Elige el nodo inicial y, opcionalmente, un nodo destino."""

    def __init__(self, nodos, sugerido=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Camino más corto")
        self.nodos = list(nodos)
        opciones = [str(nodo) for nodo in self.nodos]
        self.cmb_inicio = QComboBox()
        self.cmb_inicio.addItems(opciones)
        if sugerido in self.nodos:
            self.cmb_inicio.setCurrentIndex(self.nodos.index(sugerido))
        self.cmb_destino = QComboBox()
        self.cmb_destino.addItems([TODOS_LOS_NODOS, *opciones])
        botones = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)
        formulario = QFormLayout(self)
        formulario.addRow("Nodo inicial:", self.cmb_inicio)
        formulario.addRow("Nodo destino:", self.cmb_destino)
        formulario.addRow(botones)

    def eleccion(self):
        """``(inicio, destino)``; ``destino`` es ``None`` si se eligió "Todos los nodos"."""
        inicio = self.nodos[self.cmb_inicio.currentIndex()]
        indice_destino = self.cmb_destino.currentIndex()
        return inicio, None if indice_destino == 0 else self.nodos[indice_destino - 1]


def pedir_inicio_y_destino(nodos, parent=None, sugerido=None):
    """Devuelve ``(inicio, destino)`` o ``None`` si se cancela."""
    dialogo = DialogoInicioDestino(nodos, sugerido, parent)
    if dialogo.exec() == QDialog.DialogCode.Accepted:
        return dialogo.eleccion()
    return None


class DialogoGrafoAleatorio(QDialog):
    """Opciones para generar un grafo aleatorio."""

    def __init__(self, dirigido=False, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Grafo aleatorio")
        self.spn_nodos = _numero(1, MAXIMO_NODOS, 8)
        self.spn_aristas = _numero(0, maximo_de_aristas(8, dirigido), 12)
        self.spn_peso_minimo = _numero(-VALOR_MAXIMO, VALOR_MAXIMO, 1)
        self.spn_peso_maximo = _numero(-VALOR_MAXIMO, VALOR_MAXIMO, 20)
        self.chk_dirigido = QCheckBox("Dirigido")
        self.chk_dirigido.setChecked(dirigido)
        self.chk_conexo = QCheckBox("Conexo (todos los nodos quedan unidos)")
        self.chk_conexo.setChecked(True)
        botones = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)
        formulario = QFormLayout(self)
        formulario.addRow("Nodos:", self.spn_nodos)
        formulario.addRow("Aristas:", self.spn_aristas)
        formulario.addRow("Peso mínimo:", self.spn_peso_minimo)
        formulario.addRow("Peso máximo:", self.spn_peso_maximo)
        formulario.addRow(self.chk_dirigido)
        formulario.addRow(self.chk_conexo)
        formulario.addRow(botones)
        self.spn_nodos.valueChanged.connect(self._ajustar_maximo_de_aristas)
        self.chk_dirigido.toggled.connect(self._ajustar_maximo_de_aristas)

    def _ajustar_maximo_de_aristas(self, *_):
        self.spn_aristas.setMaximum(maximo_de_aristas(self.spn_nodos.value(), self.chk_dirigido.isChecked()))

    def opciones(self):
        """Argumentos para ``ModeloGrafo.generar_aleatorio``."""
        return {
            "cantidad_nodos": self.spn_nodos.value(),
            "cantidad_aristas": self.spn_aristas.value(),
            "peso_minimo": self.spn_peso_minimo.value(),
            "peso_maximo": self.spn_peso_maximo.value(),
            "dirigido": self.chk_dirigido.isChecked(),
            "conexo": self.chk_conexo.isChecked(),
        }


def pedir_grafo_aleatorio(parent=None, dirigido=False):
    """Devuelve las opciones elegidas para el grafo aleatorio o ``None`` si se cancela."""
    dialogo = DialogoGrafoAleatorio(dirigido, parent)
    if dialogo.exec() == QDialog.DialogCode.Accepted:
        return dialogo.opciones()
    return None


def _numero(minimo, maximo, valor):
    campo = QSpinBox()
    campo.setRange(minimo, maximo)
    campo.setValue(valor)
    return campo


def pedir_arista(parent=None):
    """Devuelve ``(origen, destino, peso)`` o ``None`` si se cancela."""
    dialogo = DialogoArista(parent)
    if dialogo.exec() == QDialog.DialogCode.Accepted:
        return tuple(dialogo.valores)
    return None


def pedir_peso(parent, etiqueta, valor=1):
    """Devuelve el peso ingresado (un entero, que puede ser negativo) o ``None`` si se cancela."""
    peso, aceptado = QInputDialog.getInt(parent, "Peso de la arista", etiqueta, valor, -VALOR_MAXIMO, VALOR_MAXIMO)
    return peso if aceptado else None


def pedir_nodo(titulo, nodos, parent=None, sugerido=None):
    """Muestra una lista desplegable con ``nodos`` y devuelve el elegido, o ``None`` si se cancela."""
    nodos = list(nodos)
    opciones = [str(nodo) for nodo in nodos]
    indice = nodos.index(sugerido) if sugerido in nodos else 0
    texto, aceptado = QInputDialog.getItem(parent, titulo, "Nodo:", opciones, indice, False)
    return nodos[opciones.index(texto)] if aceptado else None
