"""Pruebas de humo de la interfaz, sin ventana visible."""
import csv
import os

import networkx as nx
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from matplotlib.backend_bases import MouseButton, MouseEvent  # noqa: E402
from matplotlib.colors import to_hex  # noqa: E402
from PyQt6 import QtCore  # noqa: E402
from PyQt6.QtGui import QPalette  # noqa: E402

from ui import dialogos, panel_vista  # noqa: E402
from ui.estilos import COLORES  # noqa: E402
from ui.tema import TEMAS  # noqa: E402
from ui.ventana_principal import CLAVE_TEMA_OSCURO, MainWindow, instalar_traducciones  # noqa: E402

ESQUINA_VACIA = (0.02, 0.98)


@pytest.fixture(scope="module")
def app():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


@pytest.fixture(autouse=True)
def sin_dialogos_modales(monkeypatch):
    """Un diálogo modal sin simular dejaría la prueba esperando una respuesta: se hace fallar al instante."""
    def bloquear(dialogo, *_):
        raise AssertionError(f"Diálogo modal inesperado: {type(dialogo).__name__} «{dialogo.windowTitle()}»")
    for clase in (QtWidgets.QDialog, QtWidgets.QMessageBox, QtWidgets.QMenu):
        monkeypatch.setattr(clase, "exec", bloquear)


@pytest.fixture
def avisos(monkeypatch):
    mensajes = []
    for nombre in ("warning", "critical"):
        monkeypatch.setattr(QtWidgets.QMessageBox, nombre,
                            staticmethod(lambda _padre, _titulo, texto, *a, **k: mensajes.append(texto)))
    return mensajes


def preferencias_temporales(carpeta):
    """Preferencias en un archivo .ini temporal, para no tocar las del usuario."""
    return QtCore.QSettings(str(carpeta / "preferencias.ini"), QtCore.QSettings.Format.IniFormat)


@pytest.fixture
def ventana(app, avisos, tmp_path):
    ventana = MainWindow(preferencias_temporales(tmp_path))
    ventana.panel_vista.cargar_grafo_prueba()
    ventana.panel_vista.lienzo.draw()
    yield ventana
    ventana.close()
    ventana.deleteLater()


@pytest.fixture
def vista(ventana):
    return ventana.panel_vista


@pytest.fixture
def confirmar(vista, monkeypatch):
    """Responde automáticamente a las confirmaciones; por defecto, que sí."""
    respuesta = {"valor": True}
    monkeypatch.setattr(vista, "_confirmar", lambda _mensaje: respuesta["valor"])
    return respuesta


@pytest.fixture
def peso_ingresado(monkeypatch):
    """Valor que devolverá el diálogo de peso; ``None`` simula cancelar."""
    respuesta = {"valor": 4}
    monkeypatch.setattr(QtWidgets.QInputDialog, "getInt", staticmethod(
        lambda *a, **k: (respuesta["valor"] or 0, respuesta["valor"] is not None)))
    return respuesta


def aristas_azules(vista):
    return [arista for arista in vista.modelo.grafo.edges if vista.modelo.color_arista(*arista) == "blue"]


def mouse(vista, nombre, punto, boton=MouseButton.LEFT):
    lienzo = vista.lienzo
    x, y = lienzo.ejes.transData.transform(punto)
    lienzo.callbacks.process(nombre, MouseEvent(nombre, lienzo, x, y, button=boton))


def clic(vista, punto, boton=MouseButton.LEFT):
    mouse(vista, "button_press_event", punto, boton)
    mouse(vista, "button_release_event", punto, boton)


def posicion(vista, nodo):
    return vista.modelo.posiciones[nodo]


def punto_medio(vista, origen, destino):
    (x1, y1), (x2, y2) = posicion(vista, origen), posicion(vista, destino)
    return (x1 + x2) / 2, (y1 + y2) / 2


class TestAlgoritmos:
    @pytest.mark.parametrize("ejecutar, nombre, titulo", [
        (lambda vista: vista.ejecutar_bfs(1), panel_vista.BFS, f"{panel_vista.BFS} desde el nodo 1"),
        (lambda vista: vista.ejecutar_dfs(1), panel_vista.DFS, f"{panel_vista.DFS} desde el nodo 1"),
        (lambda vista: vista.ejecutar_kruskal(), panel_vista.KRUSKAL, panel_vista.KRUSKAL),
        (lambda vista: vista.ejecutar_dijkstra(1), panel_vista.DIJKSTRA, f"{panel_vista.DIJKSTRA} desde el nodo 1"),
    ])
    def test_pintan_y_describen_el_resultado(self, vista, avisos, ejecutar, nombre, titulo):
        ejecutar(vista)
        assert len(aristas_azules(vista)) == 7
        assert vista.lbl_algoritmo.text() == nombre
        assert vista.panel_info.titulo == titulo
        assert vista.panel_info.texto().startswith(titulo)
        assert vista.panel_info.tabla_pasos.rowCount() == len(vista.pasos)
        assert avisos == []

    def test_colores_no_se_acumulan(self, vista):
        vista.ejecutar_bfs(1)
        vista.ejecutar_dfs(1)
        vista.ejecutar_kruskal()
        assert len(aristas_azules(vista)) == 7

    def test_nodo_inicial_inexistente(self, vista, avisos):
        vista.ejecutar_dijkstra(99)
        assert avisos == ["El nodo 99 no existe en el grafo."]
        assert vista.lbl_algoritmo.text() == ""

    def test_se_recalcula_al_eliminar_un_nodo(self, vista):
        vista.ejecutar_bfs(1)
        vista.eliminar_nodo(2)
        assert vista.lbl_algoritmo.text() == panel_vista.BFS
        assert len(aristas_azules(vista)) == 6


