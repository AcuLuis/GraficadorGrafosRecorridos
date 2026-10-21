import math

import networkx as nx
import pytest

from algoritmos import bfs, dfs, dijkstra, kruskal
from conftest import construir


def es_arbol_desde(aristas, inicio):
    """Cada nodo nuevo cuelga de uno ya alcanzado y ninguno se repite."""
    alcanzados = {inicio}
    for padre, hijo in aristas:
        if padre not in alcanzados or hijo in alcanzados:
            return False
        alcanzados.add(hijo)
    return True


@pytest.mark.parametrize("algoritmo, referencia", [(bfs, nx.bfs_edges), (dfs, nx.dfs_edges)])
class TestRecorridos:
    def test_coincide_con_networkx(self, grafo_prueba, algoritmo, referencia):
        assert algoritmo(grafo_prueba, 1) == list(referencia(grafo_prueba, 1))

    def test_forma_un_arbol_que_cubre_lo_alcanzable(self, grafo_prueba, algoritmo, referencia):
        aristas = algoritmo(grafo_prueba, 3)
        assert es_arbol_desde(aristas, 3)
        assert len(aristas) == grafo_prueba.number_of_nodes() - 1

    def test_respeta_la_direccion(self, grafo_dirigido, algoritmo, referencia):
        assert algoritmo(grafo_dirigido, 1) == [(1, 2), (2, 3)]
        assert algoritmo(grafo_dirigido, 3) == []

    def test_nodo_inicial_inexistente(self, grafo_prueba, algoritmo, referencia):
        with pytest.raises(ValueError, match="El nodo 99 no existe"):
            algoritmo(grafo_prueba, 99)

    def test_no_modifica_el_grafo(self, grafo_prueba, algoritmo, referencia):
        antes = sorted(grafo_prueba.edges(data=True))
        algoritmo(grafo_prueba, 1)
        assert sorted(grafo_prueba.edges(data=True)) == antes


def test_bfs_recorre_por_niveles(grafo_prueba):
    niveles = nx.single_source_shortest_path_length(grafo_prueba, 1)
    for padre, hijo in bfs(grafo_prueba, 1):
        assert niveles[hijo] == niveles[padre] + 1


def test_dfs_no_depende_del_limite_de_recursion():
    camino = construir([(i, i + 1, 1) for i in range(5000)])
    assert len(dfs(camino, 0)) == 5000


class TestKruskal:
    def test_peso_total_minimo(self, grafo_prueba):
        aristas = kruskal(grafo_prueba)
        esperado = nx.minimum_spanning_tree(grafo_prueba).size(weight="weight")
        assert sum(peso for _, _, peso in aristas) == esperado == 26

    def test_resultado_es_arbol_de_expansion(self, grafo_prueba):
        arbol = construir(kruskal(grafo_prueba))
        assert nx.is_tree(arbol)
        assert set(arbol.nodes) == set(grafo_prueba.nodes)

    def test_aristas_en_orden_de_peso(self, grafo_prueba):
        pesos = [peso for _, _, peso in kruskal(grafo_prueba)]
        assert pesos == sorted(pesos)

    def test_grafo_no_conexo_da_un_bosque(self):
        grafo = construir([(1, 2, 3), (3, 4, 1)], nodos_extra=[5])
        assert sorted(kruskal(grafo)) == [(1, 2, 3), (3, 4, 1)]

    def test_rechaza_grafos_dirigidos(self, grafo_dirigido):
        with pytest.raises(ValueError, match="no dirigidos"):
            kruskal(grafo_dirigido)


class TestDijkstra:
    def test_distancias_coinciden_con_networkx(self, grafo_prueba):
        distancias, _ = dijkstra(grafo_prueba, 1)
        assert distancias == nx.single_source_dijkstra_path_length(grafo_prueba, 1)

    def test_pesos_en_ambos_sentidos_de_aristas_no_dirigidas(self):
        # La arista se crea como (1, 2) pero se recorre de 2 a 1.
        grafo = construir([(1, 2, 7), (2, 3, 1)])
        distancias, _ = dijkstra(grafo, 3)
        assert distancias == {1: 8, 2: 1, 3: 0}

    def test_arbol_de_caminos_minimos(self, grafo_prueba):
        distancias, aristas = dijkstra(grafo_prueba, 1)
        assert len(aristas) == grafo_prueba.number_of_nodes() - 1
        for origen, destino, peso in aristas:
            assert peso == grafo_prueba[origen][destino]["weight"]
            assert distancias[destino] == distancias[origen] + peso

    def test_nodos_inalcanzables(self, grafo_dirigido):
        distancias, aristas = dijkstra(grafo_dirigido, 1)
        assert distancias == {1: 0, 2: 1, 3: 2, 4: math.inf}
        assert aristas == [(1, 2, 1), (2, 3, 1)]

    def test_rechaza_pesos_negativos(self):
        with pytest.raises(ValueError, match="no negativos"):
            dijkstra(construir([(1, 2, -1)]), 1)

    def test_nodo_inicial_inexistente(self, grafo_prueba):
        with pytest.raises(ValueError, match="El nodo 0 no existe"):
            dijkstra(grafo_prueba, 0)
