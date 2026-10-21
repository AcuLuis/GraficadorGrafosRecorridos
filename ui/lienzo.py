import math

import networkx as nx
from matplotlib.backend_bases import MouseButton
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from PyQt6.QtCore import pyqtSignal

from ui.estilos import COLORES, COLORES_DESTACADOS

TAMANO_NODO = 300  # área del nodo en puntos², el valor por defecto de networkx
ANCHO_ARISTA = 1.0
ANCHO_ARISTA_DESTACADA = 2.5
LIMITES_INICIALES = (0.0, 1.0, 0.0, 1.0)  # x mínimo, x máximo, y mínimo, y máximo
FACTOR_ZOOM = 1.25
ANCHO_VISIBLE_MINIMO = 0.05  # zoom máximo
ANCHO_VISIBLE_MAXIMO = 4.0  # zoom mínimo
TOLERANCIA_PX = 5  # margen al detectar clics sobre nodos y aristas
UMBRAL_ARRASTRE_PX = 3  # desplazamiento mínimo para que un clic cuente como arrastre


class Lienzo(FigureCanvasQTAgg):
    """Dibuja un ``ModeloGrafo`` con matplotlib y traduce el mouse en acciones sobre nodos y aristas.

    Señales:

    - ``clic_vacio(x, y)``: clic izquierdo fuera de los nodos, en coordenadas del área (0 a 1).
    - ``clic_nodo(nodo)``: clic izquierdo sobre un nodo, sin arrastrarlo.
    - ``nodo_movido(nodo, inicio, fin)``: fin de un arrastre. Mientras dura, la posición del
      nodo se actualiza en el modelo para verlo moverse.
    - ``menu_nodo(nodo)`` y ``menu_arista(origen, destino)``: clic derecho sobre un elemento.

    Si ``estilo`` tiene un ``EstiloVista`` (por ejemplo, un paso de un algoritmo), los colores
    salen de él; si es ``None``, las aristas usan los colores guardados en el modelo.

    La rueda del mouse acerca o aleja la vista alrededor del cursor y arrastrar con el botón
    central la desplaza. Los nodos siempre viven dentro del área de dibujo (de 0 a 1).
    """

    clic_vacio = pyqtSignal(float, float)
    clic_nodo = pyqtSignal(object)
    nodo_movido = pyqtSignal(object, object, object)
    menu_nodo = pyqtSignal(object)
    menu_arista = pyqtSignal(object, object)

    def __init__(self, modelo, parent=None):
        super().__init__(Figure())
        self.setParent(parent)
        self.modelo = modelo
        self.nodo_resaltado = None
        self.estilo = None
        self.limites = LIMITES_INICIALES
        self._arrastre = None
        self._desplazamiento = None
        self.ejes = self.figure.add_subplot()
        self.figure.subplots_adjust(left=0.02, right=0.98, bottom=0.02, top=0.98)
        self.mpl_connect("button_press_event", self._al_presionar)
        self.mpl_connect("motion_notify_event", self._al_mover)
        self.mpl_connect("button_release_event", self._al_soltar)
        self.mpl_connect("scroll_event", self._al_girar_rueda)
        self.dibujar()

    def dibujar(self):
        grafo = self.modelo.grafo
        posiciones = self.modelo.posiciones
        self.ejes.clear()
        self._aplicar_limites()
        self.ejes.axis("off")
        self.ejes.add_patch(Rectangle((0, 0), 1, 1, linewidth=2, edgecolor="black", facecolor="none"))
        aristas = list(grafo.edges)
        colores_aristas = [self._color_arista(*arista) for arista in aristas]
        discontinuas = self.estilo.discontinuas if self.estilo else set()
        nx.draw(grafo, pos=posiciones, with_labels=True, font_weight="bold", ax=self.ejes, node_size=TAMANO_NODO,
                node_color=[self._color_nodo(nodo) for nodo in grafo.nodes],
                edgelist=aristas, edge_color=colores_aristas,
                width=[ANCHO_ARISTA_DESTACADA if color in COLORES_DESTACADOS else ANCHO_ARISTA for color in colores_aristas],
                style=["dashed" if arista in discontinuas else "solid" for arista in aristas])
        nx.draw_networkx_edge_labels(grafo, pos=posiciones, edge_labels=nx.get_edge_attributes(grafo, "weight"),
                                     ax=self.ejes)
        self.draw_idle()

    def _color_nodo(self, nodo):
        if nodo == self.nodo_resaltado:
            return COLORES["seleccionado"]
        if self.estilo and nodo in self.estilo.nodos:
            return self.estilo.nodos[nodo]
        return COLORES["normal"]

    def _color_arista(self, origen, destino):
        if self.estilo:
            return self.estilo.aristas.get((origen, destino), COLORES["arista"])
        return self.modelo.color_arista(origen, destino)

    def guardar_imagen(self, ruta):
        self.figure.savefig(ruta, bbox_inches="tight", pad_inches=0.1)

    # Zoom y desplazamiento

    def acercar(self, factor=FACTOR_ZOOM, centro=None):
        """Acerca la vista (``factor`` > 1) o la aleja (``factor`` < 1) manteniendo fijo ``centro``."""
        x0, x1, y0, y1 = self.limites
        cx, cy = centro if centro is not None else ((x0 + x1) / 2, (y0 + y1) / 2)
        ancho = min(max((x1 - x0) / factor, ANCHO_VISIBLE_MINIMO), ANCHO_VISIBLE_MAXIMO)
        escala = ancho / (x1 - x0)
        self.limites = (cx - (cx - x0) * escala, cx + (x1 - cx) * escala,
                        cy - (cy - y0) * escala, cy + (y1 - cy) * escala)
        self._aplicar_limites()
        self.draw_idle()

    def alejar(self):
        self.acercar(1 / FACTOR_ZOOM)

    def restablecer_vista(self):
        self.limites = LIMITES_INICIALES
        self._aplicar_limites()
        self.draw_idle()

    def _aplicar_limites(self):
        x0, x1, y0, y1 = self.limites
        self.ejes.set_xlim(x0, x1)
        self.ejes.set_ylim(y0, y1)

    # Elementos bajo el cursor, en píxeles de la figura

    def _en_pixeles(self, nodo):
        return self.ejes.transData.transform(self.modelo.posiciones[nodo])

    def nodo_en(self, x, y):
        radio = math.sqrt(TAMANO_NODO) / 2 * self.figure.dpi / 72 + TOLERANCIA_PX
        cercanos = [(math.dist((x, y), self._en_pixeles(nodo)), nodo) for nodo in self.modelo.grafo.nodes]
        cercanos = [candidato for candidato in cercanos if candidato[0] <= radio]
        return min(cercanos, key=lambda candidato: candidato[0])[1] if cercanos else None

    def arista_en(self, x, y):
        cercanas = [(_distancia_a_segmento((x, y), self._en_pixeles(origen), self._en_pixeles(destino)), (origen, destino))
                    for origen, destino in self.modelo.grafo.edges]
        cercanas = [candidata for candidata in cercanas if candidata[0] <= TOLERANCIA_PX]
        return min(cercanas, key=lambda candidata: candidata[0])[1] if cercanas else None

    # Eventos del mouse

    def _al_presionar(self, evento):
        if evento.inaxes is not self.ejes:
            return
        if evento.button == MouseButton.MIDDLE:
            self._desplazamiento = {"pixel": (evento.x, evento.y), "limites": self.limites}
            return
        nodo = self.nodo_en(evento.x, evento.y)
        if evento.button == MouseButton.RIGHT:
            if nodo is not None:
                self.menu_nodo.emit(nodo)
            elif (arista := self.arista_en(evento.x, evento.y)) is not None:
                self.menu_arista.emit(*arista)
        elif evento.button == MouseButton.LEFT:
            if nodo is None:
                if 0 <= evento.xdata <= 1 and 0 <= evento.ydata <= 1:
                    self.clic_vacio.emit(evento.xdata, evento.ydata)
            else:
                self._arrastre = {"nodo": nodo, "inicio": self.modelo.posiciones[nodo],
                                  "pixel": (evento.x, evento.y), "movido": False}

    def _al_mover(self, evento):
        if self._desplazamiento is not None:
            self._desplazar(evento)
            return
        arrastre = self._arrastre
        if arrastre is None or evento.inaxes is not self.ejes:
            return
        if not arrastre["movido"] and math.dist((evento.x, evento.y), arrastre["pixel"]) < UMBRAL_ARRASTRE_PX:
            return
        arrastre["movido"] = True
        self.modelo.mover_nodo(arrastre["nodo"], evento.xdata, evento.ydata)
        self.dibujar()

    def _desplazar(self, evento):
        (x_inicial, y_inicial), (x0, x1, y0, y1) = self._desplazamiento["pixel"], self._desplazamiento["limites"]
        caja = self.ejes.bbox
        dx = (evento.x - x_inicial) * (x1 - x0) / caja.width
        dy = (evento.y - y_inicial) * (y1 - y0) / caja.height
        self.limites = (x0 - dx, x1 - dx, y0 - dy, y1 - dy)
        self._aplicar_limites()
        self.draw_idle()

    def _al_girar_rueda(self, evento):
        if evento.inaxes is self.ejes and evento.step:
            self.acercar(FACTOR_ZOOM ** evento.step, centro=(evento.xdata, evento.ydata))

    def _al_soltar(self, evento):
        if evento.button == MouseButton.MIDDLE:
            self._desplazamiento = None
            return
        arrastre, self._arrastre = self._arrastre, None
        if arrastre is None:
            return
        nodo = arrastre["nodo"]
        if arrastre["movido"]:
            self.nodo_movido.emit(nodo, arrastre["inicio"], self.modelo.posiciones[nodo])
        else:
            self.clic_nodo.emit(nodo)


def _distancia_a_segmento(punto, inicio, fin):
    (px, py), (ax, ay), (bx, by) = punto, inicio, fin
    dx, dy = bx - ax, by - ay
    largo2 = dx * dx + dy * dy
    t = 0.0 if largo2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / largo2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))
