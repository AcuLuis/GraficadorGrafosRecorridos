import networkx as nx
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from PyQt6.QtCore import pyqtSignal


class Lienzo(FigureCanvasQTAgg):
    """Dibuja un ``ModeloGrafo`` con matplotlib.

    Emite ``clic(x, y)`` con las coordenadas del área de dibujo (entre 0 y 1)
    cuando el usuario hace clic dentro de ella.
    """

    clic = pyqtSignal(float, float)

    def __init__(self, modelo, parent=None):
        super().__init__(Figure())
        self.setParent(parent)
        self.modelo = modelo
        self.ejes = self.figure.add_subplot()
        self.mpl_connect("button_press_event", self._al_presionar)
        self.dibujar()

    def _al_presionar(self, evento):
        if evento.xdata is not None and evento.ydata is not None:
            self.clic.emit(evento.xdata, evento.ydata)

    def dibujar(self):
        grafo = self.modelo.grafo
        posiciones = self.modelo.posiciones
        self.ejes.clear()
        self.ejes.set_xlim(0, 1)
        self.ejes.set_ylim(0, 1)
        self.ejes.axis("off")
        self.ejes.add_patch(Rectangle((0, 0), 1, 1, linewidth=2, edgecolor="black", facecolor="none"))
        nx.draw(grafo, pos=posiciones, with_labels=True, font_weight="bold", ax=self.ejes,
                edge_color=[self.modelo.color_arista(origen, destino) for origen, destino in grafo.edges])
        nx.draw_networkx_edge_labels(grafo, pos=posiciones, edge_labels=nx.get_edge_attributes(grafo, "weight"),
                                     ax=self.ejes)
        self.draw_idle()

    def guardar_imagen(self, ruta):
        self.figure.savefig(ruta, bbox_inches="tight", pad_inches=0.1)
