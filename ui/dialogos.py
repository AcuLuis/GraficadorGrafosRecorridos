from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import QDialog, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton

VALOR_MAXIMO = 999999


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
            [("Nodo Padre:", 1), ("Nodo Hijo:", 1), ("Peso:", 0)],
            "Los nodos deben ser enteros positivos y el peso un entero mayor o igual a 0.",
            parent,
        )


class DialogoNodo(DialogoEnteros):
    def __init__(self, titulo, parent=None):
        super().__init__(
            titulo,
            [("Ingresa ID del Nodo:", 1)],
            "Ingrese un ID de nodo válido (entero positivo).",
            parent,
        )


def pedir_arista(parent=None):
    """Devuelve ``(origen, destino, peso)`` o ``None`` si se cancela."""
    dialogo = DialogoArista(parent)
    if dialogo.exec() == QDialog.DialogCode.Accepted:
        return tuple(dialogo.valores)
    return None


def pedir_nodo(titulo, parent=None):
    """Devuelve el ID de nodo ingresado o ``None`` si se cancela."""
    dialogo = DialogoNodo(titulo, parent)
    if dialogo.exec() == QDialog.DialogCode.Accepted:
        return dialogo.valores[0]
    return None
