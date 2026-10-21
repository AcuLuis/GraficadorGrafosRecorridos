from PyQt6.QtWidgets import QDialog,QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtGui import QIntValidator
class MiDialogo(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.valor1 = None
        self.valor2 = None
        self.valor3=None
        self.setWindowTitle('Ingresar Valores')
        layout = QHBoxLayout(self)
        label1 = QLabel('Nodo Padre:')
        self.edit1 = QLineEdit(self)
        self.edit1.setValidator(QIntValidator(1, 999999))
        layout.addWidget(label1)
        layout.addWidget(self.edit1)
        label2 = QLabel('Nodo Hijo:')
        self.edit2 = QLineEdit(self)
        self.edit2.setValidator(QIntValidator(1, 999999))
        layout.addWidget(label2)
        layout.addWidget(self.edit2)
        label3 = QLabel('Peso:')
        self.edit3 = QLineEdit(self)
        self.edit3.setValidator(QIntValidator(0, 999999))
        layout.addWidget(label3)
        layout.addWidget(self.edit3)
        btnAceptar = QPushButton('Aceptar', self)
        btnAceptar.clicked.connect(self.aceptar_valores)
        layout.addWidget(btnAceptar)
    def aceptar_valores(self):
        campos = (self.edit1, self.edit2, self.edit3)
        if all(campo.hasAcceptableInput() for campo in campos):
            self.valor1, self.valor2, self.valor3 = (int(campo.text()) for campo in campos)
            self.accept()
        else:
            alerta = QMessageBox()
            alerta.setIcon(QMessageBox.Icon.Warning)
            alerta.setText("Error")
            alerta.setInformativeText("Los nodos deben ser enteros positivos y el peso un entero mayor o igual a 0.")
            alerta.setWindowTitle("Alerta")
            alerta.exec()
