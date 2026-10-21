import random

import networkx as nx

MAXIMO_NODOS = 100
MARGEN = 0.08  # distancia mínima de los nodos al borde del área de dibujo


def maximo_de_aristas(cantidad_nodos, dirigido):
    return cantidad_nodos * (cantidad_nodos - 1) // (1 if dirigido else 2)


def grafo_aleatorio(cantidad_nodos, cantidad_aristas, peso_minimo=1, peso_maximo=10, dirigido=False, conexo=True,
                    semilla=None):
    """Grafo con nodos ``1..cantidad_nodos``, ``cantidad_aristas`` aristas al azar y pesos enteros al azar.

    Si ``conexo`` es verdadero, primero se arma un árbol al azar que une todos los nodos (en un
    grafo dirigido, todos quedan alcanzables desde uno de ellos) y después se agregan las demás aristas.
    """
    if not 1 <= cantidad_nodos <= MAXIMO_NODOS:
        raise ValueError(f"La cantidad de nodos debe estar entre 1 y {MAXIMO_NODOS}.")
    maximo = maximo_de_aristas(cantidad_nodos, dirigido)
    if not 0 <= cantidad_aristas <= maximo:
        raise ValueError(f"Con {cantidad_nodos} nodos se pueden crear como máximo {maximo} aristas.")
    if conexo and cantidad_aristas < cantidad_nodos - 1:
        raise ValueError(f"Un grafo conexo de {cantidad_nodos} nodos necesita al menos {cantidad_nodos - 1} aristas.")
    if peso_minimo > peso_maximo:
        raise ValueError("El peso mínimo no puede ser mayor que el peso máximo.")

    azar = random.Random(semilla)
    grafo = nx.DiGraph() if dirigido else nx.Graph()
    nodos = list(range(1, cantidad_nodos + 1))
    grafo.add_nodes_from(nodos)

    def agregar(origen, destino):
        grafo.add_edge(origen, destino, weight=azar.randint(peso_minimo, peso_maximo))

    if conexo:
        orden = nodos[:]
        azar.shuffle(orden)
        for indice in range(1, len(orden)):
            agregar(orden[azar.randrange(indice)], orden[indice])
    posibles = [(origen, destino) for origen in nodos for destino in nodos
                if origen != destino and (dirigido or origen < destino) and not grafo.has_edge(origen, destino)]
    azar.shuffle(posibles)
    for origen, destino in posibles[:cantidad_aristas - grafo.number_of_edges()]:
        agregar(origen, destino)
    return grafo


def distribuir(grafo, semilla=0):
    """Posiciones dentro del área de dibujo para los nodos de ``grafo``, con el layout de fuerzas de NetworkX."""
    if grafo.number_of_nodes() == 0:
        return {}
    if grafo.number_of_nodes() == 1:
        return {nodo: (0.5, 0.5) for nodo in grafo.nodes}
    crudas = nx.spring_layout(grafo, seed=semilla)
    return dict(zip(crudas, zip(*(_reescalar([posicion[eje] for posicion in crudas.values()]) for eje in (0, 1)))))


def _reescalar(valores):
    minimo, maximo = min(valores), max(valores)
    if maximo - minimo < 1e-9:
        return [0.5] * len(valores)
    return [MARGEN + (1 - 2 * MARGEN) * (float(valor) - minimo) / (maximo - minimo) for valor in valores]
