from algoritmos.comun import cantidad, peso
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


def kruskal(grafo):
    """Aristas del árbol de expansión mínima como ``(origen, destino, peso)``, en el orden en que se agregan."""
    return [(origen, destino, peso(grafo, origen, destino)) for origen, destino in kruskal_pasos(grafo)[-1].aristas]
