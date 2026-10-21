import math

PESO_POR_DEFECTO = 1


def validar_inicio(grafo, inicio):
    if inicio not in grafo:
        raise ValueError(f"El nodo {inicio} no existe en el grafo.")


def peso(grafo, origen, destino):
    return grafo[origen][destino].get("weight", PESO_POR_DEFECTO)


def cantidad(numero, singular, plural):
    return f"{numero} {singular if numero == 1 else plural}"


def formatear_distancia(distancia):
    return "∞" if distancia == math.inf else str(distancia)
