import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import QApplication, QDockWidget, QLabel, QMainWindow

from modelo import ModeloGrafo
from ui.panel_informacion import PanelInformacion
from ui.panel_vista import BFS, DFS, DIJKSTRA, KRUSKAL, PanelVista

ANCHO_PANEL_LATERAL = 300
DURACION_AVISO_MS = 3000


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
        self._crear_barra_de_estado()

    def _crear_panel_lateral(self):
        dock = QDockWidget("Panel de Información", self)
        dock.setWidget(self.panel_info)
        dock.setMinimumWidth(ANCHO_PANEL_LATERAL)
        dock.setMaximumWidth(ANCHO_PANEL_LATERAL)
        dock.setStyleSheet("QDockWidget::title { background: lightblue; }")
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)

    def _crear_menus(self):
        vista = self.panel_vista
        teclas = QKeySequence.StandardKey
        # PyQt entrega estas acciones a Python: se guardan en la ventana para que no se destruyan.
        self.accion_deshacer = vista.pila_deshacer.createUndoAction(self, "Deshacer")
        self.accion_deshacer.setShortcut(teclas.Undo)
        self.accion_rehacer = vista.pila_deshacer.createRedoAction(self, "Rehacer")
        self.accion_rehacer.setShortcuts([QKeySequence("Ctrl+Y"), QKeySequence("Ctrl+Shift+Z")])

        self._agregar_menu("&Archivo", [
            ("Guardar Avance", vista.guardar_json, teclas.Save),
            ("Cargar Avance", vista.cargar_json, teclas.Open),
            ("Guardar Imagen", vista.guardar_imagen, "Ctrl+E"),
            None,
            ("Salir", self.close, "Ctrl+Q"),
        ])
        self._agregar_menu("&Editar", [
            self.accion_deshacer,
            self.accion_rehacer,
            None,
            ("Modo Nodo", vista.activar_modo_nodo, "N"),
            ("Modo Arista", vista.activar_modo_arista, "A"),
            ("Cancelar Selección", vista.cancelar_seleccion, "Esc"),
            None,
            ("Eliminar Nodo", vista.eliminar_seleccionado, teclas.Delete),
            ("Limpiar Grafo", vista.limpiar, "Ctrl+L"),
        ])
        self._agregar_menu("&Grafos", [
            ("Grafo de Prueba", vista.cargar_grafo_prueba, "Ctrl+T"),
            ("Recorrido Seleccionado", vista.conservar_recorrido, "Ctrl+R"),
        ])
        self._agregar_menu("&Algoritmos", [
            (BFS, lambda *_: vista.pedir_inicio_y_ejecutar(vista.ejecutar_bfs), "Ctrl+1"),
            (DFS, lambda *_: vista.pedir_inicio_y_ejecutar(vista.ejecutar_dfs), "Ctrl+2"),
            (KRUSKAL, vista.ejecutar_kruskal, "Ctrl+3"),
            (DIJKSTRA, lambda *_: vista.pedir_inicio_y_ejecutar(vista.ejecutar_dijkstra), "Ctrl+4"),
        ])

    def _agregar_menu(self, titulo, elementos):
        """Crea un menú. Cada elemento es ``None`` (separador), una ``QAction`` o ``(texto, función, atajo)``."""
        menu = self.menuBar().addMenu(titulo)
        for elemento in elementos:
            if elemento is None:
                menu.addSeparator()
                continue
            if not isinstance(elemento, QAction):
                texto, funcion, atajo = elemento
                accion = QAction(texto, self)
                accion.setShortcut(QKeySequence(atajo))
                accion.triggered.connect(funcion)
                elemento = accion
            menu.addAction(elemento)
        return menu

    def _crear_barra_de_estado(self):
        self.etiqueta_ayuda = QLabel()
        self.statusBar().addWidget(self.etiqueta_ayuda, 1)
        self.panel_vista.ayuda.connect(self.etiqueta_ayuda.setText)
        self.panel_vista.notificacion.connect(lambda texto: self.statusBar().showMessage(texto, DURACION_AVISO_MS))
        self.panel_vista.actualizar_ayuda()


def main():
    app = QApplication(sys.argv)
    ventana = MainWindow()
    ventana.show()
    sys.exit(app.exec())
