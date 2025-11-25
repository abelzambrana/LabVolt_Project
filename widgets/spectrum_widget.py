# widgets/spectrum_widget.py - analizador de espectro con display de frecuencia
from PySide6 import QtWidgets
import pyqtgraph as pg
import numpy as np

class SpectrumWidget(QtWidgets.QWidget):
    """Analizador de espectro con display a la derecha y rejilla tipo CRT."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        h = QtWidgets.QHBoxLayout(self)
        self.plot = pg.PlotWidget(title="Analizador de espectro")
        self.plot.getViewBox().setBackgroundColor((6,27,24))
        self.curve = self.plot.plot([], [], pen=pg.mkPen('y', width=1.4))
        self.plot.showGrid(x=True, y=True, alpha=0.25)
        h.addWidget(self.plot, 3)
        right = QtWidgets.QVBoxLayout()
        self.freq_display = QtWidgets.QLabel("Frecuencia central: - Hz")
        self.freq_display.setStyleSheet("color:#00ff66; background:#002b20; padding:6px;")
        right.addWidget(self.freq_display)
        right.addStretch(1)
        h.addLayout(right, 1)
        self.setLayout(h)

    def update_from_data(self, data):
        t = data.get("t")
        if t is None: return
        # elijo primera señal válida
        arr = None
        for k,v in data.items():
            if k == "t": continue
            try:
                tmp = np.array(v, dtype=float)
                if tmp.size > 1:
                    arr = tmp; key = k; break
            except Exception:
                continue
        if arr is None: return
        N = len(arr)
        fs = 1.0/(t[1]-t[0])
        freqs = np.fft.rfftfreq(N, d=1/fs)
        spec = np.abs(np.fft.rfft(arr)) / N
        spec_db = 20*np.log10(spec + 1e-12)
        self.curve.setData(freqs, spec_db)
        idx = int(np.argmax(spec))
        self.freq_display.setText(f"Frecuencia central: {freqs[idx]:.2f} Hz  ({key})")
