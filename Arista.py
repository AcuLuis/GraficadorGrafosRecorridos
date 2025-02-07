from PyQt5.QtWidgets import QDialog,QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtGui import QIntValidator
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
        self.edit1.setValidator(QIntValidator())
        layout.addWidget(label1)
        layout.addWidget(self.edit1)
        label2 = QLabel('Nodo Hijo:')
        self.edit2 = QLineEdit(self)
        self.edit2.setValidator(QIntValidator())
        layout.addWidget(label2)
        layout.addWidget(self.edit2)
        label3 = QLabel('Peso:')
        self.edit3 = QLineEdit(self)
        self.edit3.setValidator(QIntValidator())
        layout.addWidget(label3)
        layout.addWidget(self.edit3)
        btnAceptar = QPushButton('Aceptar', self)
        btnAceptar.clicked.connect(self.aceptar_valores)
        layout.addWidget(btnAceptar)
    def aceptar_valores(self):
        valor1 = self.edit1.text()
        valor2 = self.edit2.text()
        valor3=self.edit3.text()
        self.valor1 = valor1
        self.valor2 = valor2
        self.valor3= valor3
        if self.valor1 != '' and self.valor2 != '' and self.valor3 != '':
            self.accept()
        else:
            alerta = QMessageBox()
            alerta.setIcon(QMessageBox.Warning)
            alerta.setText("Error")
            alerta.setInformativeText("Ingrese los datos correctos.")
            alerta.setWindowTitle("Alerta")
            alerta.exec_()
