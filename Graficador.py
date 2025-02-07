from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import networkx as nx
import matplotlib.pyplot as plt
from Arista import MiDialogo
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from Utilidades import Operaciones as op
from collections import deque
from DialogNodo import *
import json

centralWidget = None
panel = None
ancho = None
altura = None
posX = None
posY = None
TipoGrafo="NoDirigido"
verifica = None
class Lienzo:
    def __init__(self, main_window):
        self.main_window = main_window    
        self.graph = nx.Graph()
        self.edge_colors={}
        self.edge_weights = {} 
        self.pos = {}
        self.fig, self.ax = plt.subplots()
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.MouseClick)
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.ax.axis('off')
        self.rect = plt.Rectangle((0,0), 1, 1, linewidth=2, edgecolor='black', facecolor='none')
        self.ax.add_patch(self.rect)
    def setTipoGrafo(self, tipo):
        pass
    def DibujarArista(self, posNodo1, posNodo2,peso=1):
        pass
    def Alertas(self, mensaje):
        pass
    def MouseClick(self, event):
        pass
    def DibujarGrafo(self):
        pass
    def GuardarIMG(self):
        pass
    def guardarEnJSON(self):
        pass
    def cargarJson(self):
        pass
    def getNodos(self):
        pass
    def getAristas(self):
        pass
    def getPesos(self):
        pass
    def setAristaColor(self,listaAristas,color):
        pass
    def setAristaColorDirigido(self,listaAristas,color):
        pass
    def Limpiar(self):
        pass
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VISUALIZADOR")
        global AltoPanelVista
        global AnchoPanelVista
        AltoPanelVista=600
        AnchoPanelVista=800
        status_bar = self.statusBar()
        self.size_escena = QLabel("")
        status_bar.addWidget(self.size_escena)
        self.resize(1200,900)
        menubar = self.menuBar()
        menuArchivo = menubar.addMenu("&Archivo")
        menuArchivo.addSeparator()
        menuGrafos = menubar.addMenu("&Grafos")
        menuGrafos.addSeparator()
        menuAlgoritmos = menubar.addMenu("&Algoritmos")
        menuAlgoritmos.addSeparator()
        btnGuardarImagen=QAction('Guardar Imagen', self)
        btnGuardarImagen.triggered.connect(self.GuardarImagen)
        menuArchivo.addAction(btnGuardarImagen)
        btnGuardarJson=QAction('Guardar Avance', self)
        btnGuardarJson.triggered.connect(self.GuardarJson)
        menuArchivo.addAction(btnGuardarJson)
        btnCargarJson=QAction('Cargar Avance', self)
        btnCargarJson.triggered.connect(self.CargarJson)
        menuArchivo.addAction(btnCargarJson)
        btnGrafoPrueba=QAction('Grafo de Prueba', self)
        btnGrafoPrueba.triggered.connect(self.dibujaPruebaGrafo)
        menuGrafos.addAction(btnGrafoPrueba)
        btnselecReco=QAction('Recorrido Seleccionado', self)
        btnselecReco.triggered.connect(self.seleccion)
        menuGrafos.addAction(btnselecReco)
        btnBFS=QAction('BFS-Busqueda en anchura', self)
        btnBFS.triggered.connect(self.BFS)
        menuAlgoritmos.addAction(btnBFS)
        btnKruskal=QAction('Kruskal-Arbol de expansión mínima', self)
        btnKruskal.triggered.connect(self.KRUSKAL)
        menuAlgoritmos.addAction(btnKruskal)
        btnDFS=QAction('DFS-Busqueda en profundidad', self)
        btnDFS.triggered.connect(self.DFS)
        menuAlgoritmos.addAction(btnDFS)
        btnDIJS=QAction('DIJSKTRA-Camino mas corto', self)
        btnDIJS.triggered.connect(self.DIJSKTRA)
        menuAlgoritmos.addAction(btnDIJS)
        global centralWidget 
        centralWidget= PanelVista(AnchoPanelVista, AltoPanelVista)
        self.setCentralWidget(centralWidget)
        self.dock_widget = QDockWidget("Panel de Informacion", self)
        global panel
        panel = Panel()
        panel.setMinimumWidth(300)
        self.dock_widget.setWidget(panel)
        self.dock_widget.setMaximumWidth(300)
        self.dock_widget.setStyleSheet(
                           "QDockWidget::title"
                           "{"
                           "background : lightblue;"
                           "}")
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_widget)
    def GuardarImagen(self):
        pass
    def GuardarJson(self):
        pass
    def CargarJson(self):
        pass
    def Alertas(self, mensaje):
        pass
    def BFS(self):
        pass
    def KRUSKAL(self):
        pass
    def DFS(self):
        pass
    def DIJSKTRA(self):
        pass
    def dibujaPruebaGrafo(self):
        pass
    def seleccion(self):
        pass
