@echo off
rem Abre el Graficador de Grafos en Windows.
rem La primera vez crea un entorno virtual (.venv) dentro del proyecto e instala las dependencias.
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Creando el entorno virtual .venv ...
    py -3 -m venv .venv 2>nul
    if not exist ".venv\Scripts\python.exe" python -m venv .venv
    if not exist ".venv\Scripts\python.exe" (
        echo No se encontro Python 3. Instalalo desde https://www.python.org/downloads/ y vuelve a intentarlo.
        pause
        exit /b 1
    )
)

echo Verificando dependencias ...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -q -r requirements.txt
if errorlevel 1 (
    echo No se pudieron instalar las dependencias. Revisa tu conexion a internet.
    pause
    exit /b 1
)

start "" ".venv\Scripts\pythonw.exe" Graficador.py
