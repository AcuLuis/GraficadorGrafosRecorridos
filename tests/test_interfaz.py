"""Pruebas de humo de la interfaz, sin ventana visible."""
import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from ui import panel_vista  # noqa: E402
from ui.ventana_principal import MainWindow  # noqa: E402


@pytest.fixture(scope="module")
def app():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


@pytest.fixture
def avisos(monkeypatch):
    mensajes = []
    for nombre in ("warning", "critical"):
        monkeypatch.setattr(QtWidgets.QMessageBox, nombre,
                            staticmethod(lambda _padre, _titulo, texto, *a, **k: mensajes.append(texto)))
    return mensajes


@pytest.fixture
def vista(app, avisos):
    ventana = MainWindow()
    ventana.panel_vista.cargar_grafo_prueba()
    yield ventana.panel_vista
    ventana.close()
    ventana.deleteLater()


def aristas_azules(vista):
    return [arista for arista in vista.modelo.grafo.edges if vista.modelo.color_arista(*arista) == "blue"]


@pytest.mark.parametrize("ejecutar, nombre, titulo", [
    (lambda vista: vista.ejecutar_bfs(1), panel_vista.BFS, "PASOS BFS:"),
    (lambda vista: vista.ejecutar_dfs(1), panel_vista.DFS, "PASOS DFS:"),
    (lambda vista: vista.ejecutar_kruskal(), panel_vista.KRUSKAL, "PASOS KRUSKAL:"),
    (lambda vista: vista.ejecutar_dijkstra(1), panel_vista.DIJKSTRA, "PASOS DIJKSTRA:"),
])
def test_algoritmos_pintan_y_describen_el_resultado(vista, avisos, ejecutar, nombre, titulo):
    ejecutar(vista)
    assert len(aristas_azules(vista)) == 7
    assert vista.lbl_algoritmo.text() == nombre
    assert vista.panel_info.texto().startswith(titulo)
    assert avisos == []


def test_colores_no_se_acumulan_entre_algoritmos(vista):
    vista.ejecutar_bfs(1)
    vista.ejecutar_dfs(1)
    vista.ejecutar_kruskal()
    assert len(aristas_azules(vista)) == 7


def test_nodo_inicial_inexistente(vista, avisos):
    vista.ejecutar_dijkstra(99)
    assert avisos == ["El nodo 99 no existe en el grafo."]
    assert vista.lbl_algoritmo.text() == ""


def test_clic_agrega_nodo_solo_en_modo_nodo(vista):
    vista.lienzo.clic.emit(0.5, 0.5)
    assert 9 in vista.modelo.grafo
    vista.rb_dibujar_arista.setChecked(True)
    assert vista.btn_ingresar_arista.isEnabled()
    vista.lienzo.clic.emit(0.6, 0.6)
    assert 10 not in vista.modelo.grafo


def test_eliminar_nodo_repite_el_ultimo_algoritmo(vista):
    vista.ejecutar_bfs(1)
    vista.eliminar_nodo(2)
    assert vista.lbl_algoritmo.text() == panel_vista.BFS
    assert len(aristas_azules(vista)) == 6


def test_recorrido_seleccionado(vista, avisos):
    vista.conservar_recorrido()
    assert avisos == ["Primero ejecuta un algoritmo para obtener un recorrido."]
    vista.ejecutar_kruskal()
    vista.conservar_recorrido()
    assert vista.modelo.grafo.number_of_edges() == 7


def test_cargar_json_invalido_conserva_el_grafo(vista, avisos, tmp_path, monkeypatch):
    ruta = tmp_path / "roto.json"
    ruta.write_text("{no es json", encoding="utf-8")
    monkeypatch.setattr(QtWidgets.QFileDialog, "getOpenFileName", staticmethod(lambda *a, **k: (str(ruta), "")))
    vista.cargar_json()
    assert avisos and avisos[0].startswith("No se pudo cargar el grafo")
    assert vista.modelo.grafo.number_of_edges() == 17


def test_cargar_grafo_dirigido_sincroniza_el_tipo(vista, tmp_path, monkeypatch):
    vista.modelo.cambiar_tipo(dirigido=True)
    vista.modelo.agregar_nodo(0.2, 0.2)
    vista.modelo.agregar_nodo(0.8, 0.8)
    vista.modelo.agregar_arista(1, 2, 3)
    ruta = tmp_path / "dirigido.json"
    vista.modelo.guardar_json(ruta)
    vista.modelo.cambiar_tipo(dirigido=False)
    monkeypatch.setattr(QtWidgets.QFileDialog, "getOpenFileName", staticmethod(lambda *a, **k: (str(ruta), "")))
    vista.cargar_json()
    assert vista.modelo.dirigido
    assert vista.rb_dirigido.isChecked()


def test_cambiar_tipo_pide_confirmacion(vista, monkeypatch):
    monkeypatch.setattr(vista, "_confirmar_borrado", lambda: False)
    vista.rb_dirigido.click()
    assert not vista.modelo.dirigido
    assert vista.rb_no_dirigido.isChecked()
    monkeypatch.setattr(vista, "_confirmar_borrado", lambda: True)
    vista.rb_dirigido.click()
    assert vista.modelo.dirigido
    assert vista.modelo.grafo.number_of_nodes() == 0
