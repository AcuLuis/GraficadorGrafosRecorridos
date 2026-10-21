"""Orden topológico y detección de ciclos."""
import networkx as nx
import pytest

from algoritmos import detectar_ciclo, detectar_ciclo_pasos, orden_topologico, topologico_pasos
from conftest import construir, invariantes_comunes


def grafos_aleatorios(dirigido):
    for semilla in range(25):
        aleatorio = nx.gnp_random_graph(7, 0.25, seed=semilla, directed=dirigido)
        grafo = nx.DiGraph() if dirigido else nx.Graph()
        grafo.add_nodes_from(aleatorio.nodes)
        grafo.add_weighted_edges_from((origen, destino, 1) for origen, destino in aleatorio.edges)
        yield grafo


def es_ciclo_valido(grafo, nodos):
    aristas = list(zip(nodos, nodos[1:] + nodos[:1]))
    return len(set(nodos)) == len(nodos) >= (2 if grafo.is_directed() else 3) and all(
        grafo.has_edge(*arista) for arista in aristas)


@pytest.fixture
def dag():
    # Tareas: 1 y 2 antes que 3; 3 antes que 4 y 5; 4 antes que 6.
    return construir([(1, 3, 1), (2, 3, 1), (3, 4, 1), (3, 5, 1), (4, 6, 1)], dirigido=True)


class TestOrdenTopologico:
    def test_orden_valido(self, dag):
        orden = orden_topologico(dag)
        assert sorted(orden) == sorted(dag.nodes)
        posicion = {nodo: indice for indice, nodo in enumerate(orden)}
        assert all(posicion[origen] < posicion[destino] for origen, destino in dag.edges)

    def test_descripcion_final(self, dag):
        final = topologico_pasos(dag)[-1]
        assert final.descripcion == f"Orden topológico: {', '.join(map(str, orden_topologico(dag)))}."
        assert final.visitados == set(dag.nodes)

    def test_invariantes(self, dag):
        pasos = topologico_pasos(dag)
        invariantes_comunes(pasos)
        assert pasos[0].frontera == (1, 2)

    def test_con_ciclo(self):
        grafo = construir([(1, 2, 1), (2, 3, 1), (3, 4, 1), (4, 2, 1), (4, 5, 1)], dirigido=True)
        final = topologico_pasos(grafo)[-1]
        assert orden_topologico(grafo) is None
        assert final.descripcion.startswith("No existe orden topológico: 4 nodos quedan")
        assert sorted(final.ciclo) == [(2, 3), (3, 4), (4, 2)]

    @pytest.mark.parametrize("indice", range(25))
    def test_coincide_con_networkx(self, indice):
        grafo = list(grafos_aleatorios(dirigido=True))[indice]
        orden = orden_topologico(grafo)
        assert (orden is not None) == nx.is_directed_acyclic_graph(grafo)
        if orden is not None:
            assert sorted(orden) == sorted(grafo.nodes)
            posicion = {nodo: i for i, nodo in enumerate(orden)}
            assert all(posicion[origen] < posicion[destino] for origen, destino in grafo.edges)

    def test_rechaza_grafos_no_dirigidos(self, grafo_prueba):
        with pytest.raises(ValueError, match="solo aplica a grafos dirigidos"):
            topologico_pasos(grafo_prueba)


class TestDeteccionDeCiclos:
    def test_dag_sin_ciclos(self, dag):
        final = detectar_ciclo_pasos(dag)[-1]
        assert detectar_ciclo(dag) is None
        assert final.descripcion == "El grafo no tiene ciclos: es un grafo acíclico dirigido (DAG)."
        assert final.visitados == set(dag.nodes)

    def test_bosque_sin_ciclos(self):
        bosque = construir([(1, 2, 1), (2, 3, 1), (4, 5, 1)])
        assert detectar_ciclo(bosque) is None
        assert detectar_ciclo_pasos(bosque)[-1].descripcion == "El grafo no tiene ciclos: es un bosque."

    def test_ciclo_no_dirigido(self, grafo_prueba):
        ciclo = detectar_ciclo(grafo_prueba)
        assert es_ciclo_valido(grafo_prueba, ciclo)

    def test_una_arista_de_ida_y_vuelta_es_un_ciclo_dirigido(self, grafo_dirigido):
        assert detectar_ciclo(grafo_dirigido) == [1, 2]

    def test_invariantes(self, grafo_prueba, dag):
        invariantes_comunes(detectar_ciclo_pasos(grafo_prueba))
        invariantes_comunes(detectar_ciclo_pasos(dag))

    @pytest.mark.parametrize("dirigido", [False, True])
    def test_coincide_con_networkx(self, dirigido):
        for grafo in grafos_aleatorios(dirigido):
            ciclo = detectar_ciclo(grafo)
            tiene_ciclo = not (nx.is_directed_acyclic_graph(grafo) if dirigido else nx.is_forest(grafo))
            assert (ciclo is not None) == tiene_ciclo
            if ciclo is not None:
                assert es_ciclo_valido(grafo, ciclo)
