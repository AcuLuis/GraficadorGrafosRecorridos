from PyQt6.QtGui import QUndoCommand


class ComandoModelo(QUndoCommand):
    """Cambio ya aplicado al modelo, que se deshace y rehace restaurando instantáneas.

    El cambio se aplica antes de crear el comando para poder informar errores al usuario;
    por eso el primer ``redo()``, que ``QUndoStack.push`` llama automáticamente, no hace nada.
    """

    def __init__(self, descripcion, modelo, antes, despues, al_cambiar):
        super().__init__(descripcion)
        self.modelo = modelo
        self.antes = antes
        self.despues = despues
        self.al_cambiar = al_cambiar
        self._ya_aplicado = True

    def redo(self):
        if self._ya_aplicado:
            self._ya_aplicado = False
            return
        self.modelo.restaurar(self.despues)
        self.al_cambiar()

    def undo(self):
        self.modelo.restaurar(self.antes)
        self.al_cambiar()