class PanelVista(QWidget):
    def __init__(self,escalaAncho, escalaAlto):
        super().__init__()
        self.ancho = escalaAncho
        self.alto = escalaAlto
        cabezera = QFrame()
        grafoUI = QGroupBox("Vista Grafo")
        cbzAlgoritmo=QGroupBox("Algoritmo")
        lblAlgoritmo = QLabel("Nombre Algoritmo:")
        self.lblTipo = QLabel("")
        font = QFont()
        font.setPointSize(16)  # Tamaño de la fuente
        font.setBold(True)    # Configurar la negrita
        self.lblTipo.setFont(font)
        cbzAlgoritmo_layout=QHBoxLayout()
        cbzAlgoritmo_layout.addWidget(lblAlgoritmo)
        cbzAlgoritmo_layout.addWidget(self.lblTipo)
        cbzAlgoritmo_layout.addStretch()
        cbzAlgoritmo.setLayout(cbzAlgoritmo_layout)
        cbzTipoGrafo=QGroupBox("Selecciona el tipo de grafo")
        self.rbDirigido=QRadioButton("Grafo Dirigido")
        self.rbNoDirigido=QRadioButton("Grafo No Dirigido")
        cbzTipoGrafo_layout=QHBoxLayout()
        cbzTipoGrafo_layout.addWidget(self.rbNoDirigido)
        cbzTipoGrafo_layout.addWidget(self.rbDirigido)
        cbzTipoGrafo.setLayout(cbzTipoGrafo_layout)
        cbzBotones=QGroupBox("Selecciona una opción")
        self.rbDibNodo = QRadioButton('Dibujar Nodo')
        self.rbDibArista = QRadioButton('Dibujar Arista')
        self.btnDibujar = QPushButton('Ingresar Puntos')
        self.btnLimpiar = QPushButton('Limpiar')
        cbzBotones_layout=QHBoxLayout()
        cbzBotones_layout.addWidget(self.rbDibNodo)
        cbzBotones_layout.addWidget(self.rbDibArista)
        cbzBotones_layout.addWidget(self.btnDibujar)
        cbzBotones_layout.addWidget(self.btnLimpiar)
        cbzBotones.setLayout(cbzBotones_layout)
        self.rbDibArista.setObjectName('rbDibArista')
        self.rbDibNodo.setChecked(True)
        self.btnDibujar.setEnabled(False)
        self.rbNoDirigido.setChecked(True)
        cabezera_layout = QVBoxLayout()
        cabezera_layout.addWidget(cbzAlgoritmo)
        #cabezera_layout.addWidget(cbzTipoGrafo)
        cabezera_layout.addWidget(cbzBotones)
        cabezera.setLayout(cabezera_layout)
        cabezera.setFixedHeight(290) ### AJUSTA LA PANTALLa
        self.lienzo = Lienzo(self)
        grafoUI_layout = QVBoxLayout()
        grafoUI_layout.addWidget(self.lienzo.fig.canvas)
        grafoUI.setLayout(grafoUI_layout)
        self.setMinimumSize(self.ancho,self.alto)
        main_layout = QVBoxLayout()
        main_layout.addWidget(cabezera)
        main_layout.addWidget(grafoUI)
        self.setLayout(main_layout)
        self.rbDirigido.clicked.connect(self.setTipoGrafo)
        self.rbNoDirigido.clicked.connect(self.setTipoGrafo)
        self.rbDibArista.toggled.connect(lambda state=self.rbDibArista.isChecked(): self.onRadioButtonToggled(state))
        #self.rbNoDirigido.toggled.connect(lambda state = self.rbNoDirigido.isChecked(): self.CambioTipoGrafo(state))
        self.btnDibujar.clicked.connect(self.PideNodos)
        self.btnLimpiar.clicked.connect(self.LimpiarLienzo)
    def setTipoGrafo(self):
        pass
    def DibujaPrueba(self):
        pass
    def resizeEvent(self, event):
        pass
    def add_node(self, node):    
        pass
    def onRadioButtonToggled(self, state):
        pass
    def dibNodoIsSelected(self):
        pass
    def MouseClickArista(self, event):
        pass
    def PideNodos(self):
        pass
    def LimpiarLienzo(self):
        pass
    def GuardarImagen(self):
        pass
    def GuardarJson(self):
        pass
    def CargarJson(self):
        pass
    def hayNodos(self):
        pass
    def hayAristas(self):
        pass
    def BFS(self,inicio):
        pass
    def KRUSKAL(self):
        pass
    def DFS(self, inicio):
        pass
    def DIJKSTRA(self, inicio):
        pass
    def seleccion_recorrido(self):
        pass
class Panel(QWidget):
    def __init__(self):
        super().__init__()
        self.content=""
        self.initUI()

    def initUI(self):
        self.scrollarea = QScrollArea(self)
        self.scrollarea.setGeometry(0, 0, 300, 200)
        self.scrollarea.setWidgetResizable(False)
        self.layoutInit=QVBoxLayout()
        self.layoutInit.addWidget(self.scrollarea)
        self.setLayout(self.layoutInit)
    def setContent(self,newcontent):
        content_label=QLabel(newcontent)
        font1 = QFont()
        font1.setPointSize(12)  # Tamaño de la fuente
        content_label.setFont(font1)
        self.scrollarea.setWidget(content_label)
app = QApplication([])
window = MainWindow()
window.show()
app.exec_()