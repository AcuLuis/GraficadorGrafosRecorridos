from pathlib import Path

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QCursor, QFont, QUndoStack
from PyQt6.QtWidgets import (QFileDialog, QGroupBox, QHBoxLayout, QLabel, QMenu, QMessageBox,
                             QPushButton, QRadioButton, QSizePolicy, QVBoxLayout, QWidget)

import algoritmos
from ui.comandos import ComandoModelo
from ui.dialogos import pedir_arista, pedir_inicio_y_destino, pedir_nodo, pedir_peso
from ui.estilos import LEYENDAS, estilo_de_paso
from ui.leyenda import Leyenda
from ui.lienzo import Lienzo
from ui.reproductor import Reproductor

CARPETA_DATOS = Path(__file__).resolve().parent.parent / "datos"
COLOR_RECORRIDO = "blue"
ANCHO_MINIMO = 800
ALTO_MINIMO = 600

BFS = "BFS - Búsqueda en anchura"
DFS = "DFS - Búsqueda en profundidad"
KRUSKAL = "Kruskal - Árbol de expansión mínima"
DIJKSTRA = "Dijkstra - Camino más corto"

AYUDA_MODO_NODO = ("Clic en un espacio vacío: crear nodo · Arrastrar un nodo: moverlo · "
                   "Clic en un nodo: seleccionarlo · Clic derecho: más opciones")
AYUDA_ARISTA_ORIGEN = "Modo arista: haz clic en el nodo de origen."
AYUDA_ARISTA_DESTINO = "Modo arista: origen en el nodo {nodo}. Haz clic en el nodo de destino (Esc cancela)."