class TestLienzo:
    def test_detecta_nodos_y_aristas(self, vista):
        lienzo = vista.lienzo
        x, y = lienzo.ejes.transData.transform(posicion(vista, 3))
        assert lienzo.nodo_en(x + 3, y - 3) == 3
        x, y = lienzo.ejes.transData.transform(punto_medio(vista, 1, 7))
        assert set(lienzo.arista_en(x, y)) == {1, 7}
        x, y = lienzo.ejes.transData.transform(ESQUINA_VACIA)
        assert lienzo.nodo_en(x, y) is None and lienzo.arista_en(x, y) is None

    def test_clic_en_vacio_crea_nodo_solo_en_modo_nodo(self, vista):
        clic(vista, ESQUINA_VACIA)
        assert 9 in vista.modelo.grafo
        assert vista.pila_deshacer.undoText() == "Crear nodo 9"
        vista.rb_dibujar_arista.setChecked(True)
        clic(vista, (0.5, 0.02))
        assert 10 not in vista.modelo.grafo

    def test_clic_en_nodo_lo_selecciona(self, vista):
        clic(vista, posicion(vista, 3))
        assert vista.seleccionado == 3
        assert vista.modelo.grafo.number_of_nodes() == 8
        clic(vista, posicion(vista, 3))
        assert vista.seleccionado is None

    def test_arrastrar_nodo_y_deshacer(self, vista):
        inicio = posicion(vista, 1)
        mouse(vista, "button_press_event", inicio)
        mouse(vista, "motion_notify_event", (0.3, 0.3))
        mouse(vista, "motion_notify_event", (0.5, 0.1))
        mouse(vista, "button_release_event", (0.5, 0.1))
        assert posicion(vista, 1) == pytest.approx((0.5, 0.1))
        assert vista.seleccionado is None
        assert vista.pila_deshacer.undoText() == "Mover nodo 1"
        vista.pila_deshacer.undo()
        assert posicion(vista, 1) == pytest.approx(inicio)

    def test_crear_arista_con_clics(self, vista, peso_ingresado):
        vista.rb_dibujar_arista.setChecked(True)
        clic(vista, posicion(vista, 1))
        assert vista.seleccionado == 1
        clic(vista, posicion(vista, 6))
        assert vista.modelo.peso(1, 6) == 4
        assert vista.seleccionado is None
        vista.pila_deshacer.undo()
        assert not vista.modelo.grafo.has_edge(1, 6)

    def test_cancelar_el_peso_no_crea_arista(self, vista, peso_ingresado):
        peso_ingresado["valor"] = None
        vista.rb_dibujar_arista.setChecked(True)
        clic(vista, posicion(vista, 1))
        clic(vista, posicion(vista, 6))
        assert not vista.modelo.grafo.has_edge(1, 6)

    def test_clic_derecho_abre_el_menu_del_elemento(self, vista, monkeypatch):
        abiertos = []
        monkeypatch.setattr(QtWidgets.QMenu, "exec",
                            lambda menu, *a: abiertos.append([accion.text() for accion in menu.actions()]))
        clic(vista, posicion(vista, 5), MouseButton.RIGHT)
        clic(vista, punto_medio(vista, 1, 7), MouseButton.RIGHT)
        assert abiertos[0][0] == "Eliminar nodo 5"
        assert abiertos[1][0].startswith("Editar peso de 1 - 7") or abiertos[1][0].startswith("Editar peso de 7 - 1")


class TestMenusContextuales:
    @staticmethod
    def disparar(menu, inicio_texto):
        next(accion for accion in menu.actions() if accion.text().startswith(inicio_texto)).trigger()

    def test_editar_peso(self, vista, peso_ingresado):
        peso_ingresado["valor"] = 8
        self.disparar(vista.menu_arista(1, 2), "Editar peso")
        assert vista.modelo.peso(1, 2) == 8

    def test_eliminar_arista(self, vista):
        self.disparar(vista.menu_arista(1, 2), "Eliminar arista")
        assert not vista.modelo.grafo.has_edge(1, 2)

    def test_algoritmo_desde_un_nodo(self, vista):
        self.disparar(vista.menu_nodo(3), "Dijkstra")
        assert vista.panel_info.titulo == f"{panel_vista.DIJKSTRA} desde el nodo 3"


