import math

import networkx as nx
import pytest

from algoritmos import (bellman_ford, bellman_ford_pasos, bfs_pasos, camino_minimo, dfs_pasos, dijkstra_pasos,
                        kruskal_pasos, prim, prim_pasos)
from conftest import construir


def invariantes_comunes(pasos):
    assert pasos, "debe haber al menos un paso"
    for paso in pasos:
        assert paso.descripcion
        assert paso.actual not in paso.frontera
        assert not set(paso.frontera) & paso.visitados
    for anterior, siguiente in zip(pasos, pasos[1:]):
        assert anterior.visitados <= siguiente.visitados


@pytest.mark.parametrize("generar, referencia", [(bfs_pasos, nx.bfs_edges), (dfs_pasos, nx.dfs_edges)])
class TestRecorridos:
    def test_ultimo_paso_es_el_resultado(self, grafo_prueba, generar, referencia):
        pasos = generar(grafo_prueba, 1)
        assert list(pasos[-1].aristas) == list(referencia(grafo_prueba, 1))
        assert pasos[-1].visitados == set(grafo_prueba.nodes)
        assert pasos[-1].frontera == ()

    def test_invariantes(self, grafo_prueba, generar, referencia):
        invariantes_comunes(generar(grafo_prueba, 4))

    def test_aristas_se_agregan_de_a_una(self, grafo_prueba, generar, referencia):
        pasos = generar(grafo_prueba, 1)
        for anterior, siguiente in zip(pasos, pasos[1:]):
            nuevas = siguiente.aristas[len(anterior.aristas):]
            assert siguiente.aristas[:len(anterior.aristas)] == anterior.aristas
            assert len(nuevas) <= 1
            if nuevas:
                assert siguiente.arista_actual == nuevas[0]

    def test_nodo_aislado(self, generar, referencia):
        grafo = construir([(1, 2, 1)], nodos_extra=[3])
        pasos = generar(grafo, 3)
        assert pasos[-1].aristas == ()
        assert "1 nodo." in pasos[-1].descripcion


def test_bfs_frontera_es_la_cola(grafo_prueba):
    pasos = bfs_pasos(grafo_prueba, 1)
    assert pasos[0].frontera == (1,)
    assert pasos[1].actual == 1 and pasos[1].frontera == ()
    assert pasos[2].frontera == (2,)


def test_dfs_frontera_es_la_pila(grafo_prueba):
    pasos = dfs_pasos(grafo_prueba, 1)
    assert pasos[1].actual == 2 and pasos[1].frontera == (1,)
    assert pasos[2].actual == 4 and pasos[2].frontera == (1, 2)


class TestKruskalPasos:
    def test_descartadas_formarian_ciclo(self, grafo_prueba):
        for paso in kruskal_pasos(grafo_prueba):
            if paso.descartadas and paso.arista_actual == paso.descartadas[-1]:
                bosque = construir([(*arista, 1) for arista in paso.aristas])
                assert nx.has_path(bosque, *paso.arista_actual)

    def test_aristas_examinadas_en_orden_de_peso(self, grafo_prueba):
        examinadas = [paso.arista_actual for paso in kruskal_pasos(grafo_prueba) if paso.arista_actual]
        pesos = [grafo_prueba.edges[arista]["weight"] for arista in examinadas]
        assert pesos == sorted(pesos)

    def test_resumen_final(self, grafo_prueba):
        final = kruskal_pasos(grafo_prueba)[-1]
        assert final.descripcion == "Árbol de expansión mínima: 7 aristas, peso total 26."
        assert final.visitados == set(grafo_prueba.nodes)

    def test_se_detiene_al_completar_el_arbol(self, grafo_prueba):
        pasos = kruskal_pasos(grafo_prueba)
        examinadas = [paso for paso in pasos if paso.arista_actual]
        assert len(examinadas) < grafo_prueba.number_of_edges()
        assert len(pasos[-1].aristas) + len(pasos[-1].descartadas) == len(examinadas)

    def test_bosque(self):
        final = kruskal_pasos(construir([(1, 2, 3), (3, 4, 1)]))[-1]
        assert final.descripcion.startswith("Bosque (el grafo no es conexo)")


class TestPrim:
    @pytest.mark.parametrize("inicio", [1, 4, 7])
    def test_arbol_de_peso_minimo(self, grafo_prueba, inicio):
        aristas = prim(grafo_prueba, inicio)
        arbol = construir(aristas)
        assert nx.is_tree(arbol) and set(arbol.nodes) == set(grafo_prueba.nodes)
        assert sum(peso for _, _, peso in aristas) == nx.minimum_spanning_tree(grafo_prueba).size(weight="weight")

    def test_invariantes_y_descartadas(self, grafo_prueba):
        pasos = prim_pasos(grafo_prueba, 1)
        invariantes_comunes(pasos)
        for paso in pasos:
            if paso.descartadas and paso.arista_actual == paso.descartadas[-1]:
                assert set(paso.arista_actual) <= paso.visitados

    def test_crece_desde_el_inicio(self, grafo_prueba):
        pasos = prim_pasos(grafo_prueba, 6)
        assert pasos[0].visitados == {6}
        assert pasos[1].arista_actual == (6, 4)  # la arista más liviana que sale del nodo 6

    def test_grafo_no_conexo(self):
        final = prim_pasos(construir([(1, 2, 3), (3, 4, 1)]), 1)[-1]
        assert final.aristas == ((1, 2),)
        assert "no es conexo" in final.descripcion

    def test_rechaza_grafos_dirigidos(self, grafo_dirigido):
        with pytest.raises(ValueError, match="no dirigidos"):
            prim_pasos(grafo_dirigido, 1)


