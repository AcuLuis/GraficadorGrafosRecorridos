from dataclasses import dataclass, field

# Colores de nodos y aristas. "recorrido" coincide con el color que guarda el modelo
# para las aristas del resultado, de modo que el último paso se ve igual que el resultado.
COLORES = {
    "normal": "#1f78b4",
    "seleccionado": "#ff7f0e",
    "actual": "#d62728",
    "espera": "#f2c12e",
    "visitado": "#2ca02c",
    "arista": "black",
    "recorrido": "blue",
    "examinada": "#d62728",
    "descartada": "#a0a0a0",
}
CLAVES_DE_ARISTA = {"arista", "recorrido", "examinada", "descartada"}
COLORES_DESTACADOS = {COLORES["recorrido"], COLORES["examinada"]}

LEYENDAS = {
    "bfs": [("actual", "Nodo actual"), ("espera", "En la cola"), ("visitado", "Procesado"),
            ("examinada", "Arista revisada"), ("recorrido", "Arista del recorrido")],
    "dfs": [("actual", "Nodo actual"), ("espera", "En la pila"), ("visitado", "Terminado"),
            ("examinada", "Arista revisada"), ("recorrido", "Arista del recorrido")],
    "kruskal": [("visitado", "Nodo en el árbol"), ("examinada", "Arista revisada"),
                ("recorrido", "Arista del árbol"), ("descartada", "Descartada (ciclo)")],
    "dijkstra": [("actual", "Nodo actual"), ("espera", "En la cola de prioridad"), ("visitado", "Distancia fijada"),
                 ("examinada", "Arista revisada"), ("recorrido", "Arista de camino mínimo")],
}


@dataclass
class EstiloVista:
    """Colores con los que se dibuja un paso. Lo que no aparece usa el color normal."""

    nodos: dict = field(default_factory=dict)
    aristas: dict = field(default_factory=dict)
    discontinuas: set = field(default_factory=set)


def estilo_de_paso(paso, dirigido):
    estilo = EstiloVista()
    for nodo in paso.visitados:
        estilo.nodos[nodo] = COLORES["visitado"]
    for nodo in paso.frontera:
        estilo.nodos[nodo] = COLORES["espera"]
    if paso.actual is not None:
        estilo.nodos[paso.actual] = COLORES["actual"]

    def pintar(arista, color):
        estilo.aristas[arista] = color
        if not dirigido:
            estilo.aristas[arista[::-1]] = color

    for arista in paso.aristas:
        pintar(arista, COLORES["recorrido"])
    for arista in paso.descartadas:
        pintar(arista, COLORES["descartada"])
        estilo.discontinuas.update((arista, arista[::-1]))
    if paso.arista_actual is not None:
        pintar(paso.arista_actual, COLORES["examinada"])
    return estilo
