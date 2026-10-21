"""Algoritmos de grafos implementados como funciones puras sobre grafos de NetworkX.

Ninguna función modifica el grafo recibido ni depende de la interfaz gráfica.
Los errores de uso (nodo inexistente, tipo de grafo no válido, pesos negativos)
se informan con ``ValueError`` y un mensaje listo para mostrar al usuario.

Cada algoritmo tiene una versión ``*_pasos`` que devuelve la lista de ``Paso`` con el
estado después de cada paso; el resultado final es siempre el del último paso.
"""
from algoritmos.arbol_minimo import kruskal, kruskal_pasos, prim, prim_pasos
from algoritmos.camino_minimo import camino_minimo, dijkstra, dijkstra_pasos
from algoritmos.pasos import Paso
from algoritmos.recorridos import bfs, bfs_pasos, dfs, dfs_pasos

__all__ = [
    "Paso",
    "bfs", "bfs_pasos",
    "dfs", "dfs_pasos",
    "kruskal", "kruskal_pasos",
    "prim", "prim_pasos",
    "dijkstra", "dijkstra_pasos", "camino_minimo",
]
