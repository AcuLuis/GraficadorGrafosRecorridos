"""Listas de adyacencia y grafos aleatorios."""
from pathlib import Path

import networkx as nx
import pytest

from modelo import ModeloGrafo
from modelo.generacion import MARGEN, distribuir, grafo_aleatorio, maximo_de_aristas
from modelo.lista_adyacencia import escribir_lista_adyacencia, leer_lista_adyacencia

CARPETA_DATOS = Path(__file__).resolve().parent.parent / "datos"


class TestLeerListaDeAdyacencia:
    def test_formato_completo(self):
        texto = """
            # comentario
            dirigido
            1: 2(10), 3(-6) 7   # vecinos con y sin peso
            2: 4
            5:
        """
        dirigido, nodos, aristas = leer_lista_adyacencia(texto)
        assert dirigido
        assert nodos == [1, 2, 3, 7, 4, 5]
        assert aristas == [(1, 2, 10), (1, 3, -6), (1, 7, 1), (2, 4, 1)]

    def test_no_dirigido_por_defecto_y_aristas_repetidas(self):
        dirigido, _, aristas = leer_lista_adyacencia("1: 2(3)\n2: 1(3), 3")
        assert not dirigido
        assert aristas == [(1, 2, 3), (2, 3, 1)]

    @pytest.mark.parametrize("texto, mensaje", [
        ("1 2 3", "Línea 1: falta «:»"),
        ("1: 2(x)", "«2\\(x\\)» no es un vecino válido"),
        ("a: 2", "«a» no es un nodo válido"),
        ("0: 2", "«0» no es un nodo válido"),
        ("1: 1", "no puede ser vecino de sí mismo"),
        ("1: 2(3)\n2: 1(4)", "Línea 2: la arista 2-1 aparece con pesos distintos \\(3 y 4\\)"),
        ("1: 2\ndirigido", "Línea 2: el tipo de grafo debe indicarse antes"),
    ])
    def test_errores_indican_la_linea(self, texto, mensaje):
        with pytest.raises(ValueError, match=mensaje):
            leer_lista_adyacencia(texto)

    @pytest.mark.parametrize("dirigido", [False, True])
    def test_ida_y_vuelta(self, dirigido):
        grafo = grafo_aleatorio(9, 15, peso_minimo=-5, peso_maximo=5, dirigido=dirigido, semilla=3)
        leido_dirigido, nodos, aristas = leer_lista_adyacencia(escribir_lista_adyacencia(grafo))
        copia = nx.DiGraph() if leido_dirigido else nx.Graph()
        copia.add_nodes_from(nodos)
        copia.add_weighted_edges_from(aristas)
        assert leido_dirigido == dirigido
        assert nx.utils.graphs_equal(copia, grafo)

    def test_archivo_de_ejemplo(self):
        modelo = ModeloGrafo()
        modelo.cargar_lista_adyacencia(CARPETA_DATOS / "ejemplo_tareas.txt")
        assert modelo.dirigido
        assert nx.is_directed_acyclic_graph(modelo.grafo)
        assert modelo.grafo.number_of_nodes() == 7


class TestGrafoAleatorio:
    @pytest.mark.parametrize("dirigido", [False, True])
    def test_cantidades_y_pesos(self, dirigido):
        grafo = grafo_aleatorio(10, 20, peso_minimo=-3, peso_maximo=8, dirigido=dirigido, semilla=1)
        assert grafo.is_directed() == dirigido
        assert list(grafo.nodes) == list(range(1, 11))
        assert grafo.number_of_edges() == 20
        assert all(-3 <= peso <= 8 for _, _, peso in grafo.edges(data="weight"))
        assert not any(origen == destino for origen, destino in grafo.edges)

    def test_conexo(self):
        for semilla in range(10):
            assert nx.is_connected(grafo_aleatorio(12, 11, semilla=semilla))
            dirigido = grafo_aleatorio(12, 11, dirigido=True, semilla=semilla)
            raices = [nodo for nodo in dirigido.nodes if dirigido.in_degree(nodo) == 0]
            assert len(raices) == 1 and len(nx.descendants(dirigido, raices[0])) == 11

    def test_misma_semilla_mismo_grafo(self):
        assert nx.utils.graphs_equal(grafo_aleatorio(8, 12, semilla=7), grafo_aleatorio(8, 12, semilla=7))

    def test_completo(self):
        assert grafo_aleatorio(5, maximo_de_aristas(5, False), semilla=0).number_of_edges() == 10

    @pytest.mark.parametrize("opciones, mensaje", [
        ({"cantidad_nodos": 0, "cantidad_aristas": 0}, "entre 1 y"),
        ({"cantidad_nodos": 4, "cantidad_aristas": 7}, "como máximo 6 aristas"),
        ({"cantidad_nodos": 5, "cantidad_aristas": 3}, "al menos 4 aristas"),
        ({"cantidad_nodos": 3, "cantidad_aristas": 2, "peso_minimo": 5, "peso_maximo": 1}, "peso mínimo"),
    ])
    def test_opciones_invalidas(self, opciones, mensaje):
        with pytest.raises(ValueError, match=mensaje):
            grafo_aleatorio(**opciones)

    def test_no_conexo_admite_pocas_aristas(self):
        assert grafo_aleatorio(5, 0, conexo=False).number_of_edges() == 0


def test_distribuir_dentro_del_area():
    posiciones = distribuir(grafo_aleatorio(15, 25, semilla=2))
    assert len(posiciones) == 15
    for x, y in posiciones.values():
        assert MARGEN - 1e-9 <= x <= 1 - MARGEN + 1e-9
        assert MARGEN - 1e-9 <= y <= 1 - MARGEN + 1e-9


def test_modelo_generar_aleatorio():
    modelo = ModeloGrafo()
    modelo.generar_aleatorio(cantidad_nodos=6, cantidad_aristas=8, dirigido=True, semilla=4)
    assert modelo.dirigido
    assert set(modelo.posiciones) == set(modelo.grafo.nodes)
    assert modelo.siguiente_id() == 7
