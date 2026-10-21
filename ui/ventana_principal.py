import sys

from PyQt6.QtCore import QLibraryInfo, QLocale, QSettings, Qt, QTranslator
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import QApplication, QDockWidget, QLabel, QMainWindow

from modelo import ModeloGrafo
from ui.panel_informacion import PanelInformacion
from ui.panel_vista import BELLMAN_FORD, BFS, CICLOS, DFS, DIJKSTRA, KRUSKAL, PRIM, TOPOLOGICO, PanelVista
from ui.tema import TEMAS, paleta_oscura

ANCHO_PANEL_LATERAL = 340
DURACION_AVISO_MS = 3000
ORGANIZACION = "GraficadorGrafos"
APLICACION = "Graficador de Grafos"
CLAVE_TEMA_OSCURO = "tema_oscuro"
PROPIEDAD_ESTILO_ORIGINAL = "estilo_original"


class MainWindow(QMainWindow):
    """Ventana principal. ``configuracion`` guarda las preferencias (por defecto, las del usuario)."""

    def __init__(self, configuracion=None):
        super().__init__()
        self.configuracion = configuracion if configuracion is not None else QSettings(ORGANIZACION, APLICACION)
        app = QApplication.instance()
        if app.property(PROPIEDAD_ESTILO_ORIGINAL) is None:
            app.setProperty(PROPIEDAD_ESTILO_ORIGINAL, app.style().name())
        self.setWindowTitle("VISUALIZADOR")
        self.resize(1200, 900)
        self.modelo = ModeloGrafo()
        self.panel_info = PanelInformacion()
        self.panel_vista = PanelVista(self.modelo, self.panel_info)
        self.setCentralWidget(self.panel_vista)
        self._crear_panel_lateral()
        self._crear_menus()
        self._crear_barra_de_estado()
        self.aplicar_tema(self.configuracion.value(CLAVE_TEMA_OSCURO, False, type=bool), guardar=False)

    def _crear_panel_lateral(self):
        self.dock = QDockWidget("Panel de Información", self)
        self.dock.setWidget(self.panel_info)
        self.dock.setMinimumWidth(ANCHO_PANEL_LATERAL)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)

    def aplicar_tema(self, oscuro, guardar=True):
        """Cambia entre el tema claro y el oscuro; si ``guardar``, lo recuerda para la próxima vez."""
        app = QApplication.instance()
        # Cambiar el estilo vuelve a pulir todos los widgets: solo se hace si el tema cambia.
        if bool(app.property(CLAVE_TEMA_OSCURO)) != oscuro:
            if oscuro:
                app.setStyle("Fusion")
                app.setPalette(paleta_oscura())
            else:
                app.setStyle(app.property(PROPIEDAD_ESTILO_ORIGINAL))
                app.setPalette(app.style().standardPalette())
            app.setProperty(CLAVE_TEMA_OSCURO, oscuro)
            # Al cambiar el estilo la barra de estado vuelve a mostrar la ayuda; sin esto se encimaría con el aviso.
            self.statusBar().clearMessage()
        tema = TEMAS["oscuro" if oscuro else "claro"]
        self.dock.setStyleSheet(f"QDockWidget::title {{ background: {tema['panel']}; }}")
        self.panel_vista.aplicar_tema(tema)
        self.accion_tema_oscuro.setChecked(oscuro)
        if guardar:
            self.configuracion.setValue(CLAVE_TEMA_OSCURO, oscuro)

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
            ("Exportar Pasos…", self.panel_info.exportar, "Ctrl+Shift+E"),
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
            ("Grafo Aleatorio…", vista.generar_grafo_aleatorio, "Ctrl+G"),
            None,
            ("Importar Lista de Adyacencia…", vista.importar_lista_adyacencia, "Ctrl+I"),
            ("Exportar Lista de Adyacencia…", vista.exportar_lista_adyacencia, "Ctrl+Shift+I"),
            None,
            ("Recorrido Seleccionado", vista.conservar_recorrido, "Ctrl+R"),
        ])
        self._agregar_menu("&Algoritmos", [
            (BFS, lambda: vista.pedir_inicio_y_ejecutar(vista.ejecutar_bfs), "Ctrl+1"),
            (DFS, lambda: vista.pedir_inicio_y_ejecutar(vista.ejecutar_dfs), "Ctrl+2"),
            None,
            (KRUSKAL, vista.ejecutar_kruskal, "Ctrl+3"),
            (PRIM, lambda: vista.pedir_inicio_y_ejecutar(vista.ejecutar_prim), "Ctrl+5"),
            None,
            (DIJKSTRA, lambda: vista.pedir_inicio_destino_y_ejecutar(vista.ejecutar_dijkstra), "Ctrl+4"),
            (BELLMAN_FORD, lambda: vista.pedir_inicio_destino_y_ejecutar(vista.ejecutar_bellman_ford), "Ctrl+6"),
            None,
            (TOPOLOGICO, vista.ejecutar_topologico, "Ctrl+7"),
            (CICLOS, vista.ejecutar_ciclos, "Ctrl+8"),
        ])
        lienzo = vista.lienzo
        self.accion_tema_oscuro = QAction("Tema Oscuro", self)
        self.accion_tema_oscuro.setCheckable(True)
        self.accion_tema_oscuro.setShortcut(QKeySequence("Ctrl+Shift+D"))
        self.accion_tema_oscuro.triggered.connect(self.aplicar_tema)
        self._agregar_menu("&Ver", [
            ("Acercar", lienzo.acercar, teclas.ZoomIn),
            ("Alejar", lienzo.alejar, teclas.ZoomOut),
            ("Restablecer Vista", lienzo.restablecer_vista, "Ctrl+0"),
            None,
            self.accion_tema_oscuro,
        ])
        reproductor = vista.reproductor
        self._agregar_menu("&Pasos", [
            ("Reproducir / Pausar", reproductor.alternar_reproduccion, "Ctrl+P"),
            ("Paso Anterior", reproductor.anterior, "Ctrl+Left"),
            ("Paso Siguiente", reproductor.siguiente, "Ctrl+Right"),
            ("Primer Paso", reproductor.primero, "Ctrl+Home"),
            ("Último Paso", reproductor.ultimo, "Ctrl+End"),
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
                # Se descarta el argumento "checked" de la señal: no debe llegar a parámetros opcionales.
                accion.triggered.connect(lambda *_, funcion=funcion: funcion())
                elemento = accion
            menu.addAction(elemento)
        return menu

    def _crear_barra_de_estado(self):
        self.etiqueta_ayuda = QLabel()
        self.statusBar().addWidget(self.etiqueta_ayuda, 1)
        self.panel_vista.ayuda.connect(self.etiqueta_ayuda.setText)
        self.panel_vista.notificacion.connect(lambda texto: self.statusBar().showMessage(texto, DURACION_AVISO_MS))
        self.panel_vista.actualizar_ayuda()


def instalar_traducciones(app):
    """Traduce al español los textos propios de Qt, como los botones Aceptar y Cancelar.

    Devuelve el traductor instalado, o ``None`` si no se encontraron las traducciones.
    """
    traductor = QTranslator(app)
    carpeta = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    if not traductor.load(QLocale(QLocale.Language.Spanish), "qtbase", "_", carpeta):
        return None
    app.installTranslator(traductor)
    return traductor


def main():
    app = QApplication(sys.argv)
    instalar_traducciones(app)
    ventana = MainWindow()
    ventana.show()
    sys.exit(app.exec())