class TestDeshacer:
    def test_deshacer_y_rehacer_creacion_de_nodo(self, vista):
        vista.lienzo.clic_vacio.emit(0.5, 0.5)
        assert 9 in vista.modelo.grafo
        vista.pila_deshacer.undo()
        assert 9 not in vista.modelo.grafo
        vista.pila_deshacer.redo()
        assert 9 in vista.modelo.grafo

    def test_deshacer_eliminacion_restaura_aristas_y_pesos(self, vista):
        antes = sorted(vista.modelo.grafo.edges(data=True))
        vista.eliminar_nodo(4)
        vista.pila_deshacer.undo()
        assert sorted(vista.modelo.grafo.edges(data=True)) == antes

    def test_deshacer_limpiar(self, vista, confirmar):
        vista.limpiar()
        assert vista.modelo.grafo.number_of_nodes() == 0
        vista.pila_deshacer.undo()
        assert vista.modelo.grafo.number_of_edges() == 17

    def test_algoritmo_se_recalcula_al_deshacer(self, vista):
        vista.ejecutar_kruskal()
        vista.eliminar_nodo(4)
        assert len(aristas_azules(vista)) == 6
        vista.pila_deshacer.undo()
        assert len(aristas_azules(vista)) == 7
        assert vista.lbl_algoritmo.text() == panel_vista.KRUSKAL

    def test_error_no_queda_en_el_historial(self, vista, avisos):
        cantidad = vista.pila_deshacer.count()
        vista.agregar_arista(1, 99, 3)
        assert avisos == ["El nodo 99 no se encuentra."]
        assert vista.pila_deshacer.count() == cantidad

    def test_deshacer_cambio_de_tipo(self, vista, confirmar):
        vista.rb_dirigido.click()
        assert vista.modelo.dirigido
        vista.pila_deshacer.undo()
        assert not vista.modelo.dirigido
        assert vista.rb_no_dirigido.isChecked()
        assert vista.modelo.grafo.number_of_edges() == 17


class TestConfirmaciones:
    def test_limpiar_cancelado(self, vista, confirmar):
        confirmar["valor"] = False
        vista.limpiar()
        assert vista.modelo.grafo.number_of_nodes() == 8

    def test_cambiar_tipo_cancelado(self, vista, confirmar):
        confirmar["valor"] = False
        vista.rb_dirigido.click()
        assert not vista.modelo.dirigido
        assert vista.rb_no_dirigido.isChecked()

    def test_cambiar_tipo_confirmado(self, vista, confirmar):
        vista.rb_dirigido.click()
        assert vista.modelo.dirigido
        assert vista.modelo.grafo.number_of_nodes() == 0

    def test_recorrido_seleccionado(self, vista, avisos, confirmar):
        vista.conservar_recorrido()
        assert avisos == ["Primero ejecuta un algoritmo para obtener un recorrido."]
        vista.ejecutar_kruskal()
        confirmar["valor"] = False
        vista.conservar_recorrido()
        assert vista.modelo.grafo.number_of_edges() == 17
        confirmar["valor"] = True
        vista.conservar_recorrido()
        assert vista.modelo.grafo.number_of_edges() == 7


class TestArchivos:
    def test_cargar_json_invalido_conserva_el_grafo(self, vista, avisos, tmp_path, monkeypatch):
        ruta = tmp_path / "roto.json"
        ruta.write_text("{no es json", encoding="utf-8")
        monkeypatch.setattr(QtWidgets.QFileDialog, "getOpenFileName", staticmethod(lambda *a, **k: (str(ruta), "")))
        vista.cargar_json()
        assert avisos and avisos[0].startswith("No se pudo cargar el grafo")
        assert vista.modelo.grafo.number_of_edges() == 17

    def test_cargar_grafo_dirigido_sincroniza_el_tipo(self, vista, tmp_path, monkeypatch):
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


def accion(ventana, texto):
    acciones = [accion for menu in ventana.menuBar().findChildren(QtWidgets.QMenu) for accion in menu.actions()]
    return next(accion for accion in acciones if accion.text() == texto)


@pytest.fixture
def nodo_elegido(monkeypatch):
    """Simula la lista desplegable de nodos; guarda lo que se mostró y responde ``valor`` (``None`` = cancelar)."""
    respuesta = {"valor": "3", "opciones": None, "indice": None}

    def get_item(_padre, _titulo, _etiqueta, opciones, indice, _editable):
        respuesta["opciones"], respuesta["indice"] = opciones, indice
        return (respuesta["valor"] or "", respuesta["valor"] is not None)

    monkeypatch.setattr(QtWidgets.QInputDialog, "getItem", staticmethod(get_item))
    return respuesta


class TestNodoInicial:
    def test_lista_con_los_nodos_existentes(self, ventana, vista, nodo_elegido):
        accion(ventana, panel_vista.BFS).trigger()
        assert nodo_elegido["opciones"] == [str(nodo) for nodo in vista.modelo.grafo.nodes]
        assert vista.panel_info.titulo == f"{panel_vista.BFS} desde el nodo 3"

    def test_sugiere_el_nodo_seleccionado(self, ventana, vista, nodo_elegido):
        vista.seleccionar(5)
        accion(ventana, panel_vista.DFS).trigger()
        assert nodo_elegido["opciones"][nodo_elegido["indice"]] == "5"

    def test_sugiere_el_ultimo_inicio(self, ventana, vista, nodo_elegido):
        vista.ejecutar_dfs(7)
        accion(ventana, panel_vista.DFS).trigger()
        assert nodo_elegido["opciones"][nodo_elegido["indice"]] == "7"

    def test_cancelar(self, ventana, vista, nodo_elegido):
        nodo_elegido["valor"] = None
        accion(ventana, panel_vista.BFS).trigger()
        assert vista.lbl_algoritmo.text() == ""

    def test_sin_aristas_no_pregunta(self, ventana, vista, nodo_elegido, avisos, confirmar):
        vista.limpiar()
        accion(ventana, panel_vista.BFS).trigger()
        assert nodo_elegido["opciones"] is None
        assert avisos == ["No hay nodo o no hay aristas."]


