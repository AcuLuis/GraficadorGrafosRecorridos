#!/usr/bin/env sh
# Abre el Graficador de Grafos en Linux o macOS.
# La primera vez crea un entorno virtual (.venv) dentro del proyecto e instala las dependencias.
set -e
cd "$(dirname "$0")"

if [ ! -x .venv/bin/python ]; then
    echo "Creando el entorno virtual .venv ..."
    python3 -m venv .venv
fi

echo "Verificando dependencias ..."
.venv/bin/python -m pip install --disable-pip-version-check -q -r requirements.txt
exec .venv/bin/python Graficador.py "$@"
