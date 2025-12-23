# widgets/oscilloscope_widget.py
# Osciloscopio estilo LabVolt / Windows 95 (solo visual por ahora)

from PySide6 import QtWidgets, QtGui, QtCore
from widgets.channel_control_widget import ChannelControlWidget


class OscilloscopeGrid(QtWidgets.QWidget):
    """
    Área de dibujo del osciloscopio:
    - 10 columnas x 8 filas
    - 5 subdivisiones por cuadro
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(520, 420)
        self.setStyleSheet("background: #008b8b;")

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, False)

        w = self.width()
        h = self.height()

        cols = 10
        rows = 8
        sub = 5

        col_w = w / cols
        row_h = h / rows

        # Líneas finas (subdivisiones)
        pen_sub = QtGui.QPen(QtGui.QColor("#4fd1c5"))
        pen_sub.setWidth(1)
        painter.setPen(pen_sub)

        for c in range(cols * sub + 1):
            x = c * (w / (cols * sub))
            painter.drawLine(int(x), 0, int(x), h)

        for r in range(rows * sub + 1):
            y = r * (h / (rows * sub))
            painter.drawLine(0, int(y), w, int(y))

        # Líneas principales
        pen_main = QtGui.QPen(QtGui.QColor("#b2ffff"))
        pen_main.setWidth(2)
        painter.setPen(pen_main)

        for c in range(cols + 1):
            x = c * col_w
            painter.drawLine(int(x), 0, int(x), h)

        for r in range(rows + 1):
            y = r * row_h
            painter.drawLine(0, int(y), w, int(y))

        # Cruz central
        pen_center = QtGui.QPen(QtGui.QColor("white"))
        pen_center.setWidth(2)
        painter.setPen(pen_center)

        painter.drawLine(w // 2, 0, w // 2, h)
        painter.drawLine(0, h // 2, w, h // 2)


class OscilloscopeWidget(QtWidgets.QWidget):
    """
    Widget principal del osciloscopio LabVolt
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

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
            ("Can1 (X)", QtGui.QColor("lime")),
            ("Can2 (Y)", QtGui.QColor("yellow")),
            ("Can3", QtGui.QColor("cyan")),
            ("Can4", QtGui.QColor("red")),
            ("Can5", QtGui.QColor("white")),
            ("Can6", QtGui.QColor("white")),
            ("Can7", QtGui.QColor("white")),
            ("Can8", QtGui.QColor("white")),
        ]

        for i, (name, color) in enumerate(channel_defs):
            ch = ChannelControlWidget(name, color)
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

        table = QtWidgets.QTableWidget(4, 4)
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
        bottom_layout.addWidget(data_group, stretch=3)

        # Derecha: base de tiempo
        time_group = QtWidgets.QGroupBox("Base de tiempo")
        time_layout = QtWidgets.QVBoxLayout(time_group)

        time_combo = QtWidgets.QComboBox()
        time_combo.addItems([
            "0.2 ms/div",
            "0.5 ms/div",
            "1 ms/div",
            "100 ms/div",
            "1 s/div"
        ])
        time_layout.addWidget(time_combo)
        bottom_layout.addWidget(time_group, stretch=1)

        main_layout.addLayout(bottom_layout)