class TestAtajos:
    @pytest.mark.parametrize("texto, atajo", [
        ("Guardar Avance", "Ctrl+S"), ("Cargar Avance", "Ctrl+O"), ("Guardar Imagen", "Ctrl+E"),
        ("Modo Nodo", "N"), ("Modo Arista", "A"), ("Cancelar Selección", "Esc"),
        ("Eliminar Nodo", "Del"), ("Limpiar Grafo", "Ctrl+L"),
        (panel_vista.BFS, "Ctrl+1"), (panel_vista.DFS, "Ctrl+2"),
        (panel_vista.KRUSKAL, "Ctrl+3"), (panel_vista.DIJKSTRA, "Ctrl+4"),
        (panel_vista.PRIM, "Ctrl+5"), (panel_vista.BELLMAN_FORD, "Ctrl+6"),
        (panel_vista.TOPOLOGICO, "Ctrl+7"), (panel_vista.CICLOS, "Ctrl+8"),
        ("Reproducir / Pausar", "Ctrl+P"), ("Paso Anterior", "Ctrl+Left"), ("Paso Siguiente", "Ctrl+Right"),
        ("Primer Paso", "Ctrl+Home"), ("Último Paso", "Ctrl+End"),
        ("Acercar", "Ctrl++"), ("Alejar", "Ctrl+-"), ("Restablecer Vista", "Ctrl+0"),
        ("Tema Oscuro", "Ctrl+Shift+D"),
        ("Grafo Aleatorio…", "Ctrl+G"), ("Importar Lista de Adyacencia…", "Ctrl+I"),
    ])
    def test_atajos_definidos(self, ventana, texto, atajo):
        assert accion(ventana, texto).shortcut().toString() == atajo

    def test_deshacer_y_rehacer(self, ventana, vista):
        vista.eliminar_nodo(8)
        deshacer = accion(ventana, "Deshacer Eliminar nodo 8")
        assert deshacer.shortcut().toString() == "Ctrl+Z"
        deshacer.trigger()
        assert 8 in vista.modelo.grafo
        accion(ventana, "Rehacer Eliminar nodo 8").trigger()
        assert 8 not in vista.modelo.grafo

    def test_suprimir_elimina_el_nodo_seleccionado(self, ventana, vista):
        vista.seleccionar(4)
        accion(ventana, "Eliminar Nodo").trigger()
        assert 4 not in vista.modelo.grafo
        assert vista.seleccionado is None

    def test_suprimir_sin_seleccion_pregunta(self, ventana, vista, nodo_elegido):
        accion(ventana, "Eliminar Nodo").trigger()
        assert 3 not in vista.modelo.grafo

    def test_modos_y_cancelar_seleccion(self, ventana, vista):
        accion(ventana, "Modo Arista").trigger()
        assert vista.rb_dibujar_arista.isChecked()
        vista.seleccionar(2)
        accion(ventana, "Cancelar Selección").trigger()
        assert vista.seleccionado is None
        accion(ventana, "Modo Nodo").trigger()
        assert vista.rb_dibujar_nodo.isChecked()


def colores_en_lienzo(vista):
    """Color con el que el lienzo dibuja cada nodo y cada arista en este momento."""
    lienzo = vista.lienzo
    nodos = {nodo: lienzo._color_nodo(nodo) for nodo in vista.modelo.grafo.nodes}
    aristas = {arista: lienzo._color_arista(*arista) for arista in vista.modelo.grafo.edges}
    return nodos, aristas


