import heapq
import itertools

from algoritmos.comun import cantidad, peso, validar_inicio
from algoritmos.pasos import Paso


def kruskal_pasos(grafo):
    """Árbol de expansión mínima (bosque, si el grafo no es conexo), paso a paso.

    Las aristas se examinan de menor a mayor peso; las que formarían un ciclo quedan en
    ``descartadas``. Se detiene en cuanto el árbol tiene una arista menos que nodos.
    """
    if grafo.is_directed():
        raise ValueError("Kruskal solo aplica a grafos no dirigidos.")
    representante = {nodo: nodo for nodo in grafo.nodes}

    def raiz(nodo):
        while representante[nodo] != nodo:
            representante[nodo] = representante[representante[nodo]]
            nodo = representante[nodo]
        return nodo

    pasos = []
    elegidas = []
    descartadas = []
    en_arbol = set()

    def registrar(descripcion, arista_actual=None):
        pasos.append(Paso(descripcion, visitados=frozenset(en_arbol), aristas=tuple(elegidas),
                          arista_actual=arista_actual, descartadas=tuple(descartadas)))

    ordenadas = sorted(grafo.edges, key=lambda arista: peso(grafo, *arista))
    registrar(f"Se ordenan las {cantidad(len(ordenadas), 'arista', 'aristas')} por peso, de menor a mayor.")
    aristas_necesarias = grafo.number_of_nodes() - 1
    for origen, destino in ordenadas:
        if len(elegidas) == aristas_necesarias:
            break
        peso_arista = peso(grafo, origen, destino)
        raiz_origen, raiz_destino = raiz(origen), raiz(destino)
        if raiz_origen != raiz_destino:
            representante[raiz_origen] = raiz_destino
            elegidas.append((origen, destino))
            en_arbol.update((origen, destino))
            registrar(f"Se agrega la arista {origen}-{destino} (peso {peso_arista}).", (origen, destino))
        else:
            descartadas.append((origen, destino))
            registrar(f"Se descarta la arista {origen}-{destino} (peso {peso_arista}): formaría un ciclo.",
                      (origen, destino))
    total = sum(peso(grafo, *arista) for arista in elegidas)
    tipo = "Árbol" if len(elegidas) == aristas_necesarias else "Bosque (el grafo no es conexo)"
    registrar(f"{tipo} de expansión mínima: {cantidad(len(elegidas), 'arista', 'aristas')}, peso total {total}.")
    return pasos


def prim_pasos(grafo, inicio):
    """Árbol de expansión mínima con el algoritmo de Prim, paso a paso.

    El árbol crece desde ``inicio`` agregando siempre la arista más liviana que sale de él.
    Si el grafo no es conexo, solo cubre el componente de ``inicio``. La ``frontera`` son los
    nodos candidatos (alcanzables por una arista desde el árbol), del más cercano al más lejano.
    """
    if grafo.is_directed():
        raise ValueError("Prim solo aplica a grafos no dirigidos.")
    validar_inicio(grafo, inicio)
    en_arbol = {inicio}
    elegidas = []
    descartadas = []
    desempate = itertools.count()
    candidatas = []
    pasos = []

    def agregar_candidatas(nodo):
        for vecino in grafo.neighbors(nodo):
            if vecino not in en_arbol:
                heapq.heappush(candidatas, (peso(grafo, nodo, vecino), next(desempate), nodo, vecino))

    def registrar(descripcion, actual=None, arista_actual=None):
        frontera = dict.fromkeys(fin for _, _, _, fin in sorted(candidatas) if fin not in en_arbol)
        pasos.append(Paso(descripcion, actual=actual, frontera=tuple(frontera), visitados=frozenset(en_arbol),
                          aristas=tuple(elegidas), arista_actual=arista_actual, descartadas=tuple(descartadas)))

    agregar_candidatas(inicio)
    registrar(f"El árbol comienza en el nodo {inicio}.", actual=inicio)
    while candidatas:
        peso_arista, _, origen, destino = heapq.heappop(candidatas)
        if destino in en_arbol:
            descartadas.append((origen, destino))
            registrar(f"Se descarta la arista {origen}-{destino} (peso {peso_arista}): "
                      f"ambos nodos ya están en el árbol.", arista_actual=(origen, destino))
            continue
        en_arbol.add(destino)
        elegidas.append((origen, destino))
        agregar_candidatas(destino)
        registrar(f"Se agrega la arista {origen}-{destino} (peso {peso_arista}), la más liviana que sale del árbol.",
                  actual=destino, arista_actual=(origen, destino))
    total = sum(peso(grafo, *arista) for arista in elegidas)
    resumen = f"Árbol de expansión mínima: {cantidad(len(elegidas), 'arista', 'aristas')}, peso total {total}."
    if len(en_arbol) < grafo.number_of_nodes():
        resumen += f" El grafo no es conexo: el árbol solo cubre el componente del nodo {inicio}."
    registrar(resumen)
    return pasos


def kruskal(grafo):
    """Aristas del árbol de expansión mínima como ``(origen, destino, peso)``, en el orden en que se agregan."""
    return [(origen, destino, peso(grafo, origen, destino)) for origen, destino in kruskal_pasos(grafo)[-1].aristas]


def prim(grafo, inicio):
    """Aristas del árbol de expansión mínima de Prim como ``(origen, destino, peso)``, en el orden en que se agregan."""
    return [(origen, destino, peso(grafo, origen, destino)) for origen, destino in prim_pasos(grafo, inicio)[-1].aristas]
