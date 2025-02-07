#grafo={(1, 2): 1, (1, 3): 1, (1, 4): 1, (1, 5): 1, (2, 6): 1, (5, 6): 1}
class Operaciones:
    def getVecinos(grafo,nodo):
        vecinos = []
        for arista, peso in grafo.items():
            if(arista[0]==nodo):
                vecinos.append(arista[1])
            if(arista[1]==nodo):
                vecinos.append(arista[0])
        return vecinos
    def getSortAristas(grafo):
     listGrafo=list(grafo.items())
     for i in range(len(listGrafo)):
        for j in range(len(listGrafo)-i-1):
         x=listGrafo[j][1]
         y=listGrafo[j+1][1]
         if(x>y):
            arista,peso=listGrafo[j]
            listGrafo[j]=listGrafo[j+1]
            listGrafo[j+1]=(arista,peso)
     return list(listGrafo)