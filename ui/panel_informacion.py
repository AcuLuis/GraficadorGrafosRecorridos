import csv
from pathlib import Path

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QAbstractItemView, QFileDialog, QHeaderView, QLabel, QMessageBox, QPushButton,
                             QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

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
        self.pasos = []

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
        self.btn_exportar = QPushButton("Exportar pasos…")
        self.btn_exportar.setToolTip("Guardar los pasos como CSV o como texto.")
        self.btn_exportar.clicked.connect(self.exportar)

        layout = QVBoxLayout(self)
        layout.addWidget(self.lbl_titulo)
        layout.addWidget(self.lbl_resumen)
        layout.addWidget(self.tabla_pasos, 2)
        layout.addWidget(self.lbl_distancias)
        layout.addWidget(self.tabla_distancias, 1)
        layout.addWidget(self.btn_exportar)
        self.limpiar()

    @property
    def resumen(self):
        return self.pasos[-1].descripcion if self.pasos else ""

    @property
    def con_distancias(self):
        return bool(self.pasos) and self.pasos[-1].distancias is not None

    def mostrar_resultado(self, titulo, pasos):
        self.titulo, self.pasos = titulo, list(pasos)
        self.lbl_titulo.setText(titulo)
        self.lbl_resumen.setText(self.resumen)
        self.tabla_pasos.blockSignals(True)
        self.tabla_pasos.setRowCount(len(self.pasos))
        for fila, paso in enumerate(self.pasos):
            self.tabla_pasos.setItem(fila, 0, QTableWidgetItem(str(fila + 1)))
            self.tabla_pasos.setItem(fila, 1, QTableWidgetItem(paso.descripcion))
        self.tabla_pasos.resizeRowsToContents()
        self.tabla_pasos.blockSignals(False)
        self.lbl_distancias.setVisible(self.con_distancias)
        self.tabla_distancias.setVisible(self.con_distancias)
        self.btn_exportar.setEnabled(True)

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
        filas = _filas_de_distancias(paso)
        self.tabla_distancias.setRowCount(len(filas))
        for fila, valores in enumerate(filas):
            nodo = valores[0]
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
        self.titulo, self.pasos = "", []
        self.lbl_titulo.setText(TITULO_VACIO)
        self.lbl_resumen.setText(RESUMEN_VACIO)
        self.tabla_pasos.setRowCount(0)
        self.tabla_distancias.setRowCount(0)
        self.lbl_distancias.setVisible(False)
        self.tabla_distancias.setVisible(False)
        self.btn_exportar.setEnabled(False)

    # Exportación

    def texto(self):
        """El resultado como texto plano: título, resumen, pasos numerados y, si hay, distancias finales."""
        if not self.pasos:
            return ""
        lineas = [self.titulo, self.resumen, ""]
        lineas += [f"{numero}. {paso.descripcion}" for numero, paso in enumerate(self.pasos, 1)]
        if self.con_distancias:
            lineas += ["", "Distancias finales:"]
            lineas += [f"Nodo {nodo}: {distancia} (anterior: {anterior})"
                       for nodo, distancia, anterior in _filas_de_distancias(self.pasos[-1])]
        return "\n".join(lineas) + "\n"

    def exportar(self):
        if not self.pasos:
            return
        ruta, _ = QFileDialog.getSaveFileName(self, "Exportar pasos", "", "CSV (*.csv);;Texto (*.txt)")
        if not ruta:
            return
        try:
            self.guardar(ruta)
        except OSError as error:
            QMessageBox.critical(self, "Error", f"No se pudieron exportar los pasos:\n{error}")

    def guardar(self, ruta):
        """Guarda los pasos como CSV (si la ruta termina en .csv) o como texto."""
        if Path(ruta).suffix.lower() != ".csv":
            Path(ruta).write_text(self.texto(), encoding="utf-8")
            return
        # utf-8-sig para que Excel reconozca los acentos.
        with open(ruta, "w", newline="", encoding="utf-8-sig") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(["Paso", "Descripción"])
            escritor.writerows((numero, paso.descripcion) for numero, paso in enumerate(self.pasos, 1))
            if self.con_distancias:
                escritor.writerow([])
                escritor.writerow(["Nodo", "Distancia", "Anterior"])
                escritor.writerows(_filas_de_distancias(self.pasos[-1]))


def _filas_de_distancias(paso):
    """``(nodo, distancia, anterior)`` de cada nodo, con ∞ y — para los que aún no se alcanzan."""
    filas = []
    for nodo in sorted(paso.distancias, key=str):
        anterior = paso.anteriores.get(nodo)
        filas.append((nodo, formatear_distancia(paso.distancias[nodo]), "—" if anterior is None else anterior))
    return filas


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
