from PyQt6.QtWidgets import QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtGui import QIntValidator
class MiDialogoNodoEliminar(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.valor1 = None
        self.setWindowTitle('Eliminar Nodo')
        layout = QHBoxLayout(self)
        label1 = QLabel('Ingresa ID del Nodo:')
        self.edit1 = QLineEdit(self)
        self.edit1.setValidator(QIntValidator(1, 999999))
        layout.addWidget(label1)
        layout.addWidget(self.edit1)
        btnAceptar = QPushButton('Aceptar', self)
        btnAceptar.clicked.connect(self.aceptar_valores)
        layout.addWidget(btnAceptar)
    def aceptar_valores(self):
        if self.edit1.hasAcceptableInput():
            self.valor1 = int(self.edit1.text())
            self.accept()
        else:
            alerta = QMessageBox()
            alerta.setIcon(QMessageBox.Icon.Warning)
            alerta.setText("Error")
            alerta.setInformativeText("Ingrese un ID de nodo válido (entero positivo).")
            alerta.setWindowTitle("Alerta")
            alerta.exec()
class InicioNodo(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.valor1 = None
        self.setWindowTitle('InicioNodo')
        layout = QHBoxLayout(self)
        label1 = QLabel('Ingresa ID del Nodo:')
        self.edit1 = QLineEdit(self)
        self.edit1.setValidator(QIntValidator(1, 999999))
        layout.addWidget(label1)
        layout.addWidget(self.edit1)
        btnAceptar = QPushButton('Aceptar', self)
        btnAceptar.clicked.connect(self.aceptar_valores)
        layout.addWidget(btnAceptar)
    def aceptar_valores(self):
        if self.edit1.hasAcceptableInput():
            self.valor1 = int(self.edit1.text())
            self.accept()
        else:
            alerta = QMessageBox()
            alerta.setIcon(QMessageBox.Icon.Warning)
            alerta.setText("Error")
            alerta.setInformativeText("Ingrese un ID de nodo válido (entero positivo).")
            alerta.setWindowTitle("Alerta")
            alerta.exec()