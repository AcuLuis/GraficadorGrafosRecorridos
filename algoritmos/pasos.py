from dataclasses import dataclass


@dataclass(frozen=True)
class Paso:
    """Estado de un algoritmo después de un paso, para describirlo o animarlo.

    - ``actual``: nodo que se está procesando.
    - ``frontera``: nodos que esperan ser procesados (cola, pila o cola de prioridad).
    - ``visitados``: nodos ya procesados (en Kruskal, los que ya forman parte del árbol).
    - ``aristas``: aristas elegidas hasta ahora (recorrido, árbol o camino), como ``(origen, destino)``.
    - ``arista_actual``: arista examinada en este paso.
    - ``descartadas``: aristas descartadas (en Kruskal, las que formarían un ciclo).
    - ``distancias`` y ``anteriores``: distancia y predecesor de cada nodo (Dijkstra y Bellman-Ford).
    - ``ciclo``: aristas de un ciclo encontrado (un ciclo negativo, o el ciclo que impide un orden topológico).
    """

    descripcion: str
    actual: object = None
    frontera: tuple = ()
    visitados: frozenset = frozenset()
    aristas: tuple = ()
    arista_actual: tuple = None
    descartadas: tuple = ()
    distancias: dict = None
    anteriores: dict = None
    ciclo: tuple = ()
