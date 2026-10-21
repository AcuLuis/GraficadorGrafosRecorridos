"""Pruebas de humo de la interfaz, sin ventana visible."""
import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from matplotlib.backend_bases import MouseButton, MouseEvent  # noqa: E402

from ui import panel_vista  # noqa: E402
from ui.estilos import COLORES  # noqa: E402
from ui.ventana_principal import MainWindow  # noqa: E402

ESQUINA_VACIA = (0.02, 0.98)


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
def ventana(app, avisos):
    ventana = MainWindow()
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
        accion(ventana, panel_vista.DIJKSTRA).trigger()
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
        ("Reproducir / Pausar", "Ctrl+P"), ("Paso Anterior", "Ctrl+Left"), ("Paso Siguiente", "Ctrl+Right"),
        ("Primer Paso", "Ctrl+Home"), ("Último Paso", "Ctrl+End"),
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
