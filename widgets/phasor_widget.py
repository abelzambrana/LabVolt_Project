# widgets/phasor_widget.py - diagrama fasorial con panel lateral de datos
from PySide6 import QtWidgets, QtCore
import pyqtgraph as pg
import numpy as np

class PhasorWidget(QtWidgets.QWidget):
    """Phasor: dibujo polar con anillos y panel derecho que contiene tabla pequeña."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        h = QtWidgets.QHBoxLayout(self)
        # plot polar (usamos PlotWidget pero convertimos coordenadas)
        self.plot = pg.PlotWidget()
        self.plot.getViewBox().setBackgroundColor((6,27,24))
        self.plot.setAspectLocked(True)
        h.addWidget(self.plot, 3)
        # derecho: controles y tabla simplificada
        right = QtWidgets.QVBoxLayout()
        # selector de referencia
        self.ref_combo = QtWidgets.QComboBox()
        self.ref_combo.addItems(["Va","Vb","Vc"])
        right.addWidget(QtWidgets.QLabel("Referencia:"))
        right.addWidget(self.ref_combo)
        # tabla simple de fasores
        self.table = QtWidgets.QTableWidget(6, 3)
        self.table.setHorizontalHeaderLabels(["Canal", "Mag", "Phase"])
        right.addWidget(self.table)
        right.addStretch(1)
        h.addLayout(right, 1)
        self.setLayout(h)
        self._draw_base()

    def _draw_base(self):
        # dibuja anillos y ejes de referencia
        self.plot.clear()
        theta = np.linspace(0, 2*np.pi, 512)
        for r in (0.33, 0.66, 1.0):
            x = r * np.cos(theta); y = r * np.sin(theta)
            self.plot.plot(x, y, pen=pg.mkPen((180,220,220), width=1))
        # ejes
        self.plot.plot([0,1],[0,0], pen=pg.mkPen('w'))
        self.plot.plot([0,0],[0,1], pen=pg.mkPen('w'))

    def update_from_data(self, data, fundamental=50.0):
        # calcula fasores por FFT y los dibuja
        t = data.get("t"); 
        if t is None: return
        t = np.array(t, dtype=float)
        if t.size < 2: return
        fs = 1.0/(t[1]-t[0])
        N = len(t)
        self._draw_base()
        rows = []
        # extraigo Vs e Is
        for i, ch in enumerate(["Va","Vb","Vc","Ia","Ib","Ic"]):
            arr = np.array(data.get(ch, np.zeros(N)), dtype=float)
            if arr.size < 2:
                mag, ang = 0.0, 0.0
            else:
                freqs = np.fft.rfftfreq(len(arr), d=1/fs)
                fftc = np.fft.rfft(arr)
                idx = np.argmin(np.abs(freqs-fundamental))
                mag = 2*np.abs(fftc[idx])/len(arr)
                ang = np.angle(fftc[idx], deg=True)
            # escalado visual: voltajes y corrientes diferentes
            scale = 220.0 if ch.startswith("V") else 5.0
            mag_norm = mag/scale if scale else 0.0
            x = mag_norm * np.cos(np.radians(ang))
            y = mag_norm * np.sin(np.radians(ang))
            pen = pg.mkPen('r', width=3) if ch.startswith("V") else pg.mkPen('c', width=2, style=QtCore.Qt.DashLine)
            self.plot.plot([0,x], [0,y], pen=pen)
            rows.append((ch, f"{mag:.3f}", f"{ang:.1f}°"))
        # actualizo tabla
        self.table.clearContents()
        for r_i, row in enumerate(rows):
            ch, magstr, phstr = row
            self.table.setItem(r_i, 0, QtWidgets.QTableWidgetItem(ch))
            self.table.setItem(r_i, 1, QtWidgets.QTableWidgetItem(magstr))
            self.table.setItem(r_i, 2, QtWidgets.QTableWidgetItem(phstr))