class TestAnimacion:
    def test_muestra_el_ultimo_paso_al_ejecutar(self, vista):
        vista.ejecutar_bfs(1)
        assert vista.reproductor.total == len(vista.pasos)
        assert vista.reproductor.indice == len(vista.pasos) - 1
        _, aristas = colores_en_lienzo(vista)
        assert list(aristas.values()).count(COLORES["recorrido"]) == 7

    def test_primer_paso(self, vista):
        vista.ejecutar_bfs(1)
        vista.reproductor.primero()
        nodos, aristas = colores_en_lienzo(vista)
        assert nodos[1] == COLORES["espera"]
        assert set(nodos.values()) == {COLORES["espera"], COLORES["normal"]}
        assert set(aristas.values()) == {COLORES["arista"]}
        assert vista.panel_info.tabla_pasos.currentRow() == 0

    def test_paso_a_paso(self, vista):
        vista.ejecutar_bfs(1)
        vista.reproductor.primero()
        vista.reproductor.siguiente()
        vista.reproductor.siguiente()
        nodos, aristas = colores_en_lienzo(vista)
        assert nodos[1] == COLORES["actual"]
        assert nodos[2] == COLORES["espera"]
        assert aristas[(1, 2)] == COLORES["examinada"]
        vista.reproductor.anterior()
        assert vista.reproductor.indice == 1
        assert vista.reproductor.lbl_paso.text() == f"Paso 2 de {len(vista.pasos)}"

    def test_reproduccion_automatica(self, vista):
        vista.ejecutar_dfs(1)
        vista.reproductor.reproducir()
        assert vista.reproductor.reproduciendo
        assert vista.reproductor.indice == 0
        while vista.reproductor.reproduciendo:
            vista.reproductor._avanzar_automaticamente()
        assert vista.reproductor.indice == len(vista.pasos) - 1

    def test_velocidad(self, vista):
        intervalo = vista.reproductor.temporizador.interval()
        vista.reproductor.cmb_velocidad.setCurrentText("2x")
        assert vista.reproductor.temporizador.interval() == intervalo // 2

    def test_elegir_un_paso_en_la_tabla(self, vista):
        vista.ejecutar_kruskal()
        vista.panel_info.tabla_pasos.selectRow(3)
        assert vista.reproductor.indice == 3

    def test_kruskal_muestra_descartadas(self, vista):
        vista.ejecutar_kruskal()
        descartadas = vista.pasos[-1].descartadas
        assert descartadas
        _, aristas = colores_en_lienzo(vista)
        for origen, destino in descartadas:
            color = aristas.get((origen, destino)) or aristas.get((destino, origen))
            assert color == COLORES["descartada"]
        assert set(descartadas) <= vista.lienzo.estilo.discontinuas

    def test_dijkstra_muestra_distancias(self, vista):
        vista.ejecutar_dijkstra(1)
        tabla = vista.panel_info.tabla_distancias
        assert tabla.isVisibleTo(vista.panel_info)
        assert tabla.rowCount() == 8
        vista.reproductor.primero()
        distancias = {tabla.item(fila, 0).text(): tabla.item(fila, 1).text() for fila in range(tabla.rowCount())}
        assert distancias["1"] == "0"
        assert distancias["6"] == "∞"
        vista.ejecutar_bfs(1)
        assert not tabla.isVisibleTo(vista.panel_info)

    def test_leyenda_segun_el_algoritmo(self, vista, confirmar):
        vista.ejecutar_bfs(1)
        assert "En la cola" in vista.leyenda.entradas
        vista.ejecutar_kruskal()
        assert "Descartada (ciclo)" in vista.leyenda.entradas
        # Cada entrada es una muestra de color y un texto; las de la leyenda anterior no deben quedar.
        assert len(vista.leyenda.findChildren(QtWidgets.QLabel)) == 2 * len(vista.leyenda.entradas)
        vista.limpiar()
        assert vista.leyenda.entradas == []
        assert not vista.reproductor.isEnabled()

    def test_editar_el_grafo_conserva_el_paso(self, vista):
        vista.ejecutar_bfs(1)
        vista.reproductor.ir_a(3)
        vista.eliminar_nodo(8)
        assert vista.reproductor.indice == 3
        vista.reproductor.ultimo()
        vista.eliminar_nodo(7)
        assert vista.reproductor.indice == vista.reproductor.total - 1


class TestDijkstraConDestino:
    def test_dialogo_inicio_y_destino(self, app):
        dialogo = dialogos.DialogoInicioDestino([1, 2, 3], sugerido=2)
        assert dialogo.eleccion() == (2, None)
        dialogo.cmb_destino.setCurrentIndex(3)
        assert dialogo.eleccion() == (2, 3)

    def test_menu_algoritmos(self, ventana, vista, monkeypatch):
        monkeypatch.setattr(panel_vista, "pedir_inicio_y_destino", lambda *a, **k: (1, 6))
        accion(ventana, panel_vista.DIJKSTRA).trigger()
        assert vista.panel_info.titulo == f"{panel_vista.DIJKSTRA} del nodo 1 al nodo 6"
        assert vista.panel_info.resumen == "Camino más corto: 1 → 3 → 6, costo 10."
        assert sorted(map(sorted, aristas_azules(vista))) == [[1, 3], [3, 6]]

    def test_sin_destino_calcula_todos(self, ventana, vista, monkeypatch):
        monkeypatch.setattr(panel_vista, "pedir_inicio_y_destino", lambda *a, **k: (1, None))
        accion(ventana, panel_vista.DIJKSTRA).trigger()
        assert len(aristas_azules(vista)) == 7

    def test_menu_contextual_desde_el_seleccionado(self, vista):
        vista.seleccionar(2)
        TestMenusContextuales.disparar(vista.menu_nodo(6), "Camino más corto del nodo 2 al nodo 6")
        costo, camino = nx.single_source_dijkstra(vista.modelo.grafo, 2, 6)
        assert vista.panel_info.resumen == f"Camino más corto: {' → '.join(map(str, camino))}, costo {costo}."

    def test_eliminar_el_destino_calcula_todos(self, vista):
        vista.ejecutar_dijkstra(1, 6)
        vista.eliminar_nodo(6)
        assert vista.panel_info.titulo == f"{panel_vista.DIJKSTRA} desde el nodo 1"


