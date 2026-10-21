from collections import deque

from algoritmos.ciclos import detectar_ciclo
from algoritmos.comun import cantidad
from algoritmos.pasos import Paso


def topologico_pasos(grafo):
    """Orden topológico con el algoritmo de Kahn, paso a paso.

    Toma primero los nodos sin aristas de entrada; al procesar las aristas que salen de un nodo,
    los vecinos que se quedan sin entradas pendientes pasan a la cola (la ``frontera``). Si al
    final quedan nodos sin ordenar, el grafo tiene un ciclo y el último paso lo muestra en ``ciclo``.
    """
    if not grafo.is_directed():
        raise ValueError("El orden topológico solo aplica a grafos dirigidos.")
    pendientes = {nodo: grafo.in_degree(nodo) for nodo in grafo.nodes}
    cola = deque(nodo for nodo in grafo.nodes if pendientes[nodo] == 0)
    orden = []
    procesadas = []
    pasos = []

    def registrar(descripcion, actual=None, arista_actual=None, ciclo=()):
        pasos.append(Paso(descripcion, actual=actual, frontera=tuple(cola), visitados=frozenset(orden),
                          aristas=tuple(procesadas), arista_actual=arista_actual, ciclo=tuple(ciclo)))

    registrar(f"Nodos sin aristas de entrada: {', '.join(map(str, cola)) or 'ninguno'}. Entran a la cola.")
    while cola:
        nodo = cola.popleft()
        orden.append(nodo)
        registrar(f"Se toma el nodo {nodo}: ocupa la posición {len(orden)} del orden.", actual=nodo)
        for vecino in grafo.successors(nodo):
            pendientes[vecino] -= 1
            procesadas.append((nodo, vecino))
            if pendientes[vecino] == 0:
                cola.append(vecino)
                texto = f"el nodo {vecino} ya no tiene entradas pendientes y entra a la cola."
            else:
                texto = (f"al nodo {vecino} le quedan "
                         f"{cantidad(pendientes[vecino], 'entrada pendiente', 'entradas pendientes')}.")
            registrar(f"Se procesa la arista {nodo} → {vecino}: {texto}", actual=nodo, arista_actual=(nodo, vecino))

    if len(orden) == grafo.number_of_nodes():
        registrar(f"Orden topológico: {', '.join(map(str, orden))}.")
    else:
        ordenados = set(orden)
        restantes = [nodo for nodo in grafo.nodes if nodo not in ordenados]
        # Cada nodo restante tiene una entrada desde otro restante, así que entre ellos hay un ciclo.
        ciclo = detectar_ciclo(grafo.subgraph(restantes))
        registrar(f"No existe orden topológico: {cantidad(len(restantes), 'nodo queda', 'nodos quedan')} con "
                  f"entradas pendientes porque el grafo tiene un ciclo ({' → '.join(map(str, ciclo + ciclo[:1]))}).",
                  ciclo=list(zip(ciclo, ciclo[1:] + ciclo[:1])))
    return pasos


def orden_topologico(grafo):
    """Lista de nodos en orden topológico, o ``None`` si el grafo tiene un ciclo."""
    pasos = topologico_pasos(grafo)
    if pasos[-1].ciclo:
        return None
    # Cada paso agrega como mucho un nodo a los ya ordenados.
    orden = []
    for anterior, siguiente in zip(pasos, pasos[1:]):
        orden.extend(siguiente.visitados - anterior.visitados)
    return orden
