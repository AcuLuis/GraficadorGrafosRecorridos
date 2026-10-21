import math
from pathlib import Path

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QFileDialog, QFrame, QGroupBox, QHBoxLayout, QLabel, QMessageBox,
                             QPushButton, QRadioButton, QVBoxLayout, QWidget)

import algoritmos
from ui.dialogos import pedir_arista, pedir_nodo
from ui.lienzo import Lienzo

CARPETA_DATOS = Path(__file__).resolve().parent.parent / "datos"
COLOR_RECORRIDO = "blue"
ANCHO_MINIMO = 800
ALTO_MINIMO = 600

BFS = "BFS - Búsqueda en anchura"
DFS = "DFS - Búsqueda en profundidad"
KRUSKAL = "Kruskal - Árbol de expansión mínima"
DIJKSTRA = "Dijkstra - Camino más corto"


def texto_pasos(titulo, aristas):
    return titulo + "\n" + "".join(f"Va de nodo {arista[0]} -> nodo {arista[1]}\n" for arista in aristas)


class PanelVista(QWidget):
    """Área principal: controles de edición, lienzo y ejecución de algoritmos sobre el modelo."""

    def __init__(self, modelo, panel_info, parent=None):
        super().__init__(parent)
        self.modelo = modelo
        self.panel_info = panel_info
        # (función, argumentos) del último algoritmo, para repetirlo si se elimina un nodo.
        self.ultimo_algoritmo = None
        self._construir_interfaz()

    def _construir_interfaz(self):
        grupo_algoritmo = QGroupBox("Algoritmo")
        self.lbl_algoritmo = QLabel("")
        fuente = QFont()
        fuente.setPointSize(16)
        fuente.setBold(True)
        self.lbl_algoritmo.setFont(fuente)
        layout_algoritmo = QHBoxLayout(grupo_algoritmo)
        layout_algoritmo.addWidget(QLabel("Nombre Algoritmo:"))
        layout_algoritmo.addWidget(self.lbl_algoritmo)
        layout_algoritmo.addStretch()

        self.grupo_tipo = QGroupBox("Selecciona el tipo de grafo")
        self.rb_no_dirigido = QRadioButton("Grafo No Dirigido")
        self.rb_dirigido = QRadioButton("Grafo Dirigido")
        self.rb_no_dirigido.setChecked(True)
        layout_tipo = QHBoxLayout(self.grupo_tipo)
        layout_tipo.addWidget(self.rb_no_dirigido)
        layout_tipo.addWidget(self.rb_dirigido)

        grupo_edicion = QGroupBox("Selecciona una opción")
        self.rb_dibujar_nodo = QRadioButton("Dibujar Nodo")
        self.rb_dibujar_arista = QRadioButton("Dibujar Arista")
        self.btn_ingresar_arista = QPushButton("Ingresar Puntos")
        self.btn_limpiar = QPushButton("Limpiar")
        self.btn_eliminar_nodo = QPushButton("Eliminar Nodo")
        self.rb_dibujar_nodo.setChecked(True)
        self.btn_ingresar_arista.setEnabled(False)
        layout_edicion = QHBoxLayout(grupo_edicion)
        for widget in (self.rb_dibujar_nodo, self.rb_dibujar_arista, self.btn_ingresar_arista,
                       self.btn_limpiar, self.btn_eliminar_nodo):
            layout_edicion.addWidget(widget)

        cabecera = QFrame()
        layout_cabecera = QVBoxLayout(cabecera)
        layout_cabecera.addWidget(grupo_algoritmo)
        #layout_cabecera.addWidget(self.grupo_tipo)
        layout_cabecera.addWidget(grupo_edicion)
        cabecera.setFixedHeight(290)

        self.lienzo = Lienzo(self.modelo)
        grupo_grafo = QGroupBox("Vista Grafo")
        QVBoxLayout(grupo_grafo).addWidget(self.lienzo)

        layout = QVBoxLayout(self)
        layout.addWidget(cabecera)
        layout.addWidget(grupo_grafo)
        self.setMinimumSize(ANCHO_MINIMO, ALTO_MINIMO)

        self.lienzo.clic.connect(self._al_hacer_clic)
        self.rb_dirigido.clicked.connect(self.cambiar_tipo_grafo)
        self.rb_no_dirigido.clicked.connect(self.cambiar_tipo_grafo)
        self.rb_dibujar_arista.toggled.connect(self.btn_ingresar_arista.setEnabled)
        self.btn_ingresar_arista.clicked.connect(self.pedir_arista)
        self.btn_limpiar.clicked.connect(self.limpiar)
        self.btn_eliminar_nodo.clicked.connect(self.pedir_nodo_a_eliminar)

    # Edición del grafo

    def _al_hacer_clic(self, x, y):
        if self.rb_dibujar_nodo.isChecked():
            self.modelo.agregar_nodo(x, y)
            self.lienzo.dibujar()

    def pedir_arista(self):
        valores = pedir_arista(self)
        if valores is not None:
            self.agregar_arista(*valores)

    def agregar_arista(self, origen, destino, peso):
        try:
            self.modelo.agregar_arista(origen, destino, peso)
        except ValueError as error:
            QMessageBox.warning(self, "Alerta", str(error))
            return
        self.lienzo.dibujar()

    def pedir_nodo_a_eliminar(self):
        nodo = pedir_nodo("Eliminar Nodo", self)
        if nodo is not None:
            self.eliminar_nodo(nodo)

    def eliminar_nodo(self, nodo):
        try:
            self.modelo.eliminar_nodo(nodo)
        except ValueError as error:
            QMessageBox.warning(self, "Error", str(error))
            return
        if not self.modelo.tiene_aristas():
            self._limpiar_resultado()
        elif self.ultimo_algoritmo:
            ejecutar, argumentos = self.ultimo_algoritmo
            if argumentos and argumentos[0] not in self.modelo.grafo:
                argumentos = (next(iter(self.modelo.grafo.nodes)),)
            ejecutar(*argumentos)
            return
        self.lienzo.dibujar()

    def limpiar(self):
        self.modelo.limpiar()
        self._limpiar_resultado()
        self.lienzo.dibujar()

    def cambiar_tipo_grafo(self):
        dirigido = self.rb_dirigido.isChecked()
        if dirigido == self.modelo.dirigido:
            return
        if self.modelo.grafo.number_of_nodes() and not self._confirmar_borrado():
            self._sincronizar_tipo()
            return
        self.modelo.cambiar_tipo(dirigido)
        self._limpiar_resultado()
        self.lienzo.dibujar()

    def _confirmar_borrado(self):
        alerta = QMessageBox(QMessageBox.Icon.Warning, "Alerta",
                             "Se borrará tu avance.\n¿Estás seguro de continuar?", parent=self)
        btn_si = alerta.addButton("Sí", QMessageBox.ButtonRole.YesRole)
        alerta.addButton("Cancelar", QMessageBox.ButtonRole.NoRole)
        alerta.exec()
        return alerta.clickedButton() is btn_si

    def _sincronizar_tipo(self):
        (self.rb_dirigido if self.modelo.dirigido else self.rb_no_dirigido).setChecked(True)

    def _limpiar_resultado(self):
        self.ultimo_algoritmo = None
        self.lbl_algoritmo.setText("")
        self.panel_info.limpiar()

    # Algoritmos

    def ejecutar_bfs(self, inicio):
        def calcular():
            aristas = algoritmos.bfs(self.modelo.grafo, inicio)
            return aristas, texto_pasos("PASOS BFS:", aristas)
        self._ejecutar(BFS, calcular, self.ejecutar_bfs, inicio)

    def ejecutar_dfs(self, inicio):
        def calcular():
            aristas = algoritmos.dfs(self.modelo.grafo, inicio)
            return aristas, texto_pasos("PASOS DFS:", aristas)
        self._ejecutar(DFS, calcular, self.ejecutar_dfs, inicio)

    def ejecutar_kruskal(self):
        def calcular():
            aristas = algoritmos.kruskal(self.modelo.grafo)
            peso_total = sum(peso for _, _, peso in aristas)
            return aristas, texto_pasos("PASOS KRUSKAL:", aristas) + f"\nPeso total: {peso_total}\n"
        self._ejecutar(KRUSKAL, calcular, self.ejecutar_kruskal)

    def ejecutar_dijkstra(self, inicio):
        def calcular():
            distancias, aristas = algoritmos.dijkstra(self.modelo.grafo, inicio)
            texto = "PASOS DIJKSTRA:\n"
            for origen, destino, peso in aristas:
                texto += f"Va de nodo {origen} -> nodo {destino} (Peso: {peso})\n"
            texto += f"\nDISTANCIAS DESDE {inicio}:\n"
            for nodo in sorted(distancias):
                distancia = distancias[nodo]
                texto += f"Nodo {nodo}: {distancia if distancia != math.inf else 'inalcanzable'}\n"
            return aristas, texto
        self._ejecutar(DIJKSTRA, calcular, self.ejecutar_dijkstra, inicio)

    def _ejecutar(self, nombre, calcular, repetir, *argumentos):
        if not self.modelo.tiene_aristas():
            QMessageBox.warning(self, "Advertencia", "No hay nodo o no hay aristas.")
            return
        try:
            aristas, texto = calcular()
        except ValueError as error:
            QMessageBox.warning(self, "Advertencia", str(error))
            return
        self.modelo.reiniciar_colores()
        self.modelo.pintar_aristas([arista[:2] for arista in aristas], COLOR_RECORRIDO)
        self.lienzo.dibujar()
        self.panel_info.mostrar(texto)
        self.lbl_algoritmo.setText(nombre)
        self.ultimo_algoritmo = (repetir, argumentos)

    def conservar_recorrido(self):
        if not self.modelo.tiene_aristas():
            return
        try:
            self.modelo.conservar_aristas(COLOR_RECORRIDO)
        except ValueError as error:
            QMessageBox.warning(self, "Advertencia", str(error))
            return
        self.lienzo.dibujar()

    # Archivos

    def guardar_imagen(self):
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar Imagen", "", "PNG Files (*.png);;All Files (*)")
        if not ruta:
            return
        try:
            self.lienzo.guardar_imagen(ruta)
        except (OSError, ValueError) as error:
            QMessageBox.critical(self, "Error", f"No se pudo guardar la imagen:\n{error}")

    def guardar_json(self):
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar Grafo", "", "JSON Files (*.json);;All Files (*)")
        if not ruta:
            return
        try:
            self.modelo.guardar_json(ruta)
        except OSError as error:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el grafo:\n{error}")

    def cargar_json(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Cargar Grafo", "", "JSON Files (*.json);;All Files (*)")
        if not ruta:
            return
        try:
            self.modelo.cargar_json(ruta)
        except (OSError, ValueError) as error:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el grafo:\n{error}")
            return
        self._despues_de_cargar()

    def cargar_grafo_prueba(self):
        try:
            self.modelo.cargar_texto(CARPETA_DATOS / "Nodos.txt", CARPETA_DATOS / "Aristas.txt")
        except (OSError, ValueError) as error:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el grafo de prueba:\n{error}")
            return
        self._despues_de_cargar()

    def _despues_de_cargar(self):
        self._sincronizar_tipo()
        self._limpiar_resultado()
        self.lienzo.dibujar()
