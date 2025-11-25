# labvolt_clone.py
# Replica aproximada del UI LabVolt (4 pantallas) y conexión a DAQReader.
# Requisitos: PySide6, pyqtgraph, numpy, pandas (para DAQReader)
# Uso: python labvolt_clone.py
import sys
import numpy as np
from PySide6 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
from daq_reader import DAQReader  # debes tener tu daq_reader.py en la misma carpeta

pg.setConfigOptions(antialias=True)

# ---------------------------
# Estilos y utilidades
# ---------------------------
LCD_STYLE = """
QLabel.lcd {
    color: #00ff66;
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #00a05a, stop:0.5 #007a47, stop:1 #004d2b);
    border: 2px inset #666;
    border-radius: 4px;
    padding: 4px;
}
QLabel.placeholder {
    background: black;
    border: 2px inset #333;
}
QGroupBox {
    border: 1px solid #9a9a9a;
    margin-top: 6px;
    font-weight: bold;
}
"""

CRT_PLOT_BG = (0, 90, 75)  # dark teal RGB like LabVolt CRT
CRT_GRID_PEN = pg.mkPen((180, 220, 220), width=1)


# ---------------------------
# Measurement Widget (panel principal)
# ---------------------------
class MeasurementWidget(QtWidgets.QWidget):
    """
    Grid of small groupboxes with big green LCD-like displays and unit labels,
    intended to replicate the 'Aparatos de medición' window.
    """
    def __init__(self, channels, parent=None):
        super().__init__(parent)
        self.channels = channels  # list of dicts: {'title':..., 'ch':..., 'unit':...}
        self._build_ui()
        self.setStyleSheet(LCD_STYLE)

    def _build_ui(self):
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(8)
        positions = [(r, c) for r in range(4) for c in range(6)]  # flexible grid
        for pos, chinfo in zip(positions, self.channels):
            gb = QtWidgets.QGroupBox(chinfo.get('title', ''))
            v = QtWidgets.QVBoxLayout(gb)
            display = QtWidgets.QLabel("0.000", alignment=QtCore.Qt.AlignCenter)
            display.setObjectName(chinfo.get('ch', ''))
            display.setProperty("class", "lcd")
            display.setStyleSheet("")  # inherited from LCD_STYLE
            font = QtGui.QFont("Courier", 20, QtGui.QFont.Bold)
            display.setFont(font)
            # Placeholder below for unit and small label row
            unit_lbl = QtWidgets.QLabel(chinfo.get('unit', ''), alignment=QtCore.Qt.AlignCenter)
            unit_lbl.setFixedHeight(18)
            unit_lbl.setStyleSheet("font-size:11px;")
            v.addWidget(display, stretch=1)
            v.addWidget(unit_lbl, stretch=0)
            grid.addWidget(gb, *pos)
            # store references
            chinfo['widget'] = display
            chinfo['unit_widget'] = unit_lbl
        self.setLayout(grid)

    def set_value(self, ch_name, value):
        for ch in self.channels:
            if ch.get('ch') == ch_name:
                w: QtWidgets.QLabel = ch['widget']
                # format with 3 decimals unless very large
                w.setText(f"{value:.3f}")
                return

    def set_placeholder(self, ch_name, enabled=True):
        for ch in self.channels:
            if ch.get('ch') == ch_name:
                w: QtWidgets.QLabel = ch['widget']
                if enabled:
                    w.setProperty("class", "placeholder")
                    w.setStyleSheet("QLabel { background: black; color: #000; }")
                    w.setText("")
                else:
                    w.setProperty("class", "lcd")
                    w.setStyleSheet("")
                return


