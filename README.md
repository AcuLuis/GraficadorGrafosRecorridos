# Visualizador de Grafos y Algoritmos de recorridos

## Graficador de los grafos con recorridos: BSF, DSF, KRUSKAL y DIJSKTRA.
Este proyecto es una aplicación gráfica desarrollada en Python utilizando las bibliotecas PyQt5 y NetworkX. La aplicación permite visualizar y manipular grafos, tanto dirigidos como no dirigidos, y ejecutar algoritmos comunes sobre ellos, como BFS, DFS, Kruskal y Dijkstra.

## Características principales
- **Interfaz gráfica intuitiva**: La aplicación cuenta con una interfaz gráfica que permite a los usuarios dibujar nodos y aristas, así como seleccionar el tipo de grafo (dirigido o no dirigido).

## Algoritmos de grafos: La aplicación implementa varios algoritmos de grafos, incluyendo:
-**BFS (Búsqueda en anchura)**
-**DFS (Búsqueda en profundidad)**
-**Kruskal (Árbol de expansión mínima)**
-**Dijkstra (Camino más corto)**

## Guardado y carga de grafos:
 Los grafos pueden ser guardados y cargados en formato JSON, lo que permite a los usuarios guardar su trabajo y continuar en otra sesión.

## Exportación de imágenes: 
Los grafos pueden ser exportados como imágenes en formato PNG.

## Manipulación de nodos y aristas:
 Los usuarios pueden agregar, eliminar y modificar nodos y aristas, así como cambiar el color de las aristas para resaltar caminos específicos.

## Requisitos
Para ejecutar esta aplicación, necesitas tener instaladas las siguientes bibliotecas de Python:
- **PyQt5**
- **NetworkX**
- **Matplotlib**

## Estructura del código
El código está organizado en varias clases principales:

- **Lienzo**: Esta clase maneja la visualización del grafo y la interacción con el usuario. Se encarga de dibujar los nodos y aristas, así como de manejar eventos como clics del mouse.
- **MainWindow**: Es la ventana principal de la aplicación. Contiene menús, barras de herramientas y paneles para interactuar con el grafo. También maneja la lógica de los algoritmos de grafos.
- **PanelVista**: Es un widget que contiene el lienzo donde se dibuja el grafo y los controles para interactuar con él.
- **Panel**: Es un panel lateral que muestra información sobre los algoritmos ejecutados, como los pasos de BFS, DFS, etc.

## Uso
- **Dibujar nodos**: Selecciona la opción "Dibujar Nodo" y haz clic en el lienzo para agregar nodos.

- **Dibujar aristas**: Selecciona la opción "Dibujar Arista" y sigue las instrucciones para conectar dos nodos con una arista.

- **Ejecutar algoritmos**: Selecciona un algoritmo del menú "Algoritmos" y sigue las instrucciones para ejecutarlo.

- **Guardar y cargar grafos**: Utiliza las opciones del menú "Archivo" para guardar o cargar un grafo en formato JSON.

- **Exportar imagen**: Utiliza la opción "Guardar Imagen" para exportar el grafo como una imagen PNG.

## Ejecución
Para ejecutar la aplicación, simplemente ejecuta el archivo Python:
`python Graficador.py`

## Contribuciones
Si deseas contribuir a este proyecto, siéntete libre de hacer un fork y enviar un pull request. Cualquier mejora, corrección de errores o nueva funcionalidad es bienvenida.

## Licencia
Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.

