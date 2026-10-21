#grafo={(1, 2): 1, (1, 3): 1, (1, 4): 1, (1, 5): 1, (2, 6): 1, (5, 6): 1}
class Operaciones:
    def getSortAristas(grafo):
        return sorted(grafo.items(), key=lambda item: item[1])
