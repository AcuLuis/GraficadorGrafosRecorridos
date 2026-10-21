"""Lectura y escritura de listas de adyacencia en texto.

Formato: una línea por nodo; se ignoran las líneas vacías y lo que sigue a ``#``.

    dirigido              # opcional: "dirigido" o "no dirigido" (por defecto)
    1: 2(10), 3(6), 7
    2: 4(5)
    5:

Cada línea es ``nodo: vecino(peso), vecino(peso), ...``. El peso es opcional (por defecto 1)
y puede ser negativo; los vecinos se separan con comas o espacios. Los nodos son enteros positivos.
En un grafo no dirigido una arista puede aparecer en ambos nodos, pero con el mismo peso.
"""
import re

_VECINO = re.compile(r"(\d+)(?:\((-?\d+)\))?")
TIPOS = {"dirigido": True, "no dirigido": False}


def leer_lista_adyacencia(texto):
    """Devuelve ``(dirigido, nodos, aristas)``, con ``aristas`` como ``(origen, destino, peso)``.

    Lanza ``ValueError`` indicando la línea con el problema si el texto no respeta el formato.
    """
    dirigido = False
    nodos = {}
    aristas = {}
    for numero, linea in enumerate(texto.splitlines(), 1):
        linea = linea.split("#", 1)[0].strip()
        if not linea:
            continue
        if linea.lower() in TIPOS:
            if nodos:
                raise ValueError(f"Línea {numero}: el tipo de grafo debe indicarse antes de los nodos.")
            dirigido = TIPOS[linea.lower()]
            continue
        if ":" not in linea:
            raise ValueError(f"Línea {numero}: falta «:» después del nodo (formato: nodo: vecino(peso), ...).")
        cabeza, resto = linea.split(":", 1)
        nodo = _nodo(cabeza.strip(), numero)
        nodos.setdefault(nodo, None)
        for texto_vecino in resto.replace(",", " ").split():
            coincidencia = _VECINO.fullmatch(texto_vecino)
            if coincidencia is None:
                raise ValueError(f"Línea {numero}: «{texto_vecino}» no es un vecino válido; usa nodo o nodo(peso).")
            vecino = _nodo(coincidencia.group(1), numero)
            peso = int(coincidencia.group(2)) if coincidencia.group(2) else 1
            if vecino == nodo:
                raise ValueError(f"Línea {numero}: el nodo {nodo} no puede ser vecino de sí mismo.")
            nodos.setdefault(vecino, None)
            clave = (nodo, vecino) if dirigido else frozenset((nodo, vecino))
            if clave in aristas and aristas[clave][2] != peso:
                raise ValueError(f"Línea {numero}: la arista {nodo}-{vecino} aparece con pesos distintos "
                                 f"({aristas[clave][2]} y {peso}).")
            aristas.setdefault(clave, (nodo, vecino, peso))
    return dirigido, list(nodos), list(aristas.values())


def escribir_lista_adyacencia(grafo):
    """Texto con la lista de adyacencia de ``grafo``, que ``leer_lista_adyacencia`` vuelve a leer igual."""
    lineas = ["dirigido" if grafo.is_directed() else "no dirigido"]
    for nodo in sorted(grafo.nodes, key=str):
        vecinos = sorted(grafo.neighbors(nodo), key=str)
        lineas.append(f"{nodo}: " + ", ".join(f"{vecino}({grafo[nodo][vecino].get('weight', 1)})" for vecino in vecinos))
    return "\n".join(linea.rstrip() for linea in lineas) + "\n"


def _nodo(texto, numero):
    if not texto.isdigit() or int(texto) == 0:
        raise ValueError(f"Línea {numero}: «{texto}» no es un nodo válido (debe ser un entero positivo).")
    return int(texto)