class PanelVista(QWidget):
    """Área principal: controles de edición, lienzo y ejecución de algoritmos sobre el modelo.

    Emite ``ayuda(texto)`` con las instrucciones del modo actual y ``notificacion(texto)``
    con la descripción de cada cambio aplicado al grafo.
    """

    ayuda = pyqtSignal(str)
    notificacion = pyqtSignal(str)

    def __init__(self, modelo, panel_info, parent=None):
        super().__init__(parent)
        self.modelo = modelo
        self.panel_info = panel_info
        # (función, argumentos) del último algoritmo, para recalcularlo cuando cambia el grafo.
        self.ultimo_algoritmo = None
        self.pasos = []
        self.pila_deshacer = QUndoStack(self)
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

        self.grupo_tipo = QGroupBox("Tipo de grafo")
        self.rb_no_dirigido = QRadioButton("No dirigido")
        self.rb_dirigido = QRadioButton("Dirigido")
        self.rb_no_dirigido.setChecked(True)
        layout_tipo = QHBoxLayout(self.grupo_tipo)
        layout_tipo.addWidget(self.rb_no_dirigido)
        layout_tipo.addWidget(self.rb_dirigido)

        grupo_edicion = QGroupBox("Edición")
        self.rb_dibujar_nodo = QRadioButton("Dibujar Nodo")
        self.rb_dibujar_arista = QRadioButton("Dibujar Arista")
        self.btn_ingresar_arista = QPushButton("Ingresar Arista…")
        self.btn_eliminar_nodo = QPushButton("Eliminar Nodo…")
        self.btn_limpiar = QPushButton("Limpiar")
        self.rb_dibujar_nodo.setChecked(True)
        self.rb_dibujar_nodo.setToolTip("Clic en el lienzo para crear nodos; arrastra un nodo para moverlo.")
        self.rb_dibujar_arista.setToolTip("Clic en el nodo de origen y luego en el de destino.")
        self.btn_ingresar_arista.setToolTip("Agregar una arista escribiendo sus nodos y su peso.")
        layout_edicion = QHBoxLayout(grupo_edicion)
        for widget in (self.rb_dibujar_nodo, self.rb_dibujar_arista, self.btn_ingresar_arista,
                       self.btn_eliminar_nodo, self.btn_limpiar):
            layout_edicion.addWidget(widget)
        layout_edicion.addStretch()

        cabecera = QWidget()
        cabecera.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        layout_cabecera = QVBoxLayout(cabecera)
        layout_cabecera.setContentsMargins(0, 0, 0, 0)
        layout_cabecera.addWidget(grupo_algoritmo)
        fila_controles = QHBoxLayout()
        fila_controles.addWidget(self.grupo_tipo)
        fila_controles.addWidget(grupo_edicion, 1)
        layout_cabecera.addLayout(fila_controles)

        self.lienzo = Lienzo(self.modelo)
        self.leyenda = Leyenda()
        self.reproductor = Reproductor()
        grupo_grafo = QGroupBox("Vista Grafo")
        layout_grafo = QVBoxLayout(grupo_grafo)
        layout_grafo.addWidget(self.lienzo, 1)
        layout_grafo.addWidget(self.leyenda)
        layout_grafo.addWidget(self.reproductor)

        layout = QVBoxLayout(self)
        layout.addWidget(cabecera)
        layout.addWidget(grupo_grafo, 1)
        self.setMinimumSize(ANCHO_MINIMO, ALTO_MINIMO)

        self.reproductor.paso_cambiado.connect(self._mostrar_paso)
        self.panel_info.paso_elegido.connect(self.reproductor.elegir)
        self.lienzo.clic_vacio.connect(self._al_hacer_clic_vacio)
        self.lienzo.clic_nodo.connect(self._al_hacer_clic_en_nodo)
        self.lienzo.nodo_movido.connect(self._al_mover_nodo)
        self.lienzo.menu_nodo.connect(lambda nodo: self.menu_nodo(nodo).exec(QCursor.pos()))
        self.lienzo.menu_arista.connect(lambda origen, destino: self.menu_arista(origen, destino).exec(QCursor.pos()))
        self.rb_dirigido.clicked.connect(self.cambiar_tipo_grafo)
        self.rb_no_dirigido.clicked.connect(self.cambiar_tipo_grafo)
        self.rb_dibujar_arista.toggled.connect(lambda *_: self.seleccionar(None))
        self.btn_ingresar_arista.clicked.connect(self.pedir_arista)
        self.btn_eliminar_nodo.clicked.connect(self.pedir_nodo_a_eliminar)
        self.btn_limpiar.clicked.connect(self.limpiar)

    # Selección y ayuda

    @property
    def seleccionado(self):
        return self.lienzo.nodo_resaltado

    def seleccionar(self, nodo):
        self.lienzo.nodo_resaltado = nodo
        self.lienzo.dibujar()
        self.actualizar_ayuda()

    def actualizar_ayuda(self):
        if self.rb_dibujar_nodo.isChecked():
            texto = AYUDA_MODO_NODO
        elif self.seleccionado is None:
            texto = AYUDA_ARISTA_ORIGEN
        else:
            texto = AYUDA_ARISTA_DESTINO.format(nodo=self.seleccionado)
        self.ayuda.emit(texto)

    def activar_modo_nodo(self):
        self.rb_dibujar_nodo.setChecked(True)

    def activar_modo_arista(self):
        self.rb_dibujar_arista.setChecked(True)

    def cancelar_seleccion(self):
        self.seleccionar(None)

    def nombre_arista(self, origen, destino):
        return f"{origen} → {destino}" if self.modelo.dirigido else f"{origen} - {destino}"

    # Interacción con el lienzo

    def _al_hacer_clic_vacio(self, x, y):
        if self.rb_dibujar_nodo.isChecked():
            self.lienzo.nodo_resaltado = None
            self._modificar(f"Crear nodo {self.modelo.siguiente_id()}", lambda: self.modelo.agregar_nodo(x, y))
            self.actualizar_ayuda()
        else:
            self.seleccionar(None)

    def _al_hacer_clic_en_nodo(self, nodo):
        origen = self.seleccionado
        if self.rb_dibujar_nodo.isChecked() or origen is None or origen == nodo:
            self.seleccionar(None if origen == nodo else nodo)
            return
        self.seleccionar(None)
        existe = self.modelo.grafo.has_edge(origen, nodo)
        peso = pedir_peso(self, f"Peso de la arista {self.nombre_arista(origen, nodo)}:",
                          self.modelo.peso(origen, nodo) if existe else 1)
        if peso is not None:
            self.agregar_arista(origen, nodo, peso)

    def _al_mover_nodo(self, nodo, inicio, fin):
        # Durante el arrastre el lienzo ya movió el nodo; se registra el cambio completo para poder deshacerlo.
        self.modelo.mover_nodo(nodo, *inicio)
        self._modificar(f"Mover nodo {nodo}", lambda: self.modelo.mover_nodo(nodo, *fin))

    def menu_nodo(self, nodo):
        menu = QMenu(self)
        _agregar_opcion(menu, f"Eliminar nodo {nodo}", lambda: self.eliminar_nodo(nodo))
        menu.addSeparator()
        _agregar_opcion(menu, f"BFS desde el nodo {nodo}", lambda: self.ejecutar_bfs(nodo))
        _agregar_opcion(menu, f"DFS desde el nodo {nodo}", lambda: self.ejecutar_dfs(nodo))
        _agregar_opcion(menu, f"Dijkstra desde el nodo {nodo}", lambda: self.ejecutar_dijkstra(nodo))
        origen = self.seleccionado
        if origen is not None and origen != nodo:
            _agregar_opcion(menu, f"Camino más corto del nodo {origen} al nodo {nodo}",
                            lambda: self.ejecutar_dijkstra(origen, nodo))
        return menu

    def menu_arista(self, origen, destino):
        menu = QMenu(self)
        nombre = self.nombre_arista(origen, destino)
        _agregar_opcion(menu, f"Editar peso de {nombre}…", lambda: self.pedir_nuevo_peso(origen, destino))
        _agregar_opcion(menu, f"Eliminar arista {nombre}", lambda: self.eliminar_arista(origen, destino))
        return menu

    # Edición del grafo

    def _modificar(self, descripcion, accion, reiniciar_resultado=False, prefijo_error=""):
        """Aplica ``accion`` al modelo y la registra en la pila de deshacer.

        Si la acción falla se muestra el error y el modelo queda como estaba.
        """
        antes = self.modelo.instantanea()
        try:
            accion()
        except (OSError, ValueError) as error:
            QMessageBox.warning(self, "Alerta", f"{prefijo_error}{error}")
            return False
        if reiniciar_resultado:
            self._limpiar_resultado()
        self.pila_deshacer.push(ComandoModelo(descripcion, self.modelo, antes, self.modelo.instantanea(),
                                              self._grafo_modificado))
        self._grafo_modificado()
        self.notificacion.emit(descripcion)
        return True

    def _grafo_modificado(self):
        """Actualiza la vista tras un cambio del modelo, recalculando el último algoritmo."""
        self._sincronizar_tipo()
        if self.seleccionado is not None and self.seleccionado not in self.modelo.grafo:
            self.lienzo.nodo_resaltado = None
            self.actualizar_ayuda()
        if self.ultimo_algoritmo and self.modelo.tiene_aristas():
            ejecutar, argumentos = self.ultimo_algoritmo
            # Si se eliminó el nodo inicial se usa el primero del grafo; si se eliminó el destino, ninguno.
            argumentos = tuple(nodo if nodo in self.modelo.grafo else None for nodo in argumentos)
            if argumentos and argumentos[0] is None:
                argumentos = (next(iter(self.modelo.grafo.nodes)), *argumentos[1:])
            indice, en_el_ultimo = self.reproductor.indice, self.reproductor.indice == self.reproductor.total - 1
            ejecutar(*argumentos)
            if not en_el_ultimo:
                self.reproductor.ir_a(indice)
            return
        if not self.modelo.tiene_aristas():
            self._limpiar_resultado()
        self.lienzo.dibujar()

    def pedir_arista(self):
        valores = pedir_arista(self)
        if valores is not None:
            self.agregar_arista(*valores)

    def agregar_arista(self, origen, destino, peso):
        nombre = self.nombre_arista(origen, destino)
        descripcion = (f"Cambiar peso de {nombre}" if self.modelo.grafo.has_edge(origen, destino)
                       else f"Agregar arista {nombre}")
        self._modificar(descripcion, lambda: self.modelo.agregar_arista(origen, destino, peso))

    def pedir_nuevo_peso(self, origen, destino):
        nombre = self.nombre_arista(origen, destino)
        peso = pedir_peso(self, f"Peso de la arista {nombre}:", self.modelo.peso(origen, destino))
        if peso is not None:
            self._modificar(f"Cambiar peso de {nombre}", lambda: self.modelo.cambiar_peso(origen, destino, peso))

    def eliminar_arista(self, origen, destino):
        self._modificar(f"Eliminar arista {self.nombre_arista(origen, destino)}",
                        lambda: self.modelo.eliminar_arista(origen, destino))

    def pedir_nodo_a_eliminar(self):
        if not self.modelo.grafo.number_of_nodes():
            QMessageBox.warning(self, "Alerta", "El grafo no tiene nodos.")
            return
        nodo = pedir_nodo("Eliminar Nodo", self.modelo.grafo.nodes, self, self.seleccionado)
        if nodo is not None:
            self.eliminar_nodo(nodo)

    def eliminar_seleccionado(self):
        """Elimina el nodo seleccionado o, si no hay ninguno, pregunta cuál eliminar."""
        if self.seleccionado is None:
            self.pedir_nodo_a_eliminar()
        else:
            self.eliminar_nodo(self.seleccionado)

    def eliminar_nodo(self, nodo):
        self._modificar(f"Eliminar nodo {nodo}", lambda: self.modelo.eliminar_nodo(nodo))

    def limpiar(self):
        if self.modelo.grafo.number_of_nodes() and not self._confirmar("Se borrará todo el grafo."):
            return
        self._modificar("Limpiar grafo", self.modelo.limpiar, reiniciar_resultado=True)

    def cambiar_tipo_grafo(self):
        dirigido = self.rb_dirigido.isChecked()
        if dirigido == self.modelo.dirigido:
            return
        if self.modelo.grafo.number_of_nodes() and not self._confirmar(
                "Al cambiar el tipo de grafo se borrará el grafo actual."):
            self._sincronizar_tipo()
            return
        self._modificar("Cambiar a grafo dirigido" if dirigido else "Cambiar a grafo no dirigido",
                        lambda: self.modelo.cambiar_tipo(dirigido), reiniciar_resultado=True)

    def conservar_recorrido(self):
        if not self.modelo.tiene_aristas():
            return
        if not any(self.modelo.color_arista(*arista) == COLOR_RECORRIDO for arista in self.modelo.grafo.edges):
            QMessageBox.warning(self, "Alerta", "Primero ejecuta un algoritmo para obtener un recorrido.")
            return
        if self._confirmar("Se eliminarán las aristas que no forman parte del recorrido."):
            self._modificar("Conservar recorrido", lambda: self.modelo.conservar_aristas(COLOR_RECORRIDO))

    def _confirmar(self, mensaje):
        alerta = QMessageBox(QMessageBox.Icon.Warning, "Confirmar",
                             f"{mensaje}\nPuedes deshacerlo con Ctrl+Z.\n¿Deseas continuar?", parent=self)
        btn_si = alerta.addButton("Sí", QMessageBox.ButtonRole.YesRole)
        alerta.addButton("Cancelar", QMessageBox.ButtonRole.NoRole)
        alerta.setDefaultButton(btn_si)
        alerta.exec()
        return alerta.clickedButton() is btn_si

    def _sincronizar_tipo(self):
        (self.rb_dirigido if self.modelo.dirigido else self.rb_no_dirigido).setChecked(True)

    def _limpiar_resultado(self):
        self.ultimo_algoritmo = None
        self.pasos = []
        self.lienzo.estilo = None
        self.lbl_algoritmo.setText("")
        self.leyenda.limpiar()
        self.reproductor.limpiar()
        self.panel_info.limpiar()

    # Algoritmos

    def pedir_inicio_y_ejecutar(self, ejecutar):
        """Pide el nodo inicial (sugiere el seleccionado o el último usado) y ejecuta el algoritmo."""
        if not self.modelo.tiene_aristas():
            QMessageBox.warning(self, "Advertencia", "No hay nodo o no hay aristas.")
            return
        inicio = pedir_nodo("Nodo Inicial", self.modelo.grafo.nodes, self, self._inicio_sugerido())
        if inicio is not None:
            ejecutar(inicio)

    def pedir_y_ejecutar_dijkstra(self):
        """Pide el nodo inicial y, opcionalmente, el destino, y ejecuta Dijkstra."""
        if not self.modelo.tiene_aristas():
            QMessageBox.warning(self, "Advertencia", "No hay nodo o no hay aristas.")
            return
        eleccion = pedir_inicio_y_destino(self.modelo.grafo.nodes, self, self._inicio_sugerido())
        if eleccion is not None:
            self.ejecutar_dijkstra(*eleccion)

    def _inicio_sugerido(self):
        if self.seleccionado is not None:
            return self.seleccionado
        if self.ultimo_algoritmo and self.ultimo_algoritmo[1]:
            return self.ultimo_algoritmo[1][0]
        return None

    def ejecutar_bfs(self, inicio):
        self._ejecutar(BFS, f"desde el nodo {inicio}", "bfs",
                       lambda: algoritmos.bfs_pasos(self.modelo.grafo, inicio), self.ejecutar_bfs, inicio)

    def ejecutar_dfs(self, inicio):
        self._ejecutar(DFS, f"desde el nodo {inicio}", "dfs",
                       lambda: algoritmos.dfs_pasos(self.modelo.grafo, inicio), self.ejecutar_dfs, inicio)

    def ejecutar_kruskal(self):
        self._ejecutar(KRUSKAL, "", "kruskal", lambda: algoritmos.kruskal_pasos(self.modelo.grafo),
                       self.ejecutar_kruskal)

    def ejecutar_dijkstra(self, inicio, destino=None):
        detalle = f"desde el nodo {inicio}" if destino is None else f"del nodo {inicio} al nodo {destino}"
        self._ejecutar(DIJKSTRA, detalle, "dijkstra",
                       lambda: algoritmos.dijkstra_pasos(self.modelo.grafo, inicio, destino),
                       self.ejecutar_dijkstra, inicio, destino)

    def _ejecutar(self, nombre, detalle, leyenda, calcular, repetir, *argumentos):
        """Calcula los pasos del algoritmo, guarda el resultado en el modelo y muestra el último paso."""
        if not self.modelo.tiene_aristas():
            QMessageBox.warning(self, "Advertencia", "No hay nodo o no hay aristas.")
            return
        try:
            pasos = calcular()
        except ValueError as error:
            QMessageBox.warning(self, "Advertencia", str(error))
            return
        final = pasos[-1]
        self.modelo.reiniciar_colores()
        self.modelo.pintar_aristas(final.aristas, COLOR_RECORRIDO)
        self.pasos = pasos
        self.ultimo_algoritmo = (repetir, argumentos)
        self.lbl_algoritmo.setText(nombre)
        self.leyenda.mostrar(LEYENDAS[leyenda])
        self.panel_info.mostrar_resultado(f"{nombre} {detalle}".strip(), pasos)
        self.reproductor.cargar(len(pasos))

    def _mostrar_paso(self, indice):
        if not self.pasos:
            return
        paso = self.pasos[indice]
        self.lienzo.estilo = estilo_de_paso(paso, self.modelo.dirigido)
        self.lienzo.dibujar()
        self.panel_info.seleccionar_paso(indice, paso)

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
            return
        self.notificacion.emit(f"Grafo guardado en {ruta}")

    def cargar_json(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Cargar Grafo", "", "JSON Files (*.json);;All Files (*)")
        if ruta:
            self._modificar("Cargar grafo", lambda: self.modelo.cargar_json(ruta), reiniciar_resultado=True,
                            prefijo_error="No se pudo cargar el grafo:\n")

    def cargar_grafo_prueba(self):
        self._modificar("Cargar grafo de prueba",
                        lambda: self.modelo.cargar_texto(CARPETA_DATOS / "Nodos.txt", CARPETA_DATOS / "Aristas.txt"),
                        reiniciar_resultado=True, prefijo_error="No se pudo cargar el grafo de prueba:\n")


def _agregar_opcion(menu, texto, funcion):
    menu.addAction(texto).triggered.connect(lambda *_: funcion())
