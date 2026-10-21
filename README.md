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
El código está organizado en varias clases principales:

- **Lienzo**: Esta clase maneja la visualización del grafo y la interacción con el usuario. Se encarga de dibujar los nodos y aristas, así como de manejar eventos como clics del mouse.
- **MainWindow**: Es la ventana principal de la aplicación. Contiene los menús y el panel lateral, y pide los datos necesarios para ejecutar cada algoritmo.
- **PanelVista**: Es un widget que contiene el lienzo donde se dibuja el grafo, los controles para interactuar con él y la lógica de los algoritmos.
- **Panel**: Es un panel lateral que muestra información sobre los algoritmos ejecutados, como los pasos de BFS, DFS, etc.

## Uso
- **Dibujar nodos**: Selecciona la opción "Dibujar Nodo" y haz clic en el lienzo para agregar nodos.

- **Dibujar aristas**: Selecciona la opción "Dibujar Arista", pulsa "Ingresar Puntos" e indica el nodo padre, el nodo hijo y el peso (entero no negativo).

- **Ejecutar algoritmos**: Selecciona un algoritmo del menú "Algoritmos" y sigue las instrucciones para ejecutarlo.

- **Grafo de prueba**: En el menú "Grafos" la opción "Grafo de Prueba" carga el grafo definido en `Nodos.txt` y `Aristas.txt`.

- **Guardar y cargar grafos**: Utiliza las opciones del menú "Archivo" para guardar o cargar un grafo en formato JSON.

- **Exportar imagen**: Utiliza la opción "Guardar Imagen" para exportar el grafo como una imagen PNG.

## Ejecución
Para ejecutar la aplicación, ejecuta el archivo principal:

```bash
python Graficador.py
```

## Contribuciones
Si deseas contribuir a este proyecto, siéntete libre de hacer un fork y enviar un pull request. Cualquier mejora, corrección de errores o nueva funcionalidad es bienvenida.

## Licencia
Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.