def usar_grafo_dirigido(vista, aristas):
    """Reemplaza el grafo por uno dirigido con nodos 1..n y las aristas ``(origen, destino, peso)`` dadas."""
    vista.modelo.cambiar_tipo(dirigido=True)
    cantidad = max(max(origen, destino) for origen, destino, _ in aristas)
    for indice in range(cantidad):
        vista.modelo.agregar_nodo(0.1 + 0.8 * indice / cantidad, 0.5 + 0.3 * (indice % 2))
    for origen, destino, peso in aristas:
        vista.modelo.agregar_arista(origen, destino, peso)


def aristas_con_color(vista, clave):
    _, aristas = colores_en_lienzo(vista)
    return sorted(arista for arista, color in aristas.items() if color == COLORES[clave])


class TestAlgoritmosNuevos:
    def test_prim(self, vista):
        vista.ejecutar_prim(1)
        assert len(aristas_azules(vista)) == 7
        assert vista.panel_info.titulo == f"{panel_vista.PRIM} desde el nodo 1"
        assert vista.panel_info.resumen.endswith("peso total 26.")
        assert "Candidato" in vista.leyenda.entradas

    def test_prim_desde_el_menu_contextual(self, vista):
        TestMenusContextuales.disparar(vista.menu_nodo(5), "Prim desde el nodo 5")
        assert vista.lbl_algoritmo.text() == panel_vista.PRIM

    def test_bellman_ford_con_pesos_negativos(self, ventana, vista, monkeypatch):
        usar_grafo_dirigido(vista, [(1, 2, 4), (1, 3, 5), (3, 2, -3), (2, 4, 2)])
        monkeypatch.setattr(panel_vista, "pedir_inicio_y_destino", lambda *a, **k: (1, 4))
        accion(ventana, panel_vista.BELLMAN_FORD).trigger()
        assert vista.panel_info.resumen == "Camino más corto: 1 → 3 → 2 → 4, costo 4."
        assert vista.panel_info.tabla_distancias.isVisibleTo(vista.panel_info)

    def test_dijkstra_rechaza_pesos_negativos(self, vista, avisos):
        vista.modelo.cambiar_peso(1, 2, -1)
        vista.ejecutar_dijkstra(1)
        assert avisos == ["Dijkstra requiere pesos no negativos; para pesos negativos usa Bellman-Ford."]

    def test_bellman_ford_muestra_el_ciclo_negativo(self, vista):
        usar_grafo_dirigido(vista, [(1, 2, 1), (2, 3, -2), (3, 4, 1), (4, 2, -1)])
        vista.ejecutar_bellman_ford(1)
        assert "ciclo de peso negativo" in vista.panel_info.resumen
        assert aristas_con_color(vista, "ciclo") == [(2, 3), (3, 4), (4, 2)]

    def test_orden_topologico(self, vista):
        usar_grafo_dirigido(vista, [(1, 3, 1), (2, 3, 1), (3, 4, 1)])
        vista.ejecutar_topologico()
        assert vista.panel_info.resumen == "Orden topológico: 1, 2, 3, 4."
        assert "En la cola (sin entradas pendientes)" in vista.leyenda.entradas

    def test_orden_topologico_en_grafo_no_dirigido(self, vista, avisos):
        vista.ejecutar_topologico()
        assert avisos == ["El orden topológico solo aplica a grafos dirigidos."]

    def test_deteccion_de_ciclos(self, vista):
        vista.ejecutar_ciclos()
        ciclo = vista.pasos[-1].ciclo
        assert len(ciclo) >= 3
        assert vista.panel_info.resumen.startswith("Ciclo encontrado:")
        for origen, destino in ciclo:
            assert vista.lienzo._color_arista(origen, destino) == COLORES["ciclo"] or \
                vista.lienzo._color_arista(destino, origen) == COLORES["ciclo"]