# ---------------------------
# Oscilloscope (CRT-like)
# ---------------------------
class OscilloscopeWidget(pg.GraphicsLayoutWidget):
    def __init__(self, channels, parent=None):
        super().__init__(parent)
        self.channels = channels  # list of channel names
        self._build_ui()
        self.setMinimumHeight(360)

    def _build_ui(self):
        # left: big plot area
        self.plotItem = self.addPlot(row=0, col=0, colspan=3)
        self.plotItem.setMenuEnabled(False)
        # emulate CRT: background color and grid
        self.plotItem.getViewBox().setBackgroundColor(CRT_PLOT_BG)
        # add grid lines manually
        self._draw_grid(self.plotItem)
        self.curves = {}
        # offsets for multiple traces
        self.plotItem.addLegend(offset=(10, 10))
        for i, ch in enumerate(self.channels):
            pen = pg.mkPen(color=pg.intColor(i, hues=len(self.channels)), width=1.5)
            c = self.plotItem.plot([], [], pen=pen, name=ch)
            self.curves[ch] = c
        # right: controls (simple placeholders to mimic look)
        # We'll create a docked QWidget with controls (not interactive advanced knobs here)
        self.ctrl_widget = QtWidgets.QWidget()
        cw_layout = QtWidgets.QVBoxLayout(self.ctrl_widget)
        cw_layout.setContentsMargins(8, 8, 8, 8)
        cw_layout.addWidget(QtWidgets.QLabel("<b>Canales</b>"))
        for ch in self.channels:
            row = QtWidgets.QHBoxLayout()
            cb = QtWidgets.QCheckBox(ch)
            cb.setChecked(False)
            row.addWidget(cb)
            # input selector
            sel = QtWidgets.QComboBox()
            sel.addItems(["Ninguna"] + ["E1", "E2", "E3", "I1", "I2", "I3"])
            row.addWidget(sel)
            cw_layout.addLayout(row)
        spacer = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        cw_layout.addItem(spacer)
        proxy = self.addLayout(row=0, col=3)
        # The pyqtgraph layout does not directly accept QWidget; we use GraphicsLayoutWidget's `addItem`
        # Instead we place the control widget to the right using a numpy approach: use a QWidget overlay in the parent layout
        # For simplicity we'll add a placeholder label at right:
        self.nextRow()
        # bottom area for cursors and memory (simple placeholders)
        self.cursors_label = QtWidgets.QLabel("Cursors: -")
        # We'll expose a method to get a parent layout for external placement in the main window

    def _draw_grid(self, plot):
        vb = plot.getViewBox()
        # draw a grid using infinite lines
        for x in np.linspace(-1, 1, 11):
            line = pg.InfiniteLine(angle=90, pos=x, pen=CRT_GRID_PEN)
            plot.addItem(line)
        for y in np.linspace(-1, 1, 11):
            line = pg.InfiniteLine(angle=0, pos=y, pen=CRT_GRID_PEN)
            plot.addItem(line)
        # central crosshair thicker
        plot.addItem(pg.InfiniteLine(angle=90, pen=pg.mkPen('w', width=2)))
        plot.addItem(pg.InfiniteLine(angle=0, pen=pg.mkPen('w', width=2)))

    def update_data(self, data):
        # Expect data as dict with 't' and channel arrays
        t = data.get('t')
        if t is None:
            return
        for ch in self.channels:
            arr = data.get(ch)
            if arr is None:
                continue
            # Normalize/scale for display: center on 0 and scale to viewbox limits
            x = t
            y = arr / (np.max(np.abs(arr)) + 1e-12)  # normalized
            self.curves[ch].setData(x, y)


