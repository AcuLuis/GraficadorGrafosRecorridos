import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QDockWidget, QMainWindow

from modelo import ModeloGrafo
from ui.dialogos import pedir_nodo
from ui.panel_informacion import PanelInformacion
from ui.panel_vista import BFS, DFS, DIJKSTRA, KRUSKAL, PanelVista

ANCHO_PANEL_LATERAL = 300


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VISUALIZADOR")
        self.resize(1200, 900)
        self.modelo = ModeloGrafo()
        self.panel_info = PanelInformacion()
        self.panel_vista = PanelVista(self.modelo, self.panel_info)
        self.setCentralWidget(self.panel_vista)
        self._crear_panel_lateral()
        self._crear_menus()
        self.statusBar()

    def _crear_panel_lateral(self):
        dock = QDockWidget("Panel de Información", self)
        dock.setWidget(self.panel_info)
        dock.setMinimumWidth(ANCHO_PANEL_LATERAL)
        dock.setMaximumWidth(ANCHO_PANEL_LATERAL)
        dock.setStyleSheet("QDockWidget::title { background: lightblue; }")
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)

    def _crear_menus(self):
        vista = self.panel_vista
        self._agregar_menu("&Archivo", [
            ("Guardar Imagen", vista.guardar_imagen),
            ("Guardar Avance", vista.guardar_json),
            ("Cargar Avance", vista.cargar_json),
        ])
        self._agregar_menu("&Grafos", [
            ("Grafo de Prueba", vista.cargar_grafo_prueba),
            ("Recorrido Seleccionado", vista.conservar_recorrido),
        ])
        self._agregar_menu("&Algoritmos", [
            (BFS, self._con_nodo_inicial(vista.ejecutar_bfs)),
            (KRUSKAL, vista.ejecutar_kruskal),
            (DFS, self._con_nodo_inicial(vista.ejecutar_dfs)),
            (DIJKSTRA, self._con_nodo_inicial(vista.ejecutar_dijkstra)),
        ])

    def _agregar_menu(self, titulo, acciones):
        menu = self.menuBar().addMenu(titulo)
        for texto, funcion in acciones:
            accion = QAction(texto, self)
            accion.triggered.connect(funcion)
            menu.addAction(accion)

    def _con_nodo_inicial(self, ejecutar):
        def pedir_y_ejecutar(*_):
            inicio = pedir_nodo("Nodo Inicial", self)
            if inicio is not None:
                ejecutar(inicio)
        return pedir_y_ejecutar


def main():
    app = QApplication(sys.argv)
    ventana = MainWindow()
    ventana.show()
    sys.exit(app.exec())
