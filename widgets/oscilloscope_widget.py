# widgets/oscilloscope_widget.py - osciloscopio con rejilla CRT, perillas y botones de memoria
from PySide6 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg
import numpy as np

class OscilloscopeWidget(QtWidgets.QWidget):
    """Osciloscopio con panel derecho de controles parecido a la captura."""
    def __init__(self, channel_list, parent=None):
        super().__init__(parent)
        self.channel_list = channel_list
        self._build_ui()

    def _build_ui(self):
        # layout horizontal: plot (izq) + controles (der)
        h = QtWidgets.QHBoxLayout(self)
        # Plot principal
        self.plot = pg.PlotWidget(title="Osciloscopio")
        self.plot.getViewBox().setBackgroundColor((6,27,24))  # CRT dark
        self.plot.showGrid(x=True, y=True, alpha=0.25)
        self.plot.setLabel('left', 'Amplitud')
        self.plot.setLabel('bottom', 't', units='s')
        self.curves = {}
        for i, ch in enumerate(self.channel_list):
            pen = pg.mkPen(color=pg.intColor(i, hues=len(self.channel_list)), width=1.6)
            self.curves[ch] = self.plot.plot([], [], pen=pen, name=ch)
        h.addWidget(self.plot, 3)

        # Panel derecho con controles estilo LabVolt
        right = QtWidgets.QVBoxLayout()
        # grupo de perillas: Time/Div y Volts/Div (usamos QDial para simular)
        grp = QtWidgets.QGroupBox("Time/Div & Volts/Div")
        gl = QtWidgets.QHBoxLayout(grp)
        # Time/div dial
        tdial_box = QtWidgets.QVBoxLayout()
        self.tdial = QtWidgets.QDial()
        self.tdial.setNotchesVisible(True)
        self.tdial.setMinimum(0)
        self.tdial.setMaximum(8)
        tdial_box.addWidget(QtWidgets.QLabel("Time/Div"))
        tdial_box.addWidget(self.tdial)
        gl.addLayout(tdial_box)
        # Volts/div dial
        vdial_box = QtWidgets.QVBoxLayout()
        self.vdial = QtWidgets.QDial()
        self.vdial.setNotchesVisible(True)
        self.vdial.setMinimum(0)
        self.vdial.setMaximum(6)
        vdial_box.addWidget(QtWidgets.QLabel("Volts/Div"))
        vdial_box.addWidget(self.vdial)
        gl.addLayout(vdial_box)
        right.addWidget(grp)

        # controles de canal (checkbox + selector input)
        ch_gb = QtWidgets.QGroupBox("Canales")
        ch_layout = QtWidgets.QVBoxLayout(ch_gb)
        self.channel_checks = {}
        for ch in self.channel_list:
            row = QtWidgets.QHBoxLayout()
            cb = QtWidgets.QCheckBox(ch)
            cb.setChecked(True)
            sel = QtWidgets.QComboBox()
            sel.addItems(["E1","E2","E3","I1","I2","I3","Ninguno"])
            row.addWidget(cb)
            row.addWidget(sel)
            ch_layout.addLayout(row)
            self.channel_checks[ch] = (cb, sel)
        right.addWidget(ch_gb)

        # botones de memoria (store/recall) estilo caja
        mem_box = QtWidgets.QHBoxLayout()
        for i in range(1,5):
            b = QtWidgets.QPushButton(f"M{i}")
            b.setFixedSize(36,28)
            mem_box.addWidget(b)
        right.addLayout(mem_box)

        right.addStretch(1)
        h.addLayout(right, 1)
        self.setLayout(h)

    def update_data(self, data):
        # actualiza trazas normalizadas por su propia amplitud para verse correctamente
        t = data.get("t")
        if t is None: return
        t_arr = np.array(t, dtype=float)
        for ch, curve in self.curves.items():
            arr = data.get(ch)
            if arr is None: continue
            y = np.array(arr, dtype=float)
            # normalización pero preservando forma para semblanza a captura
            maxv = np.max(np.abs(y)) if y.size else 1.0
            scale = 1.0 if maxv == 0 else maxv
            curve.setData(t_arr, y/scale)
