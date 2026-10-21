import ast
import json

import networkx as nx

COLOR_POR_DEFECTO = "black"


class ModeloGrafo:
    """Estado del grafo que se edita: estructura, posición de cada nodo y color de cada arista.

    No depende de la interfaz gráfica. Los errores de uso se informan con ``ValueError``
    y un mensaje listo para mostrar al usuario; en ese caso el estado no cambia.
    """

    def __init__(self, dirigido=False):
        self.grafo = nx.DiGraph() if dirigido else nx.Graph()
        self.posiciones = {}
        self.colores = {}

    @property
    def dirigido(self):
        return self.grafo.is_directed()

    def tiene_aristas(self):
        return self.grafo.number_of_edges() > 0

    def cambiar_tipo(self, dirigido):
        """Cambia entre grafo dirigido y no dirigido. El grafo queda vacío."""
        self._reemplazar(ModeloGrafo(dirigido))

    def limpiar(self):
        self.grafo.clear()
        self.posiciones.clear()
        self.colores.clear()

    # Edición

    def siguiente_id(self):
        return max(self.grafo.nodes, default=0) + 1

    def agregar_nodo(self, x, y):
        nodo = self.siguiente_id()
        self.grafo.add_node(nodo)
        self.posiciones[nodo] = (x, y)
        return nodo

    def agregar_arista(self, origen, destino, peso=1):
        if origen == destino:
            raise ValueError("Una arista debe unir dos nodos distintos.")
        faltantes = [nodo for nodo in (origen, destino) if nodo not in self.grafo]
        if len(faltantes) == 2:
            raise ValueError("Los nodos no se encuentran.")
        if faltantes:
            raise ValueError(f"El nodo {faltantes[0]} no se encuentra.")
        self.grafo.add_edge(origen, destino, weight=peso)

    def eliminar_nodo(self, nodo):
        if nodo not in self.grafo:
            raise ValueError("El nodo no existe en el grafo.")
        self.grafo.remove_node(nodo)
        self.posiciones.pop(nodo, None)
        self.colores = {arista: color for arista, color in self.colores.items() if nodo not in arista}

    # Colores

    def color_arista(self, origen, destino):
        if not self.dirigido and (origen, destino) not in self.colores:
            return self.colores.get((destino, origen), COLOR_POR_DEFECTO)
        return self.colores.get((origen, destino), COLOR_POR_DEFECTO)

    def pintar_aristas(self, aristas, color):
        for origen, destino in aristas:
            self.colores[(origen, destino)] = color
            if not self.dirigido:
                self.colores[(destino, origen)] = color

    def reiniciar_colores(self):
        self.colores.clear()

    def conservar_aristas(self, color):
        """Elimina todas las aristas que no tienen ``color``."""
        aristas = list(self.grafo.edges)
        sobrantes = [arista for arista in aristas if self.color_arista(*arista) != color]
        if len(sobrantes) == len(aristas):
            raise ValueError("Primero ejecuta un algoritmo para obtener un recorrido.")
        self.grafo.remove_edges_from(sobrantes)

    # Persistencia

    def a_dict(self):
        return {
            "nodes": list(self.grafo.nodes),
            "edges": list(self.grafo.edges(data=True)),
            "pos": {str(nodo): list(posicion) for nodo, posicion in self.posiciones.items()},
            "edge_colors": {str(arista): color for arista, color in self.colores.items()},
            "graph_type": "Directed" if self.dirigido else "Undirected",
        }

    def cargar_dict(self, datos):
        try:
            nuevo = ModeloGrafo(datos.get("graph_type") == "Directed")
            nuevo.grafo.add_nodes_from(datos.get("nodes", []))
            nuevo.grafo.add_edges_from(datos.get("edges", []))
            nuevo.posiciones = {ast.literal_eval(nodo): tuple(posicion) for nodo, posicion in datos.get("pos", {}).items()}
            nuevo.colores = {ast.literal_eval(arista): color for arista, color in datos.get("edge_colors", {}).items()}
        except (ValueError, SyntaxError, TypeError, AttributeError, nx.NetworkXError) as error:
            raise ValueError(f"Formato de grafo inválido: {error}") from error
        sin_posicion = [nodo for nodo in nuevo.grafo.nodes if nodo not in nuevo.posiciones]
        if sin_posicion:
            raise ValueError(f"Nodos sin posición: {sin_posicion}")
        self._reemplazar(nuevo)

    def guardar_json(self, ruta):
        with open(ruta, "w", encoding="utf-8") as archivo:
            json.dump(self.a_dict(), archivo, indent=2)

    def cargar_json(self, ruta):
        with open(ruta, encoding="utf-8") as archivo:
            datos = json.load(archivo)
        self.cargar_dict(datos)

    def cargar_texto(self, ruta_nodos, ruta_aristas):
        """Carga el formato de texto del grafo de prueba.

        Cada línea es una tupla: ``(id, x, y)`` en el archivo de nodos y
        ``(origen, destino, peso)`` en el de aristas. Mantiene el tipo de grafo actual.
        """
        nuevo = ModeloGrafo(self.dirigido)
        try:
            for nodo, x, y in _leer_tuplas(ruta_nodos):
                nuevo.grafo.add_node(nodo)
                nuevo.posiciones[nodo] = (x, y)
            for origen, destino, peso in _leer_tuplas(ruta_aristas):
                nuevo.agregar_arista(origen, destino, peso)
        except (SyntaxError, TypeError) as error:
            raise ValueError(f"Formato de grafo inválido: {error}") from error
        self._reemplazar(nuevo)

    def _reemplazar(self, otro):
        self.grafo, self.posiciones, self.colores = otro.grafo, otro.posiciones, otro.colores


def _leer_tuplas(ruta):
    with open(ruta, encoding="utf-8") as archivo:
        return [ast.literal_eval(linea) for linea in archivo if linea.strip()]
