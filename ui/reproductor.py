from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QSlider, QStyle, QToolButton, QWidget

VELOCIDADES = [("0.5x", 0.5), ("1x", 1), ("2x", 2), ("4x", 4)]
VELOCIDAD_INICIAL = 1
INTERVALO_BASE_MS = 900


class Reproductor(QWidget):
    """Controles para recorrer los pasos de un algoritmo: ir al inicio o al final, paso anterior
    y siguiente, reproducción automática con velocidad ajustable y un deslizador.

    Emite ``paso_cambiado(indice)`` cada vez que cambia el paso mostrado.
    """

    paso_cambiado = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.total = 0
        self.indice = 0
        self.temporizador = QTimer(self)
        self.temporizador.timeout.connect(self._avanzar_automaticamente)

        iconos = QStyle.StandardPixmap
        self.btn_inicio = self._boton(iconos.SP_MediaSkipBackward, "Primer paso", self.primero)
        self.btn_anterior = self._boton(iconos.SP_MediaSeekBackward, "Paso anterior", self.anterior)
        self.btn_reproducir = self._boton(iconos.SP_MediaPlay, "Reproducir", self.alternar_reproduccion)
        self.btn_siguiente = self._boton(iconos.SP_MediaSeekForward, "Paso siguiente", self.siguiente)
        self.btn_fin = self._boton(iconos.SP_MediaSkipForward, "Último paso", self.ultimo)
        self.deslizador = QSlider(Qt.Orientation.Horizontal)
        self.deslizador.valueChanged.connect(self.elegir)
        self.lbl_paso = QLabel()
        self.cmb_velocidad = QComboBox()
        self.cmb_velocidad.addItems([texto for texto, _ in VELOCIDADES])
        self.cmb_velocidad.setCurrentIndex(VELOCIDAD_INICIAL)
        self.cmb_velocidad.currentIndexChanged.connect(self._actualizar_intervalo)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        for widget in (self.btn_inicio, self.btn_anterior, self.btn_reproducir, self.btn_siguiente, self.btn_fin):
            layout.addWidget(widget)
        layout.addWidget(self.deslizador, 1)
        layout.addWidget(self.lbl_paso)
        layout.addWidget(QLabel("Velocidad:"))
        layout.addWidget(self.cmb_velocidad)
        self._actualizar_intervalo()
        self.limpiar()

    def _boton(self, icono, consejo, funcion):
        boton = QToolButton()
        boton.setIcon(self.style().standardIcon(icono))
        boton.setToolTip(consejo)
        boton.clicked.connect(lambda *_: funcion())
        return boton

    @property
    def reproduciendo(self):
        return self.temporizador.isActive()

    def cargar(self, total, indice=None):
        """Prepara ``total`` pasos y muestra el indicado (por defecto, el último)."""
        self.pausar()
        self.total = total
        self.deslizador.blockSignals(True)
        self.deslizador.setRange(0, max(total - 1, 0))
        self.deslizador.blockSignals(False)
        self.setEnabled(total > 0)
        self.ir_a(total - 1 if indice is None else indice)

    def limpiar(self):
        self.pausar()
        self.total = 0
        self.indice = 0
        self.deslizador.blockSignals(True)
        self.deslizador.setRange(0, 0)
        self.deslizador.blockSignals(False)
        self.lbl_paso.setText("Sin pasos")
        self.setEnabled(False)

    def ir_a(self, indice):
        if not self.total:
            return
        self.indice = max(0, min(indice, self.total - 1))
        self.deslizador.blockSignals(True)
        self.deslizador.setValue(self.indice)
        self.deslizador.blockSignals(False)
        self.lbl_paso.setText(f"Paso {self.indice + 1} de {self.total}")
        self.btn_inicio.setEnabled(self.indice > 0)
        self.btn_anterior.setEnabled(self.indice > 0)
        self.btn_siguiente.setEnabled(self.indice < self.total - 1)
        self.btn_fin.setEnabled(self.indice < self.total - 1)
        self.paso_cambiado.emit(self.indice)

    # Navegación manual: detiene la reproducción automática.

    def primero(self):
        self.pausar()
        self.ir_a(0)

    def anterior(self):
        self.pausar()
        self.ir_a(self.indice - 1)

    def siguiente(self):
        self.pausar()
        self.ir_a(self.indice + 1)

    def ultimo(self):
        self.pausar()
        self.ir_a(self.total - 1)

    def elegir(self, indice):
        self.pausar()
        self.ir_a(indice)

    # Reproducción automática

    def alternar_reproduccion(self):
        if self.reproduciendo:
            self.pausar()
        else:
            self.reproducir()

    def reproducir(self):
        if self.total < 2:
            return
        if self.indice >= self.total - 1:
            self.ir_a(0)
        self.temporizador.start()
        self.btn_reproducir.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        self.btn_reproducir.setToolTip("Pausar")

    def pausar(self):
        self.temporizador.stop()
        self.btn_reproducir.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.btn_reproducir.setToolTip("Reproducir")

    def _avanzar_automaticamente(self):
        self.ir_a(self.indice + 1)
        if self.indice >= self.total - 1:
            self.pausar()

    def _actualizar_intervalo(self, *_):
        factor = VELOCIDADES[self.cmb_velocidad.currentIndex()][1]
        self.temporizador.setInterval(int(INTERVALO_BASE_MS / factor))
