from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QAbstractItemView, QHeaderView, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout,
                             QWidget)

from algoritmos.comun import formatear_distancia

TITULO_VACIO = "Sin resultados"
RESUMEN_VACIO = "Ejecuta un algoritmo desde el menú Algoritmos para ver sus pasos."


class PanelInformacion(QWidget):
    """Panel lateral con el resultado del último algoritmo: resumen, tabla de pasos y,
    en Dijkstra, la tabla de distancias del paso mostrado.

    Emite ``paso_elegido(indice)`` cuando el usuario elige una fila de la tabla de pasos.
    """

    paso_elegido = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titulo = ""
        self.resumen = ""
        self.descripciones = []

        self.lbl_titulo = QLabel()
        fuente = QFont()
        fuente.setPointSize(11)
        fuente.setBold(True)
        self.lbl_titulo.setFont(fuente)
        self.lbl_titulo.setWordWrap(True)
        self.lbl_resumen = QLabel()
        self.lbl_resumen.setWordWrap(True)

        self.tabla_pasos = _tabla(["#", "Paso"], columna_elastica=1)
        self.tabla_pasos.setWordWrap(True)
        self.tabla_pasos.itemSelectionChanged.connect(self._al_elegir_fila)

        self.lbl_distancias = QLabel("Distancias en este paso")
        self.tabla_distancias = _tabla(["Nodo", "Distancia", "Anterior"], columna_elastica=1)

        layout = QVBoxLayout(self)
        layout.addWidget(self.lbl_titulo)
        layout.addWidget(self.lbl_resumen)
        layout.addWidget(self.tabla_pasos, 2)
        layout.addWidget(self.lbl_distancias)
        layout.addWidget(self.tabla_distancias, 1)
        self.limpiar()

    def mostrar_resultado(self, titulo, resumen, descripciones, con_distancias=False):
        self.titulo, self.resumen, self.descripciones = titulo, resumen, list(descripciones)
        self.lbl_titulo.setText(titulo)
        self.lbl_resumen.setText(resumen)
        self.tabla_pasos.blockSignals(True)
        self.tabla_pasos.setRowCount(len(self.descripciones))
        for fila, descripcion in enumerate(self.descripciones):
            self.tabla_pasos.setItem(fila, 0, QTableWidgetItem(str(fila + 1)))
            self.tabla_pasos.setItem(fila, 1, QTableWidgetItem(descripcion))
        self.tabla_pasos.resizeRowsToContents()
        self.tabla_pasos.blockSignals(False)
        self.lbl_distancias.setVisible(con_distancias)
        self.tabla_distancias.setVisible(con_distancias)

    def seleccionar_paso(self, indice, paso):
        self.tabla_pasos.blockSignals(True)
        self.tabla_pasos.selectRow(indice)
        self.tabla_pasos.blockSignals(False)
        item = self.tabla_pasos.item(indice, 0)
        if item is not None:
            self.tabla_pasos.scrollToItem(item)
        if paso.distancias is not None:
            self._mostrar_distancias(paso)

    def _mostrar_distancias(self, paso):
        nodos = sorted(paso.distancias, key=str)
        self.tabla_distancias.setRowCount(len(nodos))
        for fila, nodo in enumerate(nodos):
            anterior = paso.anteriores.get(nodo)
            valores = [nodo, formatear_distancia(paso.distancias[nodo]), "—" if anterior is None else anterior]
            for columna, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor))
                if nodo in paso.visitados:
                    fuente = item.font()
                    fuente.setBold(True)
                    item.setFont(fuente)
                self.tabla_distancias.setItem(fila, columna, item)
        self.tabla_distancias.resizeRowsToContents()

    def _al_elegir_fila(self):
        filas = self.tabla_pasos.selectionModel().selectedRows()
        if filas:
            self.paso_elegido.emit(filas[0].row())

    def limpiar(self):
        self.titulo, self.resumen, self.descripciones = "", "", []
        self.lbl_titulo.setText(TITULO_VACIO)
        self.lbl_resumen.setText(RESUMEN_VACIO)
        self.tabla_pasos.setRowCount(0)
        self.tabla_distancias.setRowCount(0)
        self.lbl_distancias.setVisible(False)
        self.tabla_distancias.setVisible(False)

    def texto(self):
        """El resultado como texto plano: título, resumen y pasos numerados."""
        if not self.descripciones:
            return ""
        pasos = [f"{numero}. {descripcion}" for numero, descripcion in enumerate(self.descripciones, 1)]
        return "\n".join([self.titulo, self.resumen, "", *pasos]) + "\n"


def _tabla(encabezados, columna_elastica):
    tabla = QTableWidget(0, len(encabezados))
    tabla.setHorizontalHeaderLabels(encabezados)
    tabla.verticalHeader().setVisible(False)
    tabla.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    tabla.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    tabla.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    encabezado = tabla.horizontalHeader()
    for columna in range(len(encabezados)):
        modo = QHeaderView.ResizeMode.Stretch if columna == columna_elastica else QHeaderView.ResizeMode.ResizeToContents
        encabezado.setSectionResizeMode(columna, modo)
    return tabla
