from algoritmos.comun import peso


def kruskal(grafo):
    """Árbol de expansión mínima (bosque, si el grafo no es conexo).

    Devuelve las aristas elegidas como ``(origen, destino, peso)`` en el orden en que se agregan.
    """
    if grafo.is_directed():
        raise ValueError("Kruskal solo aplica a grafos no dirigidos.")
    representante = {nodo: nodo for nodo in grafo.nodes}

    def raiz(nodo):
        while representante[nodo] != nodo:
            representante[nodo] = representante[representante[nodo]]
            nodo = representante[nodo]
        return nodo

    elegidas = []
    for origen, destino in sorted(grafo.edges, key=lambda arista: peso(grafo, *arista)):
        raiz_origen, raiz_destino = raiz(origen), raiz(destino)
        if raiz_origen != raiz_destino:
            representante[raiz_origen] = raiz_destino
            elegidas.append((origen, destino, peso(grafo, origen, destino)))
    return elegidas
