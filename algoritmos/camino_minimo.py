import heapq
import itertools
import math

from algoritmos.comun import peso, validar_inicio


def dijkstra(grafo, inicio):
    """Caminos mínimos desde ``inicio``.

    Devuelve ``(distancias, aristas)``: la distancia a cada nodo (``math.inf`` si es
    inalcanzable) y las aristas del árbol de caminos mínimos como ``(origen, destino, peso)``.
    """
    validar_inicio(grafo, inicio)
    if any(peso(grafo, origen, destino) < 0 for origen, destino in grafo.edges):
        raise ValueError("Dijkstra requiere pesos no negativos.")
    distancias = {nodo: math.inf for nodo in grafo.nodes}
    distancias[inicio] = 0
    padre = {}
    visitados = set()
    desempate = itertools.count()
    cola = [(0, next(desempate), inicio)]
    while cola:
        distancia, _, nodo = heapq.heappop(cola)
        if nodo in visitados:
            continue
        visitados.add(nodo)
        for vecino in grafo.neighbors(nodo):
            nueva_distancia = distancia + peso(grafo, nodo, vecino)
            if nueva_distancia < distancias[vecino]:
                distancias[vecino] = nueva_distancia
                padre[vecino] = nodo
                heapq.heappush(cola, (nueva_distancia, next(desempate), vecino))
    aristas = [(origen, destino, peso(grafo, origen, destino)) for destino, origen in padre.items()]
    return distancias, aristas
