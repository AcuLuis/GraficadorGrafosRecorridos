"""Genera un ejecutable de la aplicación con PyInstaller.

Uso (con las dependencias de desarrollo instaladas: ``pip install -r requirements-dev.txt``)::

    python empaquetar.py

El resultado queda en ``dist/GraficadorGrafos/``: se puede copiar esa carpeta completa a otra
computadora con el mismo sistema operativo y abrir ``GraficadorGrafos`` sin instalar Python.
Cualquier argumento extra se pasa a PyInstaller (por ejemplo ``--onefile``).
"""
import os
import sys
from pathlib import Path

import PyInstaller.__main__

RAIZ = Path(__file__).resolve().parent
NOMBRE = "GraficadorGrafos"


def main():
    PyInstaller.__main__.run([
        str(RAIZ / "Graficador.py"),
        "--name", NOMBRE,
        "--windowed",
        "--noconfirm",
        "--clean",
        "--add-data", f"{RAIZ / 'datos'}{os.pathsep}datos",
        "--distpath", str(RAIZ / "dist"),
        "--workpath", str(RAIZ / "build"),
        "--specpath", str(RAIZ / "build"),
        *sys.argv[1:],
    ])


if __name__ == "__main__":
    main()
