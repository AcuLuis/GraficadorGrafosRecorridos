import heapq
import itertools
import math

from algoritmos.comun import cantidad, formatear_distancia, peso, validar_inicio
from algoritmos.pasos import Paso


def dijkstra_pasos(grafo, inicio, destino=None):
    """Caminos mínimos desde ``inicio``, paso a paso.

    Sin ``destino`` calcula la distancia a todos los nodos y el último paso contiene el árbol
    de caminos mínimos. Con ``destino`` se detiene al fijar ese nodo y el último paso contiene
    solo las aristas del camino. La ``frontera`` es la cola de prioridad, ordenada por distancia.
    """
    validar_inicio(grafo, inicio)
    if destino is not None:
        validar_inicio(grafo, destino)
    if any(peso(grafo, origen, fin) < 0 for origen, fin in grafo.edges):
        raise ValueError("Dijkstra requiere pesos no negativos.")
    distancias = {nodo: math.inf for nodo in grafo.nodes}
    distancias[inicio] = 0
    anteriores = {}
    fijados = set()
    desempate = itertools.count()
    cola = [(0, next(desempate), inicio)]
    pasos = []

    def en_espera():
        return tuple(dict.fromkeys(nodo for _, _, nodo in sorted(cola) if nodo not in fijados))

    def registrar(descripcion, actual=None, arista_actual=None, aristas=None):
        if aristas is None:
            aristas = [(origen, fin) for fin, origen in anteriores.items()]
        pasos.append(Paso(descripcion, actual=actual, frontera=en_espera(), visitados=frozenset(fijados),
                          aristas=tuple(aristas), arista_actual=arista_actual,
                          distancias=dict(distancias), anteriores=dict(anteriores)))

    registrar(f"La distancia al nodo inicial {inicio} es 0; los demás nodos empiezan en ∞.")
    while cola:
        distancia, _, nodo = heapq.heappop(cola)
        if nodo in fijados:
            continue
        fijados.add(nodo)
        registrar(f"Se fija el nodo {nodo} con distancia {distancia}.", actual=nodo)
        if nodo == destino:
            break
        for vecino in grafo.neighbors(nodo):
            if vecino in fijados:
                continue
            nueva_distancia = distancia + peso(grafo, nodo, vecino)
            if nueva_distancia < distancias[vecino]:
                anterior = distancias[vecino]
                distancias[vecino] = nueva_distancia
                anteriores[vecino] = nodo
                heapq.heappush(cola, (nueva_distancia, next(desempate), vecino))
                registrar(f"Se actualiza la distancia del nodo {vecino}: {formatear_distancia(anterior)} → "
                          f"{nueva_distancia} (vía el nodo {nodo}).", actual=nodo, arista_actual=(nodo, vecino))

    if destino is None:
        registrar(f"Fin: se calcularon las distancias mínimas a {cantidad(len(fijados), 'nodo', 'nodos')}.")
    elif destino not in fijados:
        registrar(f"No hay camino del nodo {inicio} al nodo {destino}.", aristas=())
    else:
        camino = [destino]
        while camino[-1] != inicio:
            camino.append(anteriores[camino[-1]])
        camino.reverse()
        registrar(f"Camino más corto: {' → '.join(map(str, camino))}, costo {distancias[destino]}.",
                  aristas=list(zip(camino, camino[1:])))
    return pasos


def dijkstra(grafo, inicio):
    """Caminos mínimos desde ``inicio``.

    Devuelve ``(distancias, aristas)``: la distancia a cada nodo (``math.inf`` si es
    inalcanzable) y las aristas del árbol de caminos mínimos como ``(origen, destino, peso)``.
    """
    final = dijkstra_pasos(grafo, inicio)[-1]
    return final.distancias, [(origen, destino, peso(grafo, origen, destino)) for origen, destino in final.aristas]


def camino_minimo(grafo, inicio, destino):
    """Devuelve ``(costo, camino)`` del camino más corto, o ``(math.inf, None)`` si no hay camino."""
    final = dijkstra_pasos(grafo, inicio, destino)[-1]
    if final.distancias[destino] == math.inf:
        return math.inf, None
    return final.distancias[destino], [inicio] + [fin for _, fin in final.aristas]
