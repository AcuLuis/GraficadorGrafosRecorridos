import networkx as nx
import pytest

# Mismo grafo que el "Grafo de Prueba" de la aplicación.
ARISTAS_PRUEBA = [
    (1, 2, 10), (1, 7, 9), (2, 4, 5), (4, 7, 7), (1, 5, 14), (5, 6, 12),
    (1, 8, 3), (8, 6, 15), (4, 8, 9), (4, 6, 1), (3, 6, 4), (3, 8, 6),
    (3, 5, 6), (3, 4, 5), (2, 3, 3), (2, 5, 2), (1, 3, 6),
]


def construir(aristas, dirigido=False, nodos_extra=()):
    grafo = nx.DiGraph() if dirigido else nx.Graph()
    grafo.add_nodes_from(nodos_extra)
    grafo.add_weighted_edges_from(aristas)
    return grafo


def invariantes_comunes(pasos):
    """Propiedades que cumplen los pasos de todos los algoritmos."""
    assert pasos, "debe haber al menos un paso"
    for paso in pasos:
        assert paso.descripcion
        assert paso.actual not in paso.frontera
        assert not set(paso.frontera) & paso.visitados
    for anterior, siguiente in zip(pasos, pasos[1:]):
        assert anterior.visitados <= siguiente.visitados


@pytest.fixture
def grafo_prueba():
    return construir(ARISTAS_PRUEBA)


@pytest.fixture
def grafo_dirigido():
    # 1 -> 2 -> 3, 2 -> 1 con otro peso, 4 -> 1 (4 no es alcanzable desde 1)
    return construir([(1, 2, 1), (2, 3, 1), (2, 1, 5), (4, 1, 1)], dirigido=True)
