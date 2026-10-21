# Visualizador de Grafos y Algoritmos de recorridos

## Graficador de grafos con recorridos: BFS, DFS, Kruskal y Dijkstra
Este proyecto es una aplicación gráfica desarrollada en Python utilizando las bibliotecas PyQt6 y NetworkX. La aplicación permite visualizar y manipular grafos y ejecutar algoritmos comunes sobre ellos, como BFS, DFS, Kruskal y Dijkstra.

## Características principales
- **Interfaz gráfica intuitiva**: La aplicación cuenta con una interfaz gráfica que permite a los usuarios dibujar nodos y aristas con peso.
- **Grafos dirigidos y no dirigidos**: Desde la interfaz se trabaja con grafos no dirigidos. Los grafos dirigidos se pueden cargar desde un archivo JSON (`"graph_type": "Directed"`).

## Algoritmos de grafos
La aplicación implementa varios algoritmos de grafos, incluyendo:
- **BFS (Búsqueda en anchura)**
- **DFS (Búsqueda en profundidad)**
- **Kruskal (Árbol de expansión mínima)**, solo para grafos no dirigidos
- **Dijkstra (Camino más corto)**, con pesos no negativos

## Guardado y carga de grafos
Los grafos pueden ser guardados y cargados en formato JSON, lo que permite a los usuarios guardar su trabajo y continuar en otra sesión.

## Exportación de imágenes
Los grafos pueden ser exportados como imágenes en formato PNG.

## Manipulación de nodos y aristas
Los usuarios pueden agregar y eliminar nodos, agregar aristas con peso y resaltar en azul el recorrido calculado por cada algoritmo.

## Requisitos
- **Python 3.9 o superior**
- **PyQt6**
- **NetworkX**
- **Matplotlib**

Instalación de dependencias:

```bash
pip install -r requirements.txt
```

## Estructura del código
El código está separado en tres capas: los algoritmos y el modelo no dependen de la interfaz gráfica, por lo que se pueden probar y reutilizar por separado.

```
Graficador.py            Punto de entrada
algoritmos/              Funciones puras sobre grafos de NetworkX
  recorridos.py          bfs, dfs
  arbol_minimo.py        kruskal
  camino_minimo.py       dijkstra
modelo/grafo.py          ModeloGrafo: nodos, posiciones, colores, guardado y carga
ui/                      Interfaz PyQt6
  ventana_principal.py   MainWindow: menús y panel lateral
  panel_vista.py         PanelVista: controles de edición y ejecución de algoritmos
  lienzo.py              Lienzo: dibuja el grafo con matplotlib y emite los clics
  panel_informacion.py   PanelInformacion: pasos del último algoritmo
  dialogos.py            Diálogos para ingresar nodos y aristas
datos/                   Grafo de prueba (Nodos.txt, Aristas.txt)
tests/                   Pruebas con pytest
```

## Uso
- **Dibujar nodos**: Selecciona la opción "Dibujar Nodo" y haz clic en el lienzo para agregar nodos.

- **Dibujar aristas**: Selecciona la opción "Dibujar Arista", pulsa "Ingresar Puntos" e indica el nodo padre, el nodo hijo y el peso (entero no negativo).

- **Ejecutar algoritmos**: Selecciona un algoritmo del menú "Algoritmos" y sigue las instrucciones para ejecutarlo.

- **Grafo de prueba**: En el menú "Grafos" la opción "Grafo de Prueba" carga el grafo definido en `datos/Nodos.txt` y `datos/Aristas.txt`.

- **Guardar y cargar grafos**: Utiliza las opciones del menú "Archivo" para guardar o cargar un grafo en formato JSON.

- **Exportar imagen**: Utiliza la opción "Guardar Imagen" para exportar el grafo como una imagen PNG.

## Ejecución
Para ejecutar la aplicación, ejecuta el archivo principal:

```bash
python Graficador.py
```

## Pruebas
Los algoritmos se comparan contra las implementaciones de NetworkX; también hay pruebas del modelo y pruebas de humo de la interfaz (se ejecutan sin abrir ventanas).

```bash
pip install -r requirements-dev.txt
pytest
```

## Contribuciones
Si deseas contribuir a este proyecto, siéntete libre de hacer un fork y enviar un pull request. Cualquier mejora, corrección de errores o nueva funcionalidad es bienvenida.

## Licencia
Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.
