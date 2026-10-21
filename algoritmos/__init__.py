"""Algoritmos de grafos implementados como funciones puras sobre grafos de NetworkX.

Ninguna función modifica el grafo recibido ni depende de la interfaz gráfica.
Los errores de uso (nodo inexistente, tipo de grafo no válido, pesos negativos)
se informan con ``ValueError`` y un mensaje listo para mostrar al usuario.
"""
from algoritmos.arbol_minimo import kruskal
from algoritmos.camino_minimo import dijkstra
from algoritmos.recorridos import bfs, dfs

__all__ = ["bfs", "dfs", "kruskal", "dijkstra"]
