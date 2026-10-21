from algoritmos.pasos import Paso


def detectar_ciclo_pasos(grafo):
    """Busca un ciclo con una búsqueda en profundidad que recorre todo el grafo, paso a paso.

    En grafos dirigidos hay un ciclo si se llega a un nodo que todavía está en el camino actual;
    en no dirigidos, si se llega a un nodo ya visitado que no es el padre. La ``frontera`` es el
    camino actual. Si se encuentra un ciclo, el último paso lo muestra en ``ciclo``.
    """
    dirigido = grafo.is_directed()
    visitados = set()
    terminados = set()
    aristas = []
    pila = []  # (nodo, padre, vecinos por revisar)
    pasos = []

    def registrar(descripcion, actual=None, arista_actual=None, ciclo=()):
        pasos.append(Paso(descripcion, actual=actual, frontera=tuple(nodo for nodo, _, _ in pila if nodo != actual),
                          visitados=frozenset(terminados), aristas=tuple(aristas), arista_actual=arista_actual,
                          ciclo=tuple(ciclo)))

    for raiz in grafo.nodes:
        if raiz in visitados:
            continue
        visitados.add(raiz)
        pila.append((raiz, None, iter(grafo.neighbors(raiz))))
        registrar(f"Se comienza una búsqueda en el nodo {raiz}.", actual=raiz)
        while pila:
            nodo, padre, vecinos = pila[-1]
            for vecino in vecinos:
                if (not dirigido and vecino == padre) or vecino in terminados:
                    continue
                if vecino in visitados:
                    camino = [nodo_en_camino for nodo_en_camino, _, _ in pila]
                    nodos_ciclo = camino[camino.index(vecino):]
                    ciclo = list(zip(nodos_ciclo, nodos_ciclo[1:])) + [(nodo, vecino)]
                    registrar(f"Ciclo encontrado: {' → '.join(map(str, nodos_ciclo + [vecino]))}.",
                              actual=nodo, arista_actual=(nodo, vecino), ciclo=ciclo)
                    return pasos
                visitados.add(vecino)
                aristas.append((nodo, vecino))
                pila.append((vecino, nodo, iter(grafo.neighbors(vecino))))
                registrar(f"Se avanza del nodo {nodo} al nodo {vecino}.", actual=vecino, arista_actual=(nodo, vecino))
                break
            else:
                pila.pop()
                terminados.add(nodo)
                registrar(f"Desde el nodo {nodo} no se llega a ningún ciclo; se marca como terminado.",
                          actual=pila[-1][0] if pila else None)
    registrar("El grafo no tiene ciclos: es un grafo acíclico dirigido (DAG)." if dirigido
              else "El grafo no tiene ciclos: es un bosque.")
    return pasos


def detectar_ciclo(grafo):
    """Nodos de un ciclo en orden (el último se une con el primero), o ``None`` si el grafo no tiene ciclos."""
    ciclo = detectar_ciclo_pasos(grafo)[-1].ciclo
    return [origen for origen, _ in ciclo] if ciclo else None
