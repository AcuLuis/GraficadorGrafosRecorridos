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
        raise ValueError("Dijkstra requiere pesos no negativos; para pesos negativos usa Bellman-Ford.")
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

    _registrar_final(registrar, distancias, anteriores, inicio, destino, alcanzados=len(fijados))
    return pasos


def bellman_ford_pasos(grafo, inicio, destino=None):
    """Caminos mínimos desde ``inicio`` con Bellman-Ford, paso a paso. Admite pesos negativos.

    Revisa todas las aristas en rondas (como máximo una menos que la cantidad de nodos) y se
    detiene antes si una ronda no cambia ninguna distancia. En grafos no dirigidos cada arista
    se recorre en ambos sentidos, así que una arista de peso negativo ya forma un ciclo negativo.
    Si hay un ciclo negativo alcanzable desde ``inicio``, el último paso lo muestra en ``ciclo``
    y no tiene aristas de camino: con ese ciclo no existen caminos mínimos.
    """
    validar_inicio(grafo, inicio)
    if destino is not None:
        validar_inicio(grafo, destino)
    arcos = list(grafo.edges)
    if not grafo.is_directed():
        arcos += [(fin, origen) for origen, fin in arcos]
    distancias = {nodo: math.inf for nodo in grafo.nodes}
    distancias[inicio] = 0
    anteriores = {}
    pasos = []

    def registrar(descripcion, actual=None, arista_actual=None, aristas=None, ciclo=()):
        if aristas is None:
            aristas = [(origen, fin) for fin, origen in anteriores.items()]
        alcanzados = frozenset(nodo for nodo, distancia in distancias.items() if distancia != math.inf)
        pasos.append(Paso(descripcion, actual=actual, visitados=alcanzados, aristas=tuple(aristas),
                          arista_actual=arista_actual, distancias=dict(distancias), anteriores=dict(anteriores),
                          ciclo=tuple(ciclo)))

    registrar(f"La distancia al nodo inicial {inicio} es 0; los demás nodos empiezan en ∞.")
    rondas = grafo.number_of_nodes() - 1
    for ronda in range(1, rondas + 1):
        registrar(f"Ronda {ronda} de {rondas}: se revisan todas las aristas.")
        hubo_cambios = False
        for origen, fin in arcos:
            if distancias[origen] == math.inf:
                continue
            nueva_distancia = distancias[origen] + peso(grafo, origen, fin)
            if nueva_distancia < distancias[fin]:
                anterior = distancias[fin]
                distancias[fin] = nueva_distancia
                anteriores[fin] = origen
                hubo_cambios = True
                registrar(f"Se actualiza la distancia del nodo {fin}: {formatear_distancia(anterior)} → "
                          f"{nueva_distancia} (vía el nodo {origen}).", actual=origen, arista_actual=(origen, fin))
        if not hubo_cambios:
            registrar(f"La ronda {ronda} no cambió ninguna distancia: ya son definitivas.")
            break
    else:
        # Si después de todas las rondas aún se puede mejorar una distancia, hay un ciclo negativo.
        for origen, fin in arcos:
            if distancias[origen] != math.inf and distancias[origen] + peso(grafo, origen, fin) < distancias[fin]:
                ciclo = _ciclo_negativo(anteriores, origen, fin, grafo.number_of_nodes())
                texto = " → ".join(map(str, ciclo + ciclo[:1])) if ciclo else f"pasa por la arista {origen}-{fin}"
                registrar(f"Hay un ciclo de peso negativo alcanzable desde el nodo {inicio} ({texto}): "
                          f"no existen caminos mínimos.", arista_actual=(origen, fin), aristas=(),
                          ciclo=list(zip(ciclo, ciclo[1:] + ciclo[:1])))
                return pasos

    alcanzados = sum(1 for distancia in distancias.values() if distancia != math.inf)
    _registrar_final(registrar, distancias, anteriores, inicio, destino, alcanzados)
    return pasos


def _registrar_final(registrar, distancias, anteriores, inicio, destino, alcanzados):
    if destino is None:
        registrar(f"Fin: se calcularon las distancias mínimas a {cantidad(alcanzados, 'nodo', 'nodos')}.")
    elif distancias[destino] == math.inf:
        registrar(f"No hay camino del nodo {inicio} al nodo {destino}.", aristas=())
    else:
        camino = [destino]
        while camino[-1] != inicio:
            camino.append(anteriores[camino[-1]])
        camino.reverse()
        registrar(f"Camino más corto: {' → '.join(map(str, camino))}, costo {distancias[destino]}.",
                  aristas=list(zip(camino, camino[1:])))


def _ciclo_negativo(anteriores, origen, fin, cantidad_nodos):
    """Nodos de un ciclo negativo, en orden, a partir de una arista que todavía mejora una distancia.

    Retroceder tantas veces como nodos hay por los predecesores garantiza caer dentro del ciclo.
    """
    anteriores = {**anteriores, fin: origen}
    nodo = fin
    for _ in range(cantidad_nodos):
        if nodo not in anteriores:
            return []
        nodo = anteriores[nodo]
    ciclo = [nodo]
    siguiente = anteriores[nodo]
    while siguiente != nodo:
        ciclo.append(siguiente)
        siguiente = anteriores[siguiente]
    ciclo.reverse()
    return ciclo


def dijkstra(grafo, inicio):
    """Caminos mínimos desde ``inicio``.

    Devuelve ``(distancias, aristas)``: la distancia a cada nodo (``math.inf`` si es
    inalcanzable) y las aristas del árbol de caminos mínimos como ``(origen, destino, peso)``.
    """
    final = dijkstra_pasos(grafo, inicio)[-1]
    return final.distancias, [(origen, destino, peso(grafo, origen, destino)) for origen, destino in final.aristas]


def bellman_ford(grafo, inicio):
    """Como ``dijkstra``, pero admite pesos negativos. Si hay un ciclo negativo alcanzable lanza ``ValueError``."""
    final = bellman_ford_pasos(grafo, inicio)[-1]
    if final.ciclo:
        raise ValueError(final.descripcion)
    return final.distancias, [(origen, destino, peso(grafo, origen, destino)) for origen, destino in final.aristas]


def camino_minimo(grafo, inicio, destino):
    """Devuelve ``(costo, camino)`` del camino más corto, o ``(math.inf, None)`` si no hay camino."""
    final = dijkstra_pasos(grafo, inicio, destino)[-1]
    if final.distancias[destino] == math.inf:
        return math.inf, None
    return final.distancias[destino], [inicio] + [fin for _, fin in final.aristas]
