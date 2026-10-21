# Visualizador de Grafos y Algoritmos de recorridos

## Graficador de grafos con recorridos: BFS, DFS, Kruskal y Dijkstra
Este proyecto es una aplicación gráfica desarrollada en Python utilizando las bibliotecas PyQt6 y NetworkX. La aplicación permite visualizar y manipular grafos y ejecutar algoritmos comunes sobre ellos, como BFS, DFS, Kruskal y Dijkstra.

## Características principales
- **Edición directa con el mouse**: crear nodos con un clic, unirlos con aristas haciendo clic en el origen y el destino, arrastrarlos para moverlos y usar el clic derecho para editar pesos o eliminar elementos.
- **Grafos dirigidos y no dirigidos**: se elige el tipo desde la cabecera de la ventana.
- **Deshacer y rehacer**: todas las ediciones del grafo se pueden deshacer (Ctrl+Z) y rehacer (Ctrl+Y).
- **Resultados que se actualizan solos**: al editar el grafo se vuelve a calcular el último algoritmo ejecutado.

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
  lienzo.py              Lienzo: dibuja el grafo y traduce el mouse en acciones sobre nodos y aristas
  panel_informacion.py   PanelInformacion: pasos del último algoritmo
  comandos.py            Comandos de deshacer/rehacer (QUndoStack)
  dialogos.py            Diálogos para elegir nodos e ingresar aristas y pesos
datos/                   Grafo de prueba (Nodos.txt, Aristas.txt)
tests/                   Pruebas con pytest
```

## Uso
La barra de estado, en la parte inferior de la ventana, muestra en todo momento qué hace cada clic en el modo actual.

- **Dibujar nodos**: con "Dibujar Nodo" activo, haz clic en un espacio vacío del lienzo. Haz clic en un nodo para seleccionarlo (se resalta en naranja) y arrástralo para moverlo.
- **Dibujar aristas**: con "Dibujar Arista" activo, haz clic en el nodo de origen y luego en el de destino, e indica el peso (entero no negativo). Si la arista ya existe, se actualiza su peso. También puedes usar "Ingresar Arista…" para escribir los nodos y el peso.
- **Editar y eliminar**: clic derecho sobre un nodo para eliminarlo o ejecutar un algoritmo desde él; clic derecho sobre una arista para editar su peso o eliminarla.
- **Ejecutar algoritmos**: elige un algoritmo del menú "Algoritmos". BFS, DFS y Dijkstra piden el nodo inicial en una lista desplegable, que sugiere el nodo seleccionado o el último usado.
- **Recorrido seleccionado**: en el menú "Grafos", conserva solo las aristas del último recorrido calculado.
- **Grafo de prueba**: en el menú "Grafos", carga el grafo definido en `datos/Nodos.txt` y `datos/Aristas.txt`.
- **Guardar y cargar grafos**: opciones del menú "Archivo", en formato JSON.
- **Exportar imagen**: "Guardar Imagen" exporta el grafo como PNG.

### Atajos de teclado

| Acción | Atajo |
| --- | --- |
| Guardar avance / Cargar avance | Ctrl+S / Ctrl+O |
| Guardar imagen | Ctrl+E |
| Deshacer / Rehacer | Ctrl+Z / Ctrl+Y |
| Modo nodo / Modo arista | N / A |
| Cancelar la selección | Esc |
| Eliminar el nodo seleccionado | Supr |
| Limpiar el grafo | Ctrl+L |
| Grafo de prueba / Recorrido seleccionado | Ctrl+T / Ctrl+R |
| BFS / DFS / Kruskal / Dijkstra | Ctrl+1 / Ctrl+2 / Ctrl+3 / Ctrl+4 |

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
