from collections import deque

from algoritmos.comun import cantidad, validar_inicio
from algoritmos.pasos import Paso


def bfs_pasos(grafo, inicio):
    """Búsqueda en anchura desde ``inicio``, paso a paso.

    En grafos dirigidos solo se siguen las aristas salientes. La ``frontera`` de cada paso
    es la cola; el último paso contiene todas las aristas del recorrido.
    """
    validar_inicio(grafo, inicio)
    pasos = []
    descubiertos = {inicio}
    procesados = set()
    cola = deque([inicio])
    aristas = []

    def registrar(descripcion, actual=None, arista_actual=None):
        pasos.append(Paso(descripcion, actual=actual, frontera=tuple(cola), visitados=frozenset(procesados),
                          aristas=tuple(aristas), arista_actual=arista_actual))

    registrar(f"Se agrega el nodo inicial {inicio} a la cola.")
    while cola:
        nodo = cola.popleft()
        registrar(f"Se saca el nodo {nodo} de la cola y se revisan sus vecinos.", actual=nodo)
        for vecino in grafo.neighbors(nodo):
            if vecino not in descubiertos:
                descubiertos.add(vecino)
                aristas.append((nodo, vecino))
                cola.append(vecino)
                registrar(f"Se descubre el nodo {vecino} desde el nodo {nodo} y se agrega a la cola.",
                          actual=nodo, arista_actual=(nodo, vecino))
        procesados.add(nodo)
    registrar(f"Fin del recorrido: se alcanzaron {cantidad(len(procesados), 'nodo', 'nodos')}.")
    return pasos


def dfs_pasos(grafo, inicio):
    """Búsqueda en profundidad desde ``inicio``, paso a paso.

    Usa una pila explícita para no depender del límite de recursión de Python, pero recorre
    en el mismo orden que la versión recursiva. La ``frontera`` de cada paso es la pila.
    """
    validar_inicio(grafo, inicio)
    pasos = []
    visitados = {inicio}
    terminados = set()
    aristas = []
    pila = [(inicio, iter(grafo.neighbors(inicio)))]

    def registrar(descripcion, actual, arista_actual=None):
        pasos.append(Paso(descripcion, actual=actual, frontera=tuple(nodo for nodo, _ in pila if nodo != actual),
                          visitados=frozenset(terminados), aristas=tuple(aristas), arista_actual=arista_actual))

    registrar(f"Se comienza en el nodo {inicio}.", inicio)
    while pila:
        nodo, vecinos = pila[-1]
        for vecino in vecinos:
            if vecino not in visitados:
                visitados.add(vecino)
                aristas.append((nodo, vecino))
                pila.append((vecino, iter(grafo.neighbors(vecino))))
                registrar(f"Se avanza del nodo {nodo} al nodo {vecino}.", vecino, (nodo, vecino))
                break
        else:
            pila.pop()
            terminados.add(nodo)
            if pila:
                anterior = pila[-1][0]
                registrar(f"El nodo {nodo} no tiene vecinos sin visitar; se retrocede al nodo {anterior}.", anterior)
    registrar(f"Fin del recorrido: se alcanzaron {cantidad(len(terminados), 'nodo', 'nodos')}.", None)
    return pasos


def bfs(grafo, inicio):
    """Aristas ``(padre, hijo)`` de la búsqueda en anchura, en el orden en que se descubre cada nodo."""
    return list(bfs_pasos(grafo, inicio)[-1].aristas)


def dfs(grafo, inicio):
    """Aristas ``(padre, hijo)`` de la búsqueda en profundidad, en el orden en que se visita cada nodo."""
    return list(dfs_pasos(grafo, inicio)[-1].aristas)