class TestGrafosNuevos:
    def test_dialogo_ajusta_el_maximo_de_aristas(self, app):
        dialogo = dialogos.DialogoGrafoAleatorio()
        dialogo.spn_nodos.setValue(4)
        assert dialogo.spn_aristas.maximum() == 6
        dialogo.chk_dirigido.setChecked(True)
        assert dialogo.spn_aristas.maximum() == 12

    def test_generar_aleatorio_y_deshacer(self, ventana, vista, monkeypatch):
        opciones = {"cantidad_nodos": 6, "cantidad_aristas": 9, "peso_minimo": 1, "peso_maximo": 5,
                    "dirigido": True, "conexo": True}
        monkeypatch.setattr(panel_vista, "pedir_grafo_aleatorio", lambda *a, **k: opciones)
        accion(ventana, "Grafo Aleatorio…").trigger()
        assert vista.modelo.dirigido and vista.rb_dirigido.isChecked()
        assert vista.modelo.grafo.number_of_edges() == 9
        vista.pila_deshacer.undo()
        assert vista.modelo.grafo.number_of_edges() == 17

    def test_opciones_invalidas(self, vista, avisos, monkeypatch):
        opciones = {"cantidad_nodos": 6, "cantidad_aristas": 2, "peso_minimo": 1, "peso_maximo": 5,
                    "dirigido": False, "conexo": True}
        monkeypatch.setattr(panel_vista, "pedir_grafo_aleatorio", lambda *a, **k: opciones)
        vista.generar_grafo_aleatorio()
        assert avisos == ["No se pudo generar el grafo:\nUn grafo conexo de 6 nodos necesita al menos 5 aristas."]

    def test_exportar_e_importar_lista_de_adyacencia(self, ventana, vista, tmp_path, monkeypatch, confirmar):
        ruta = tmp_path / "lista.txt"
        monkeypatch.setattr(QtWidgets.QFileDialog, "getSaveFileName", staticmethod(lambda *a, **k: (str(ruta), "")))
        monkeypatch.setattr(QtWidgets.QFileDialog, "getOpenFileName", staticmethod(lambda *a, **k: (str(ruta), "")))
        original = vista.modelo.grafo.copy()
        accion(ventana, "Exportar Lista de Adyacencia…").trigger()
        assert ruta.read_text(encoding="utf-8").startswith("no dirigido\n1: 2(10), 3(6), 5(14), 7(9), 8(3)\n")
        vista.limpiar()
        accion(ventana, "Importar Lista de Adyacencia…").trigger()
        assert nx.utils.graphs_equal(vista.modelo.grafo, original)

    def test_importar_lista_invalida(self, ventana, vista, avisos, tmp_path, monkeypatch):
        ruta = tmp_path / "mala.txt"
        ruta.write_text("1: 2(x)\n", encoding="utf-8")
        monkeypatch.setattr(QtWidgets.QFileDialog, "getOpenFileName", staticmethod(lambda *a, **k: (str(ruta), "")))
        accion(ventana, "Importar Lista de Adyacencia…").trigger()
        assert avisos[0].startswith("No se pudo importar la lista de adyacencia:\nLínea 1:")
        assert vista.modelo.grafo.number_of_edges() == 17


def girar_rueda(vista, punto, pasos):
    lienzo = vista.lienzo
    x, y = lienzo.ejes.transData.transform(punto)
    evento = MouseEvent("scroll_event", lienzo, x, y, button="up" if pasos > 0 else "down", step=pasos)
    lienzo.callbacks.process("scroll_event", evento)


class TestZoom:
    def test_rueda_acerca_alrededor_del_cursor(self, vista):
        punto = posicion(vista, 3)
        pixel_antes = vista.lienzo.ejes.transData.transform(punto)
        girar_rueda(vista, punto, 2)
        x0, x1, _, _ = vista.lienzo.limites
        assert x1 - x0 == pytest.approx(1 / 1.25 ** 2)
        assert vista.lienzo.ejes.transData.transform(punto) == pytest.approx(pixel_antes)

    def test_menu_ver(self, ventana, vista):
        accion(ventana, "Acercar").trigger()
        assert vista.lienzo.ejes.get_xlim()[1] - vista.lienzo.ejes.get_xlim()[0] == pytest.approx(0.8)
        accion(ventana, "Alejar").trigger()
        accion(ventana, "Alejar").trigger()
        assert vista.lienzo.ejes.get_xlim()[1] - vista.lienzo.ejes.get_xlim()[0] == pytest.approx(1.25)
        accion(ventana, "Restablecer Vista").trigger()
        assert vista.lienzo.ejes.get_xlim() == (0.0, 1.0)

    def test_limites_del_zoom(self, vista):
        for _ in range(40):
            vista.lienzo.acercar()
        assert vista.lienzo.limites[1] - vista.lienzo.limites[0] == pytest.approx(0.05)
        for _ in range(40):
            vista.lienzo.alejar()
        assert vista.lienzo.limites[1] - vista.lienzo.limites[0] == pytest.approx(4.0)

    def test_boton_central_desplaza_la_vista(self, vista):
        posiciones = dict(vista.modelo.posiciones)
        mouse(vista, "button_press_event", (0.5, 0.5), MouseButton.MIDDLE)
        mouse(vista, "motion_notify_event", (0.3, 0.5))
        mouse(vista, "button_release_event", (0.3, 0.5), MouseButton.MIDDLE)
        x0, x1, y0, y1 = vista.lienzo.limites
        # Los eventos del mouse llegan en píxeles enteros, así que se admite un error de menos de un píxel.
        assert (x0, x1) == pytest.approx((0.2, 1.2), abs=0.005)
        assert (y0, y1) == pytest.approx((0.0, 1.0), abs=0.005)
        assert vista.modelo.posiciones == posiciones

    def test_clics_y_dibujo_siguen_funcionando_con_zoom(self, vista):
        girar_rueda(vista, posicion(vista, 3), 3)
        clic(vista, posicion(vista, 3))
        assert vista.seleccionado == 3
        vista.ejecutar_bfs(1)  # redibujar conserva el zoom
        assert vista.lienzo.ejes.get_xlim()[1] - vista.lienzo.ejes.get_xlim()[0] == pytest.approx(1 / 1.25 ** 3)

    def test_clic_fuera_del_area_no_crea_nodos(self, vista):
        vista.lienzo.alejar()
        vista.lienzo.alejar()
        clic(vista, (1.2, 0.5))
        assert vista.modelo.grafo.number_of_nodes() == 8


