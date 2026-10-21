import json
from pathlib import Path

import pytest

from modelo import COLOR_POR_DEFECTO, ModeloGrafo

CARPETA_DATOS = Path(__file__).resolve().parent.parent / "datos"


@pytest.fixture
def modelo():
    modelo = ModeloGrafo()
    for x in (0.1, 0.5, 0.9):
        modelo.agregar_nodo(x, 0.5)
    modelo.agregar_arista(1, 2, 4)
    modelo.agregar_arista(2, 3, 1)
    return modelo


def estado(modelo):
    return (modelo.dirigido, sorted(modelo.grafo.edges(data=True)), dict(modelo.posiciones), dict(modelo.colores))


class TestEdicion:
    def test_ids_consecutivos(self, modelo):
        assert list(modelo.grafo.nodes) == [1, 2, 3]

    def test_ids_sin_colision_tras_eliminar(self, modelo):
        posicion_3 = modelo.posiciones[3]
        modelo.eliminar_nodo(2)
        nuevo = modelo.agregar_nodo(0.3, 0.3)
        assert nuevo == 4
        assert modelo.posiciones[3] == posicion_3

    @pytest.mark.parametrize("origen, destino, mensaje", [
        (1, 1, "dos nodos distintos"),
        (1, 9, "El nodo 9 no se encuentra"),
        (8, 9, "Los nodos no se encuentran"),
    ])
    def test_aristas_invalidas(self, modelo, origen, destino, mensaje):
        with pytest.raises(ValueError, match=mensaje):
            modelo.agregar_arista(origen, destino, 1)

    def test_eliminar_nodo_limpia_posicion_y_colores(self, modelo):
        modelo.pintar_aristas([(1, 2), (2, 3)], "blue")
        modelo.eliminar_nodo(2)
        assert 2 not in modelo.posiciones
        assert modelo.colores == {}
        assert not modelo.tiene_aristas()

    def test_eliminar_nodo_inexistente(self, modelo):
        with pytest.raises(ValueError, match="no existe"):
            modelo.eliminar_nodo(9)

    def test_cambiar_tipo_vacia_el_grafo(self, modelo):
        modelo.cambiar_tipo(dirigido=True)
        assert modelo.dirigido
        assert modelo.grafo.number_of_nodes() == 0
        assert modelo.posiciones == {}


class TestColores:
    def test_no_dirigido_es_simetrico(self, modelo):
        modelo.pintar_aristas([(2, 1)], "blue")
        assert modelo.color_arista(1, 2) == modelo.color_arista(2, 1) == "blue"
        assert modelo.color_arista(2, 3) == COLOR_POR_DEFECTO

    def test_dirigido_distingue_sentido(self):
        modelo = ModeloGrafo(dirigido=True)
        modelo.agregar_nodo(0, 0)
        modelo.agregar_nodo(1, 1)
        modelo.agregar_arista(1, 2)
        modelo.agregar_arista(2, 1)
        modelo.pintar_aristas([(1, 2)], "blue")
        assert modelo.color_arista(1, 2) == "blue"
        assert modelo.color_arista(2, 1) == COLOR_POR_DEFECTO

    def test_conservar_aristas(self, modelo):
        modelo.pintar_aristas([(1, 2)], "blue")
        modelo.conservar_aristas("blue")
        assert list(modelo.grafo.edges) == [(1, 2)]

    def test_conservar_aristas_sin_recorrido(self, modelo):
        with pytest.raises(ValueError, match="Primero ejecuta un algoritmo"):
            modelo.conservar_aristas("blue")
        assert modelo.grafo.number_of_edges() == 2


class TestPersistencia:
    @pytest.mark.parametrize("dirigido", [False, True])
    def test_json_ida_y_vuelta(self, tmp_path, dirigido):
        original = ModeloGrafo(dirigido)
        original.agregar_nodo(0.2, 0.3)
        original.agregar_nodo(0.7, 0.8)
        original.agregar_arista(1, 2, 5)
        original.pintar_aristas([(1, 2)], "blue")
        ruta = tmp_path / "grafo.json"
        original.guardar_json(ruta)

        cargado = ModeloGrafo()
        cargado.cargar_json(ruta)
        assert estado(cargado) == estado(original)

    def test_lee_archivos_del_formato_anterior(self, modelo):
        datos = modelo.a_dict()
        datos["edge_weights"] = {"(1, 2)": 4, "(2, 3)": 1}
        nuevo = ModeloGrafo()
        nuevo.cargar_dict(json.loads(json.dumps(datos)))
        assert estado(nuevo) == estado(modelo)

    def test_no_ejecuta_codigo_del_archivo(self, modelo, tmp_path):
        marca = tmp_path / "ejecutado"
        datos = {"nodes": [1], "edges": [], "pos": {f"__import__('pathlib').Path(r'{marca}').touch()": [0, 0]}}
        antes = estado(modelo)
        with pytest.raises(ValueError, match="Formato de grafo inválido"):
            modelo.cargar_dict(datos)
        assert not marca.exists()
        assert estado(modelo) == antes

    def test_json_mal_formado(self, modelo, tmp_path):
        ruta = tmp_path / "roto.json"
        ruta.write_text("{no es json", encoding="utf-8")
        antes = estado(modelo)
        with pytest.raises(ValueError):
            modelo.cargar_json(ruta)
        assert estado(modelo) == antes

    def test_nodos_sin_posicion(self, modelo):
        with pytest.raises(ValueError, match="Nodos sin posición"):
            modelo.cargar_dict({"nodes": [1, 2], "edges": [], "pos": {"1": [0, 0]}})

    def test_grafo_de_prueba(self):
        modelo = ModeloGrafo()
        modelo.cargar_texto(CARPETA_DATOS / "Nodos.txt", CARPETA_DATOS / "Aristas.txt")
        assert modelo.grafo.number_of_nodes() == 8
        assert modelo.grafo.number_of_edges() == 17
        assert set(modelo.posiciones) == set(modelo.grafo.nodes)

    def test_grafo_de_prueba_invalido_no_cambia_el_estado(self, modelo, tmp_path):
        nodos = tmp_path / "nodos.txt"
        aristas = tmp_path / "aristas.txt"
        nodos.write_text("(1, 0.1, 0.1)\n", encoding="utf-8")
        aristas.write_text("(1, 5, 2)\n", encoding="utf-8")
        antes = estado(modelo)
        with pytest.raises(ValueError, match="El nodo 5 no se encuentra"):
            modelo.cargar_texto(nodos, aristas)
        assert estado(modelo) == antes
