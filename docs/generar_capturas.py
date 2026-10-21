"""Abre la aplicación y guarda las capturas de pantalla que usa el README.

Uso, desde la carpeta del proyecto y con las dependencias instaladas::

    python docs/generar_capturas.py            # pausa de 3 segundos en cada pantalla
    python docs/generar_capturas.py --pausa 6  # más tiempo para mirar cada pantalla

La ventana se muestra mientras se preparan las escenas, así se puede revisar cada pantalla
antes de que se guarde. Las imágenes quedan en ``docs/capturas/``. Se usa una configuración
temporal, de modo que las preferencias del usuario (por ejemplo, el tema) no cambian.
"""
import argparse
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from PyQt6.QtCore import QSettings, Qt  # noqa: E402
from PyQt6.QtTest import QTest  # noqa: E402
from PyQt6.QtWidgets import QApplication  # noqa: E402

from ui.ventana_principal import MainWindow, instalar_traducciones  # noqa: E402

CARPETA_CAPTURAS = RAIZ / "docs" / "capturas"
TAMANO_VENTANA = (1280, 800)


def escenas(ventana):
    """Cada escena prepara la ventana y devuelve el nombre del archivo de su captura."""
    vista = ventana.panel_vista

    def camino_mas_corto():
        vista.cargar_grafo_prueba()
        vista.ejecutar_dijkstra(1, 6)
        return "camino_mas_corto.png"

    def paso_a_paso():
        vista.ejecutar_kruskal()
        vista.reproductor.ir_a(9)
        return "paso_a_paso.png"

    def orden_topologico():
        vista.cargar_lista_adyacencia(RAIZ / "datos" / "ejemplo_tareas.txt")
        vista.ejecutar_topologico()
        vista.reproductor.ir_a(7)
        return "orden_topologico.png"

    def tema_oscuro():
        vista.modelo.cambiar_tipo(dirigido=False)  # el grafo de prueba se carga con el tipo actual
        vista.cargar_grafo_prueba()
        vista.ejecutar_bfs(1)
        vista.reproductor.ir_a(5)
        ventana.aplicar_tema(True, guardar=False)
        return "tema_oscuro.png"

    return [camino_mas_corto, paso_a_paso, orden_topologico, tema_oscuro]


def main():
    argumentos = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    argumentos.add_argument("--pausa", type=float, default=3, help="segundos que se muestra cada pantalla")
    opciones = argumentos.parse_args()

    app = QApplication(sys.argv)
    app.styleHints().setColorScheme(Qt.ColorScheme.Light)
    instalar_traducciones(app)
    CARPETA_CAPTURAS.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temporal:
        ventana = MainWindow(QSettings(str(Path(temporal) / "preferencias.ini"), QSettings.Format.IniFormat))
        ventana.resize(*TAMANO_VENTANA)
        ventana.show()
        for escena in escenas(ventana):
            nombre = escena()
            ventana.statusBar().clearMessage()
            QTest.qWait(int(opciones.pausa * 1000))
            ventana.grab().save(str(CARPETA_CAPTURAS / nombre), "PNG")
            print(f"Guardada docs/capturas/{nombre}")
        ventana.close()


if __name__ == "__main__":
    main()
