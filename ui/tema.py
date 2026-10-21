from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette

# Colores del lienzo para cada tema. "colores" reemplaza al dibujar los colores de COLORES que
# no se distinguirían bien sobre el fondo (por ejemplo, aristas negras sobre fondo oscuro).
TEMAS = {
    "claro": {"fondo": "white", "marco": "black", "texto": "black", "panel": "lightblue", "colores": {}},
    "oscuro": {
        "fondo": "#1e1e1e",
        "marco": "#bbbbbb",
        "texto": "#e0e0e0",
        "panel": "#2d4a5a",
        "colores": {"black": "#c8c8c8", "blue": "#4f9dff", "#a0a0a0": "#808080"},
    },
}


def color_en_tema(tema, color):
    return tema["colores"].get(color, color)


def paleta_oscura():
    paleta = QPalette()
    fondo, base, texto = QColor(45, 45, 48), QColor(30, 30, 30), QColor(220, 220, 220)
    resalte, apagado = QColor(42, 130, 218), QColor(127, 127, 127)
    for rol, color in [
        (QPalette.ColorRole.Window, fondo), (QPalette.ColorRole.WindowText, texto),
        (QPalette.ColorRole.Base, base), (QPalette.ColorRole.AlternateBase, fondo),
        (QPalette.ColorRole.ToolTipBase, base), (QPalette.ColorRole.ToolTipText, texto),
        (QPalette.ColorRole.Text, texto), (QPalette.ColorRole.Button, fondo),
        (QPalette.ColorRole.ButtonText, texto), (QPalette.ColorRole.BrightText, QColor(Qt.GlobalColor.red)),
        (QPalette.ColorRole.Link, resalte), (QPalette.ColorRole.Highlight, resalte),
        (QPalette.ColorRole.HighlightedText, QColor(Qt.GlobalColor.white)),
        (QPalette.ColorRole.PlaceholderText, apagado),
    ]:
        paleta.setColor(rol, color)
    for rol in (QPalette.ColorRole.Text, QPalette.ColorRole.ButtonText, QPalette.ColorRole.WindowText):
        paleta.setColor(QPalette.ColorGroup.Disabled, rol, apagado)
    return paleta
