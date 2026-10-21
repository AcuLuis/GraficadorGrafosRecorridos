from collections import deque

from algoritmos.comun import validar_inicio


def bfs(grafo, inicio):
    """Búsqueda en anchura desde ``inicio``.

    Devuelve las aristas ``(padre, hijo)`` en el orden en que se descubre cada nodo.
    En grafos dirigidos solo se siguen las aristas salientes.
    """
    validar_inicio(grafo, inicio)
    visitados = {inicio}
    cola = deque([inicio])
    aristas = []
    while cola:
        nodo = cola.popleft()
        for vecino in grafo.neighbors(nodo):
            if vecino not in visitados:
                visitados.add(vecino)
                aristas.append((nodo, vecino))
                cola.append(vecino)
    return aristas


def dfs(grafo, inicio):
    """Búsqueda en profundidad desde ``inicio``.

    Devuelve las aristas ``(padre, hijo)`` en el mismo orden que la versión recursiva,
    pero usa una pila explícita para no depender del límite de recursión de Python.
    """
    validar_inicio(grafo, inicio)
    visitados = {inicio}
    aristas = []
    pila = [(inicio, iter(grafo.neighbors(inicio)))]
    while pila:
        nodo, vecinos = pila[-1]
        for vecino in vecinos:
            if vecino not in visitados:
                visitados.add(vecino)
                aristas.append((nodo, vecino))
                pila.append((vecino, iter(grafo.neighbors(vecino))))
                break
        else:
            pila.pop()
    return aristas