class TestDijkstraPasos:
    def test_distancia_fijada_es_la_minima(self, grafo_prueba):
        esperadas = nx.single_source_dijkstra_path_length(grafo_prueba, 1)
        for paso in dijkstra_pasos(grafo_prueba, 1):
            for nodo in paso.visitados:
                assert paso.distancias[nodo] == esperadas[nodo]

    def test_invariantes(self, grafo_prueba):
        pasos = dijkstra_pasos(grafo_prueba, 1)
        invariantes_comunes(pasos)
        for paso in pasos:
            distancias = [paso.distancias[nodo] for nodo in paso.frontera]
            assert distancias == sorted(distancias)

    @pytest.mark.parametrize("destino", [1, 4, 6, 7])
    def test_camino_minimo(self, grafo_prueba, destino):
        costo, camino = camino_minimo(grafo_prueba, 1, destino)
        assert costo == nx.dijkstra_path_length(grafo_prueba, 1, destino)
        assert camino[0] == 1 and camino[-1] == destino
        assert sum(grafo_prueba.edges[a, b]["weight"] for a, b in zip(camino, camino[1:])) == costo

    def test_con_destino_se_detiene_y_muestra_el_camino(self, grafo_prueba):
        completos = dijkstra_pasos(grafo_prueba, 1)
        hasta_8 = dijkstra_pasos(grafo_prueba, 1, 8)
        assert len(hasta_8) < len(completos)
        assert hasta_8[-1].aristas == ((1, 8),)
        assert hasta_8[-1].descripcion == "Camino más corto: 1 → 8, costo 3."

    def test_sin_camino(self, grafo_dirigido):
        assert camino_minimo(grafo_dirigido, 1, 4) == (math.inf, None)
        final = dijkstra_pasos(grafo_dirigido, 1, 4)[-1]
        assert final.descripcion == "No hay camino del nodo 1 al nodo 4."
        assert final.aristas == ()

    def test_destino_inexistente(self, grafo_prueba):
        with pytest.raises(ValueError, match="El nodo 99 no existe"):
            dijkstra_pasos(grafo_prueba, 1, 99)


@pytest.fixture
def grafo_con_negativos():
    # Dirigido, con pesos negativos y sin ciclos negativos.
    return construir([(1, 2, 4), (1, 3, 5), (3, 2, -3), (2, 4, 2), (4, 5, -1), (3, 5, 4)], dirigido=True)


class TestBellmanFord:
    def test_coincide_con_dijkstra_sin_negativos(self, grafo_prueba):
        distancias, _ = bellman_ford(grafo_prueba, 1)
        assert distancias == nx.single_source_dijkstra_path_length(grafo_prueba, 1)

    def test_pesos_negativos(self, grafo_con_negativos):
        distancias, aristas = bellman_ford(grafo_con_negativos, 1)
        esperadas = nx.single_source_bellman_ford_path_length(grafo_con_negativos, 1)
        assert distancias == esperadas
        for origen, destino, peso in aristas:
            assert distancias[destino] == distancias[origen] + peso

    def test_dijkstra_sugiere_bellman_ford(self, grafo_con_negativos):
        with pytest.raises(ValueError, match="usa Bellman-Ford"):
            dijkstra_pasos(grafo_con_negativos, 1)

    def test_se_detiene_si_una_ronda_no_cambia_nada(self, grafo_prueba):
        pasos = bellman_ford_pasos(grafo_prueba, 1)
        rondas = [paso for paso in pasos if paso.descripcion.startswith("Ronda")]
        assert len(rondas) < grafo_prueba.number_of_nodes() - 1
        assert "no cambió ninguna distancia" in pasos[-2].descripcion

    def test_camino_a_un_destino(self, grafo_con_negativos):
        final = bellman_ford_pasos(grafo_con_negativos, 1, 5)[-1]
        assert final.descripcion == "Camino más corto: 1 → 3 → 2 → 4 → 5, costo 3."
        assert final.aristas == ((1, 3), (3, 2), (2, 4), (4, 5))

    def test_ciclo_negativo_dirigido(self):
        grafo = construir([(1, 2, 1), (2, 3, -2), (3, 4, 1), (4, 2, -1)], dirigido=True)
        final = bellman_ford_pasos(grafo, 1)[-1]
        assert nx.negative_edge_cycle(grafo)
        assert final.aristas == ()
        assert sorted(final.ciclo) == [(2, 3), (3, 4), (4, 2)]
        assert sum(grafo.edges[arista]["weight"] for arista in final.ciclo) < 0
        assert "ciclo de peso negativo" in final.descripcion
        with pytest.raises(ValueError, match="ciclo de peso negativo"):
            bellman_ford(grafo, 1)

    def test_arista_negativa_no_dirigida_es_un_ciclo(self):
        final = bellman_ford_pasos(construir([(1, 2, 3), (2, 3, -1)]), 1)[-1]
        assert {frozenset(arista) for arista in final.ciclo} == {frozenset((2, 3))}

    def test_ciclo_no_alcanzable_no_importa(self):
        grafo = construir([(1, 2, 1), (3, 4, -2), (4, 3, 1)], dirigido=True)
        distancias, _ = bellman_ford(grafo, 1)
        assert distancias == {1: 0, 2: 1, 3: math.inf, 4: math.inf}
