# main_labvolt.py
# Ventana principal con menubar clásica y pestañas (Opción B).
# Título actualizado y logo cargado desde la ruta en tu proyecto.
import sys
import os
from PySide6 import QtWidgets, QtGui, QtCore
from widgets import MeasurementWidget
from daq_reader import DAQReader
from utils.styles import apply_app_style

# Ruta local del mini-logo según tu comentario
_LOCAL_MINI_LOGO_PATH = r"C:\Users\Tepsi\Documents\LabVolt_Project\img\MiniLogo.png"
# Fallback (si corres en el entorno actual)
_FALLBACK_MINI_LOGO = "/mnt/data/MiniLogo.png"

class MainLabVolt(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # título pedido
        self.setWindowTitle("LabVolt - Mediciones Eléctricas")
        self.resize(1200, 760)
        apply_app_style(self)
        self._build_ui()

        # DAQReader (tu archivo debe estar en la misma carpeta)
        self.daq = DAQReader(usb_port="COM3", fs=2000, block_size=200)
        self.daq.data_ready.connect(self.on_data_ready)
        self._last_data = None

    def _build_ui(self):
        # Menu bar clásico
        menubar = self.menuBar()
        archivo = menubar.addMenu("Archivo")
        opciones = menubar.addMenu("Opciones")
        actualizar = menubar.addMenu("Actualizar")
    

        # Archivo -> acciones
        impr = QtGui.QAction("Imprimir", self)
        prev = QtGui.QAction("Previsualización", self)
        conf_imp = QtGui.QAction("Configuración de impresión", self)
        cerrar = QtGui.QAction("Cerrar", self)
        cerrar.triggered.connect(self.close)
        archivo.addAction(impr); archivo.addAction(prev); archivo.addAction(conf_imp)
        archivo.addSeparator(); archivo.addAction(cerrar)

        # Opciones -> acciones (placeholders)
        opciones.addAction(QtGui.QAction("Colores", self))
        opciones.addAction(QtGui.QAction("Disposición", self))
        opciones.addAction(QtGui.QAction("Ajuste del medidor", self))
        opciones.addAction(QtGui.QAction("Ajuste de adquisición", self))

        # Actualizar -> único comando (acción textual)
        refresh_act = QtGui.QAction("Actualizar", self)
        refresh_act.triggered.connect(self._on_refresh)
        actualizar.addAction(refresh_act)

        # Intento de integrar el mini-logo: cargar desde tu carpeta 'img' (ruta absoluta que indicaste).
        logo_label = QtWidgets.QLabel()
        logo_pixmap = None
        try:
            if os.path.exists(_LOCAL_MINI_LOGO_PATH):
                pm = QtGui.QPixmap(_LOCAL_MINI_LOGO_PATH)
                target_w = 120
                pm = pm.scaledToWidth(target_w, QtCore.Qt.SmoothTransformation)
                logo_pixmap = pm
            elif os.path.exists(_FALLBACK_MINI_LOGO):
                pm = QtGui.QPixmap(_FALLBACK_MINI_LOGO)
                pm = pm.scaledToWidth(120, QtCore.Qt.SmoothTransformation)
                logo_pixmap = pm
        except Exception:
            logo_pixmap = None

        if logo_pixmap:
            logo_label.setPixmap(logo_pixmap)
            logo_label.setContentsMargins(4,0,8,0)
            # Coloco el logo en la esquina superior derecha del menubar
            menubar.setCornerWidget(logo_label, QtCore.Qt.TopRightCorner)

        # Central: TabWidget con pestañas (medición + placeholders)
        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central)
        self.tabs = QtWidgets.QTabWidget()
        layout.addWidget(self.tabs)

        # 1) Aparatos de medición (nuestro widget 3x4)
        channels = [
            ("E1", "Va", "V"), ("E2", "Vb", "V"), ("E3", "Vc", "V"), ("T", "torque", "N.m"),
            ("I1", "Ia", "A"), ("I2", "Ib", "A"), ("I3", "Ic", "A"), ("N", "speed", "r/min"),
            ("PQS1", "pqs1", "W"), ("PQS2", "pqs2", "W"), ("PQS3", "pqs3", "W"), ("Pm", "pm", "W"),
        ]
        self.measurement_panel = MeasurementWidget(channels, compact=True)
        self.tabs.addTab(self.measurement_panel, "Aparatos de medición")

        # placeholders para las otras pestañas
        osc_tab = QtWidgets.QWidget(); osc_tab.setLayout(QtWidgets.QVBoxLayout()); osc_tab.layout().addWidget(QtWidgets.QLabel("Osciloscopio - pendiente de integrar"))
        self.tabs.addTab(osc_tab, "Osciloscopio")
        ph_tab = QtWidgets.QWidget(); ph_tab.setLayout(QtWidgets.QVBoxLayout()); ph_tab.layout().addWidget(QtWidgets.QLabel("Analizador de fasores - pendiente"))
        self.tabs.addTab(ph_tab, "Analizador de fasores")
        sp_tab = QtWidgets.QWidget(); sp_tab.setLayout(QtWidgets.QVBoxLayout()); sp_tab.layout().addWidget(QtWidgets.QLabel("Analizador de espectro - pendiente"))
        self.tabs.addTab(sp_tab, "Analizador de espectro")
        harm_tab = QtWidgets.QWidget(); harm_tab.setLayout(QtWidgets.QVBoxLayout()); harm_tab.layout().addWidget(QtWidgets.QLabel("Analizador de armónicos - pendiente"))
        self.tabs.addTab(harm_tab, "Analizador de armónicos")
        table_tab = QtWidgets.QWidget(); table_tab.setLayout(QtWidgets.QVBoxLayout()); table_tab.layout().addWidget(QtWidgets.QLabel("Tabla de datos - pendiente"))
        self.tabs.addTab(table_tab, "Tabla de datos")

        # estado
        self.setCentralWidget(central)
        self.statusBar().showMessage("Listo - pestaña 'Aparatos de medición' activa")

    @QtCore.Slot(dict)
    def on_data_ready(self, data):
        """Actualiza medidores con el bloque recibido desde DAQReader."""
        self._last_data = data
        import numpy as _np
        for (title, ch_name, unit) in self.measurement_panel.channels:
            arr = data.get(ch_name)
            if arr is None:
                self.measurement_panel.set_value(ch_name, None)
                continue
            if ch_name in ("speed", "torque", "pm"):
                val = float(_np.mean(_np.array(arr)))
            else:
                val = float(_np.sqrt(_np.mean(_np.array(arr)**2)))
            self.measurement_panel.set_value(ch_name, val)

    def _on_refresh(self):
        """Comando del menú Actualizar: recalcula usando último bloque si existe."""
        if self._last_data is not None:
            self.on_data_ready(self._last_data)
            self.statusBar().showMessage("Datos actualizados")
        else:
            self.measurement_panel.force_all_off()
            QtCore.QTimer.singleShot(300, lambda: self.statusBar().showMessage("Sin datos para actualizar"))

    def closeEvent(self, event):
        """Al cerrar, detiene DAQ si está corriendo."""
        try:
            if hasattr(self, "daq") and self.daq.isRunning():
                self.daq.stop()
        except Exception:
            pass
        super().closeEvent(event)

def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainLabVolt()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
