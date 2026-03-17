# widgets/oscilloscope_widget.py
# Osciloscopio estilo LabVolt / Windows 95 (solo visual por ahora)

from PySide6 import QtWidgets, QtGui, QtCore
import math
from widgets.channel_control_widget import ChannelControlWidget


class OscilloscopeGrid(QtWidgets.QWidget):
    """
    Área de dibujo del osciloscopio:
    - 10 columnas x 8 filas
    - 5 subdivisiones por cuadro
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.phase = 0
        self.time_scale = 1
        self.channel_data = []
        #self.setMinimumSize(520, 420)
        #self.setStyleSheet("background: #008b8b;")

        self.trigger_level = 0
        self.trigger_enabled = True

        self.cursor1 = 200
        self.cursor2 = 400

        self.real_signals = None

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), QtGui.QColor("#008b8b"))
        #fade = QtGui.QColor(0, 40, 40, 40)
        #painter.fillRect(self.rect(), fade)

        painter.setRenderHint(QtGui.QPainter.Antialiasing, False)

        w = self.width()
        h = self.height()

        cols = 10
        rows = 8
        sub = 5

        col_w = w / cols
        row_h = h / rows

        # Líneas principales
        pen_main = QtGui.QPen(QtGui.QColor("#b2ffff"))
        pen_main.setWidth(0.5)
        painter.setPen(pen_main)

        for c in range(cols + 1):
            x = c * col_w
            painter.drawLine(int(x), 0, int(x), h)

        for r in range(rows + 1):
            y = r * row_h
            painter.drawLine(0, int(y), w, int(y))

        # Cruz central (líneas principales)
        pen_center = QtGui.QPen(QtGui.QColor("white"))
        pen_center.setWidth(1.5)
        painter.setPen(pen_center)

        cx = w // 2
        cy = h // 2

        painter.drawLine(cx, 0, cx, h)
        painter.drawLine(0, cy, w, cy)

        # Subdivisiones de la cruz central
        pen_sub = QtGui.QPen(QtGui.QColor("white"))
        pen_sub.setWidth(1)
        painter.setPen(pen_sub)

        subdivisions = 5            # cantidad de subdivisiones por división
        tick_size = 4               # tamaño de cada marca
        col_w = w / 10              # 10 divisiones horizontales
        row_h = h / 8               # 8 divisiones verticales

        # Subdivisiones horizontales sobre la línea vertical central
        for i in range(1, 10 * subdivisions):
            y = int(i * (row_h / subdivisions))
            painter.drawLine(cx - tick_size, y, cx + tick_size, y)

        # Subdivisiones verticales sobre la línea horizontal central
        for i in range(1, 10 * subdivisions):
            x = int(i * (col_w / subdivisions))
            painter.drawLine(x, cy - tick_size, x, cy + tick_size)

        # -------------------------
        # Señal de prueba
        # -------------------------
        
        '''pen_signal = QtGui.QPen(QtGui.QColor(0,255,0))
        pen_signal.setWidth(2)
        painter.setPen(pen_signal)

        points = []

        amplitude = h / 4
        center = h / 2

        for x in range(w):

            t = (x / w) * 4 * math.pi * self.time_scale

            y = center + amplitude * math.sin(t + self.phase)

            points.append(QtCore.QPointF(x, y))

        painter.drawPolyline(points)'''

        
        colors = [
            QtGui.QColor("green"),
            QtGui.QColor("yellow"),
            QtGui.QColor("violet"),
            QtGui.QColor("red"),
            QtGui.QColor("orange"),
            QtGui.QColor("blue"),
            QtGui.QColor("black"),
            QtGui.QColor("brown")
            ]

        center = h / 2

        trigger_y = center + self.trigger_level

        amplitude = h / 4

        for i, ch in enumerate(self.channel_data):

            entry = ch["entry"]

            if entry == "Ninguna":
             continue

            pen = QtGui.QPen(colors[i])
            pen.setWidth(2)

            painter.setPen(pen)

            points = []

            for x in range(w):

                t = (x / w) * 4 * math.pi * self.time_scale

                y = center + amplitude * math.sin(t + self.phase + i)

                points.append(QtCore.QPointF(x, y))

            painter.drawPolyline(points)

        cursor_pen = QtGui.QPen(QtGui.QColor("white"))
        cursor_pen.setStyle(QtCore.Qt.DashLine)
        cursor_pen.setWidth(1)

        painter.setPen(cursor_pen)

        painter.drawLine(self.cursor1,0,self.cursor1,h)
        painter.drawLine(self.cursor2,0,self.cursor2,h)

    def mouseMoveEvent(self,event):

        if event.buttons() & QtCore.Qt.LeftButton:
            self.cursor1 = int(event.position().x())

        if event.buttons() & QtCore.Qt.RightButton:
            self.cursor2 = int(event.position().x())

        self.update()

class OscilloscopeWidget(QtWidgets.QWidget):
    """
    Widget principal del osciloscopio LabVolt
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # estado del osciloscopio
        self.phase = 0
        self.time_scale = 1
        self.coupling_mode = "DC"

        # canales activos
        self.active_channels = {
            "A": True,
            "B": False
        }

        self._build_ui()

        # timer animación
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)


    def _build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        # -------------------------
        # Zona superior
        # -------------------------
        top_layout = QtWidgets.QHBoxLayout()

        # Izquierda: grilla
        self.scope_grid = OscilloscopeGrid()
        top_layout.addWidget(self.scope_grid, stretch=3)

        # Derecha: controles de canales
        channels_layout = QtWidgets.QGridLayout()
        channels_layout.setSpacing(6)

        channel_defs = [
            ("Can1 (X)", QtGui.QColor("green")),
            ("Can2 (Y)", QtGui.QColor("yellow")),
            ("Can3", QtGui.QColor("violet")),
            ("Can4", QtGui.QColor("red")),
            ("Can5", QtGui.QColor("orange")),
            ("Can6", QtGui.QColor("blue")),
            ("Can7", QtGui.QColor("black")),
            ("Can8", QtGui.QColor("brown")),
        ]

        self.channels = []

        for i, (name, color) in enumerate(channel_defs):

            ch = ChannelControlWidget(name, color)

            self.channels.append(ch)

            channels_layout.addWidget(ch, i // 2, i % 2)

        top_layout.addLayout(channels_layout, stretch=2)
        main_layout.addLayout(top_layout)

        # -------------------------
        # Zona inferior
        # -------------------------
        bottom_layout = QtWidgets.QHBoxLayout()

        # Izquierda: tabla de datos
        data_group = QtWidgets.QGroupBox("Datos Formas de ondas")
        data_layout = QtWidgets.QVBoxLayout(data_group)

        table = QtWidgets.QTableWidget(9, 4)
        table.setHorizontalHeaderLabels(["Cursores", "EFI", "PRO", "f (Hz)"])
        table.verticalHeader().setVisible(False)
        table.setStyleSheet(
            """
            QTableWidget {
                background: #ffffff;
                border: 2px solid #808080;
            }
            """
        )
        data_layout.addWidget(table)
        bottom_layout.addWidget(data_group, stretch=1)

        # Derecha: base de tiempo
        time_group = QtWidgets.QGroupBox("Base de tiempo")
        time_layout = QtWidgets.QVBoxLayout(time_group)

        self.time_combo = QtWidgets.QComboBox()
        self.time_combo.addItems([
            "0.2 ms/div.",
            "0.5 ms/div.",
            "1 ms/div.",
            "1.66667 ms/div.",
            "2 ms/div.",
            "5 ms/div.",
            "10 ms/div.",
            "20 ms/div.",
            "50 ms/div.",
            "100 ms/div.",
            "0.2 s/div.",
            "0.5 s/div.",
            "1 s/div.",
            "2 s/div.",
            "5 s/div.",
            "10 s/div."
        ])
        time_layout.addWidget(self.time_combo)

        self.time_combo.currentTextChanged.connect(self.update_timebase)

        bottom_layout.addWidget(time_group, stretch=1)

        main_layout.addLayout(bottom_layout)


    def update_timebase(self, text):

        mapping = {
            "0.2 ms/div.": 6,
            "0.5 ms/div.": 4,
            "1 ms/div.": 2,
            "5 ms/div.": 1,
            "10 ms/div.": 0.8,
            "20 ms/div.": 0.6,
            "50 ms/div.": 0.4,
            "100 ms/div.": 0.2,
            "0.2 s/div.": 0.1,
            "0.5 s/div.": 0.05,
            "1 s/div.": 0.02
        }

        self.time_scale = mapping.get(text, 1)

    def animate(self):

        self.phase += 0.1

        # leer configuración de canales
        channel_data = []

        for ch in self.channels:

            entry = ch.get_entry()
            scale = ch.get_scale()
            coupling = ch.get_coupling()

            channel_data.append({
            "entry": entry,
            "scale": scale,
            "coupling": coupling
            })

        self.scope_grid.phase = self.phase
        self.scope_grid.time_scale = self.time_scale
        self.scope_grid.channel_data = channel_data

        self.scope_grid.update()  

    def update_signals(self, data):

        self.scope_grid.real_signals = data
        self.scope_grid.update()