# ---------------------------
# Phasor (polar plot)
# ---------------------------
class PhasorWidget(pg.PlotWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackground(CRT_PLOT_BG)
        self.getPlotItem().getViewBox().setAspectLocked()
        self.getPlotItem().hideAxis('bottom')
        self.getPlotItem().hideAxis('left')
        self.setMinimumHeight(360)
        # draw circular rings and angle labels
        self._draw_polar()

    def _draw_polar(self):
        rads = np.linspace(0, 2*np.pi, 512)
        maxr = 1.0
        # rings
        for rr in [0.33, 0.66, 1.0]:
            x = rr * np.cos(rads)
            y = rr * np.sin(rads)
            self.plot(x, y, pen=pg.mkPen((180,220,220), width=1))
        # axes
        self.plot([0, 1], [0, 0], pen=pg.mkPen('w', width=1))
        self.plot([0, -1], [0, 0], pen=pg.mkPen('w', width=1))
        self.plot([0, 0], [0, 1], pen=pg.mkPen('w', width=1))
        self.plot([0, 0], [0, -1], pen=pg.mkPen('w', width=1))
        # angle ticks
        for ang in np.arange(0, 360, 45):
            a = np.radians(ang)
            x1, y1 = 0.9*np.cos(a), 0.9*np.sin(a)
            x2, y2 = 1.0*np.cos(a), 1.0*np.sin(a)
            self.plot([x1, x2], [y1, y2], pen=pg.mkPen('w', width=2))

    def update_phasors_from_data(self, voltages, currents, angle_i_deg=-30):
        """
        voltages: dict name -> complex phasor (or tuple mag, angle_deg)
        currents: same
        """
        self.clear()
        self._draw_polar()
        # draw voltages
        for name, ph in voltages.items():
            mag, ang = ph if isinstance(ph, tuple) else (abs(ph), np.degrees(np.angle(ph)))
            x = mag * np.cos(np.radians(ang))
            y = mag * np.sin(np.radians(ang))
            self.plot([0, x], [0, y], pen=pg.mkPen('r', width=3))
        # draw currents with angle shift
        for name, ph in currents.items():
            mag, ang = ph if isinstance(ph, tuple) else (abs(ph), np.degrees(np.angle(ph)))
            ang += angle_i_deg
            x = mag * np.cos(np.radians(ang))
            y = mag * np.sin(np.radians(ang))
            self.plot([0, x], [0, y], pen=pg.mkPen('c', width=2, style=QtCore.Qt.DashLine))


# ---------------------------
# Spectrum analyzer (simple)
# ---------------------------
class SpectrumWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QHBoxLayout(self)
        # left: spectrum plot
        self.spec_plot = pg.PlotWidget()
        self.spec_plot.getViewBox().setBackgroundColor(CRT_PLOT_BG)
        self._draw_grid(self.spec_plot)
        self.line = self.spec_plot.plot([], [], pen=pg.mkPen('y', width=1.5))
        layout.addWidget(self.spec_plot, 3)
        # right: controls
        ctrl = QtWidgets.QWidget()
        ctrl_layout = QtWidgets.QFormLayout(ctrl)
        ctrl_layout.addRow(QtWidgets.QLabel("<b>Entrada</b>"), QtWidgets.QComboBox())
        self.freq_display = QtWidgets.QLabel("0.000000 kHz")
        self.freq_display.setStyleSheet("color: #00ff66; background: #002b20; padding:4px;")
        ctrl_layout.addRow(QtWidgets.QLabel("Frecuencia central"), self.freq_display)
        layout.addWidget(ctrl, 1)

    def _draw_grid(self, plotw):
        # simple grid using infinite lines
        for x in np.linspace(0, 1, 11):
            plotw.addItem(pg.InfiniteLine(angle=90, pos=x, pen=CRT_GRID_PEN))
        for y in np.linspace(-1, 1, 11):
            plotw.addItem(pg.InfiniteLine(angle=0, pos=y, pen=CRT_GRID_PEN))

    def update_spectrum(self, data):
        # compute FFT of the first available channel
        t = data.get('t')
        if t is None:
            return
        # choose first numeric channel other than t
        keys = [k for k in data.keys() if k != 't']
        for k in keys:
            try:
                arr = np.array(data[k], dtype=float)
            except Exception:
                continue
            if arr.size < 2:
                continue
            break
        else:
            return
        # FFT
        N = len(arr)
        fs = 1.0 / (t[1]-t[0])
        freqs = np.fft.rfftfreq(N, d=1/fs)
        spec = np.abs(np.fft.rfft(arr)) / N
        self.line.setData(freqs, 20*np.log10(spec + 1e-12))


# ---------------------------
# Main application window
# ---------------------------
class LabVoltCloneMain(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LabVolt Simulator - Clone")
        self.resize(1200, 800)
        self._build_menu_toolbar()
        self._build_central()
        # DAQReader
        self.daq = DAQReader(usb_port="COM3", fs=2000, block_size=200)
        self.daq.data_ready.connect(self.on_data_ready)
        # keep last data for phasors/spectrum
        self._last_data = None

    def _build_menu_toolbar(self):
        menubar = self.menuBar()
        filem = menubar.addMenu("Archivo")
        verm = menubar.addMenu("Ver")
        optm = menubar.addMenu("Opciones")
        helpm = menubar.addMenu("Ayuda")
        tb = self.addToolBar("Main")
        tb.addAction(QtGui.QIcon.fromTheme("media-playback-start"), "Iniciar", lambda: self.start_acquisition())
        tb.addAction(QtGui.QIcon.fromTheme("media-playback-stop"), "Detener", lambda: self.stop_acquisition())
        tb.addAction(QtGui.QIcon.fromTheme("document-save"), "Guardar CSV", lambda: self.daq.save_to_csv())

    def _build_central(self):
        central = QtWidgets.QWidget()
        mainlay = QtWidgets.QVBoxLayout(central)
        # top: tab widget with the 4 windows
        self.tabs = QtWidgets.QTabWidget()
        # 1 - Aparatos de medición
        channels = [
            {'title': 'E1', 'ch': 'Va', 'unit': 'V'},
            {'title': 'E2', 'ch': 'Vb', 'unit': 'V'},
            {'title': 'E3', 'ch': 'Vc', 'unit': 'V'},
            {'title': 'I1', 'ch': 'Ia', 'unit': 'A'},
            {'title': 'I2', 'ch': 'Ib', 'unit': 'A'},
            {'title': 'I3', 'ch': 'Ic', 'unit': 'A'},
            {'title': 'Speed', 'ch': 'speed', 'unit': 'r/min'},
            {'title': 'Torque', 'ch': 'torque', 'unit': 'Nm'},
        ]
        self.measurement_widget = MeasurementWidget(channels)
        self.tabs.addTab(self.measurement_widget, "Aparatos de medición")
        # 2 - Osciloscopio
        osc_channels = ['Va', 'Vb', 'Vc', 'Ia', 'Ib', 'Ic']
        self.osc_widget = OscilloscopeWidget(osc_channels)
        self.tabs.addTab(self.osc_widget, "Osciloscopio")
        # 3 - Fasores
        self.phasor_widget = PhasorWidget()
        self.tabs.addTab(self.phasor_widget, "Analizador de fasores")
        # 4 - Espectro
        self.spectrum_widget = SpectrumWidget()
        self.tabs.addTab(self.spectrum_widget, "Analizador de espectro")

        mainlay.addWidget(self.tabs)
        self.setCentralWidget(central)

        # status bar
        self.statusBar().showMessage("Listo - réplica LabVolt (4 ventanas)")

    # -------------------
    # DAQ handling
    # -------------------
    def start_acquisition(self):
        if not self.daq.isRunning():
            self.daq.start()
            self.statusBar().showMessage("Adquisición iniciada")

    def stop_acquisition(self):
        if self.daq.isRunning():
            self.daq.stop()
            self.statusBar().showMessage("Adquisición detenida")

    @QtCore.Slot(dict)
    def on_data_ready(self, data):
        # save last
        self._last_data = data
        # update measurement displays
        # Map DAQ channels to widget channels
        map_ch = {
            'Va': 'Va', 'Vb': 'Vb', 'Vc': 'Vc',
            'Ia': 'Ia', 'Ib': 'Ib', 'Ic': 'Ic',
            'speed': 'speed', 'torque': 'torque'
        }
        for chk, chname in map_ch.items():
            if chname in data:
                # compute a scalar to show in the LCD: RMS for sinusoidal-like arrays
                arr = np.array(data[chname], dtype=float)
                scalar = np.sqrt(np.mean(arr**2))
                # for speed/torque we show mean
                if chname in ('speed', 'torque'):
                    scalar = np.mean(arr)
                self.measurement_widget.set_value(chname, scalar)

        # update oscilloscope traces
        self.osc_widget.update_data(data)
        # update phasors (approximate using fundamental component)
        try:
            # estimate phasor for E1/E2/E3 using FFT fundamental (50Hz)
            phs_v = {}
            for ch in ['Va', 'Vb', 'Vc']:
                if ch in data:
                    arr = np.array(data[ch], dtype=float)
                    t = np.array(data['t'], dtype=float)
                    fs = 1.0 / (t[1]-t[0])
                    N = len(arr)
                    freqs = np.fft.rfftfreq(N, d=1/fs)
                    fftc = np.fft.rfft(arr)
                    # find nearest to 50Hz
                    idx = np.argmin(np.abs(freqs-50.0))
                    mag = 2*np.abs(fftc[idx]) / N
                    ang = np.angle(fftc[idx], deg=True)
                    phs_v[ch] = (mag/220.0, ang)  # normalized magnitude
            phs_i = {}
            for ch in ['Ia', 'Ib', 'Ic']:
                if ch in data:
                    arr = np.array(data[ch], dtype=float)
                    t = np.array(data['t'], dtype=float)
                    fs = 1.0 / (t[1]-t[0])
                    N = len(arr)
                    freqs = np.fft.rfftfreq(N, d=1/fs)
                    fftc = np.fft.rfft(arr)
                    idx = np.argmin(np.abs(freqs-50.0))
                    mag = 2*np.abs(fftc[idx]) / N
                    ang = np.angle(fftc[idx], deg=True)
                    phs_i[ch] = (mag/5.0, ang)
            self.phasor_widget.update_phasors_from_data(
                {'E1': phs_v.get('Va', (0,0)), 'E2': phs_v.get('Vb', (0,0)), 'E3': phs_v.get('Vc', (0,0))},
                {'I1': phs_i.get('Ia', (0,0)), 'I2': phs_i.get('Ib', (0,0)), 'I3': phs_i.get('Ic', (0,0))},
                angle_i_deg=-30
            )
        except Exception as e:
            # fail silently but show status
            self.statusBar().showMessage(f"Phasor calc error: {e}")

        # update spectrum
        self.spectrum_widget.update_spectrum(data)


# ---------------------------
# Run
# ---------------------------
def main():
    app = QtWidgets.QApplication(sys.argv)
    win = LabVoltCloneMain()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
