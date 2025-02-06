from PyQt5.QtWidgets import QDialog,QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtGui import QIntValidator
class dialogoNodoInicio(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.valor1 = None
        self.setWindowTitle('Comenzando desde el nodo...')
        layout = QHBoxLayout(self)
        label1 = QLabel('Ingresa ID del Nodo:')
        self.edit1 = QLineEdit(self)
        self.edit1.setValidator(QIntValidator())
        layout.addWidget(label1)
        layout.addWidget(self.edit1)
        btnAceptar = QPushButton('Aceptar', self)
        btnAceptar.clicked.connect(self.aceptar_valores)
        layout.addWidget(btnAceptar)
    def aceptar_valores(self):
        valor1 = self.edit1.text()
        self.valor1 = valor1
        if self.valor1 != '':
            self.accept()
        else:
            alerta = QMessageBox()
            alerta.setIcon(QMessageBox.Warning)
            alerta.setText("Error")
            alerta.setInformativeText("Ingrese los datos correctos.")
            alerta.setWindowTitle("Alerta")
            alerta.exec_()