def claridad_de_la_ventana(app):
    return app.palette().color(QPalette.ColorRole.Window).lightness()


class TestTema:
    def test_activar_y_desactivar_desde_el_menu(self, app, ventana, vista):
        accion(ventana, "Tema Oscuro").trigger()
        try:
            assert ventana.accion_tema_oscuro.isChecked()
            assert claridad_de_la_ventana(app) < 100
            assert to_hex(vista.lienzo.figure.get_facecolor()) == TEMAS["oscuro"]["fondo"]
            assert ventana.configuracion.value(CLAVE_TEMA_OSCURO, type=bool)
        finally:
            accion(ventana, "Tema Oscuro").trigger()
        assert not ventana.configuracion.value(CLAVE_TEMA_OSCURO, type=bool)
        assert claridad_de_la_ventana(app) > 150
        assert to_hex(vista.lienzo.figure.get_facecolor()) == "#ffffff"

    def test_se_recuerda_al_abrir(self, app, avisos, tmp_path):
        preferencias = preferencias_temporales(tmp_path)
        preferencias.setValue(CLAVE_TEMA_OSCURO, True)
        ventana = MainWindow(preferencias)
        try:
            assert ventana.accion_tema_oscuro.isChecked()
            assert ventana.panel_vista.lienzo.tema is TEMAS["oscuro"]
        finally:
            ventana.aplicar_tema(False)
            ventana.close()

    def test_leyenda_con_colores_del_tema(self, ventana, vista):
        vista.ejecutar_bfs(1)
        ventana.aplicar_tema(True, guardar=False)
        try:
            estilos = [muestra.styleSheet() for muestra in vista.leyenda.findChildren(QtWidgets.QLabel)]
            assert any(TEMAS["oscuro"]["colores"]["blue"] in estilo for estilo in estilos)
        finally:
            ventana.aplicar_tema(False, guardar=False)

    def test_cambiar_tema_borra_el_aviso_pendiente(self, ventana, vista):
        vista.eliminar_nodo(8)
        assert ventana.statusBar().currentMessage() == "Eliminar nodo 8"
        ventana.aplicar_tema(True, guardar=False)
        try:
            assert ventana.statusBar().currentMessage() == ""
        finally:
            ventana.aplicar_tema(False, guardar=False)

    def test_abrir_no_guarda_preferencias(self, ventana):
        assert ventana.configuracion.allKeys() == []


class TestExportar:
    def test_sin_resultado_no_se_puede_exportar(self, vista):
        assert not vista.panel_info.btn_exportar.isEnabled()
        vista.ejecutar_bfs(1)
        assert vista.panel_info.btn_exportar.isEnabled()

    def test_csv(self, ventana, vista, tmp_path, monkeypatch):
        vista.ejecutar_dijkstra(1)
        ruta = tmp_path / "pasos.csv"
        monkeypatch.setattr(QtWidgets.QFileDialog, "getSaveFileName", staticmethod(lambda *a, **k: (str(ruta), "")))
        accion(ventana, "Exportar Pasos…").trigger()
        with open(ruta, encoding="utf-8-sig", newline="") as archivo:
            filas = list(csv.reader(archivo))
        assert filas[0] == ["Paso", "Descripción"]
        assert filas[1] == ["1", vista.pasos[0].descripcion]
        assert len([fila for fila in filas if len(fila) == 2]) == len(vista.pasos) + 1
        assert ["Nodo", "Distancia", "Anterior"] in filas
        assert ["6", "10", "3"] in filas

    def test_texto(self, vista, tmp_path):
        vista.ejecutar_kruskal()
        ruta = tmp_path / "pasos.txt"
        vista.panel_info.guardar(ruta)
        contenido = ruta.read_text(encoding="utf-8")
        assert contenido.startswith(f"{panel_vista.KRUSKAL}\nÁrbol de expansión mínima: 7 aristas, peso total 26.\n")
        assert f"{len(vista.pasos)}. " in contenido
        assert "Distancias finales" not in contenido


def test_traducciones_de_qt_al_espanol(app):
    traductor = instalar_traducciones(app)
    try:
        botones = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        assert traductor is None or botones.buttons()[0].text() == "Aceptar"
    finally:
        if traductor is not None:
            app.removeTranslator(traductor)


class TestBarraDeEstado:
    def test_selector_de_tipo_visible(self, vista):
        assert vista.grupo_tipo.isVisibleTo(vista)

    def test_ayuda_segun_el_modo(self, ventana, vista):
        assert ventana.etiqueta_ayuda.text() == panel_vista.AYUDA_MODO_NODO
        vista.rb_dibujar_arista.setChecked(True)
        assert ventana.etiqueta_ayuda.text() == panel_vista.AYUDA_ARISTA_ORIGEN
        clic(vista, posicion(vista, 2))
        assert ventana.etiqueta_ayuda.text() == panel_vista.AYUDA_ARISTA_DESTINO.format(nodo=2)

    def test_aviso_tras_cada_cambio(self, ventana, vista):
        vista.eliminar_nodo(8)
        assert ventana.statusBar().currentMessage() == "Eliminar nodo 8"
