from PySide6 import QtWidgets, QtGui, QtCore
import math
import numpy as np


# =========================================================
# WIDGET DE DIBUJO (CÍRCULO DE FASORES)
# =========================================================
class PhasorDisplay(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 400)
        self.phasors = []   # lista de (magnitud, angulo, color)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        w = self.width()
        h = self.height()

        cx = w // 2
        cy = h // 2
        radius = min(w, h) // 2 - 20

        # Fondo
        #painter.fillRect(self.rect(), QtGui.QColor("#0a7f7f"))

        # Fondo general (gris estilo Win95)
        #painter.fillRect(self.rect(), QtGui.QColor("#c0c0c0"))
        # -----------------------------
        # Fondo SOLO del círculo
        # -----------------------------
        brush = QtGui.QBrush(QtGui.QColor("#0a7f7f"))
        painter.setBrush(brush)
        painter.setPen(QtCore.Qt.NoPen)

        painter.drawEllipse(cx - radius, cy - radius, radius * 2, radius * 2)
        
        painter.setBrush(QtCore.Qt.NoBrush)

        # -----------------------------
        # Círculos concéntricos
        # -----------------------------
        pen_grid = QtGui.QPen(QtGui.QColor("#b2ffff"))
        pen_grid.setWidth(1)
        painter.setPen(pen_grid)

        for i in range(1, 5):
            r = int(radius * i / 4)
            painter.drawEllipse(cx - r, cy - r, 2 * r, 2 * r)

        # -----------------------------
        # Subdivisiones (24 marcas)
        # -----------------------------
        pen_ticks = QtGui.QPen(QtGui.QColor("black"))
        pen_ticks.setWidth(1.3)  # más grueso → "negrita"
        painter.setPen(pen_ticks)

        for i in range(24):
            angle = i * (360 / 24)
            rad = math.radians(angle)

            # punto exterior
            x1 = cx + int((radius + 5) * math.cos(rad))
            y1 = cy - int((radius + 5) * math.sin(rad))

            # punto interior (marca)
            x2 = cx + int(radius * math.cos(rad))
            y2 = cy - int(radius * math.sin(rad))

            painter.drawLine(x1, y1, x2, y2)


        # -----------------------------
        # Cruz central
        # -----------------------------
        pen_axis = QtGui.QPen(QtGui.QColor("white"))
        pen_axis.setWidth(1)
        painter.setPen(pen_axis)

        painter.drawLine(cx - radius, cy, cx + radius, cy)
        painter.drawLine(cx, cy - radius, cx, cy + radius)

        # -----------------------------
        # Marcas de ángulo
        # -----------------------------
        angles = [0, 45, 90, 135, 180, -135, -90, -45]

        for angle in angles:
            rad = math.radians(angle)
            x = cx + int((radius + 15) * math.cos(rad))
            y = cy - int((radius + 15) * math.sin(rad))
            
            #Nro de grados en negrita
            font = painter.font()
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(QtGui.QColor("black"))

            painter.drawText(x - 12, y + 5, f"{angle}°")

        # -----------------------------
        # (Opcional futuro) Dibujar fasores
        # -----------------------------
        # Por ahora vacío (solo visual)
        # Luego aquí dibujamos vectores reales
        
        # -----------------------------
        # Dibujar fasores reales
        # -----------------------------
        for mag, ang, color in self.phasors:
            pen_vec = QtGui.QPen(QtGui.QColor(color))
            pen_vec.setWidth(2)
            painter.setPen(pen_vec)

            r = mag * radius  # escala
            rad = math.radians(ang)

            x = cx + int(r * math.cos(rad))
            y = cy - int(r * math.sin(rad))

            painter.drawLine(cx, cy, x, y)

            # punta
            painter.drawEllipse(x-3, y-3, 6, 6)

# =========================================================
#  WIDGET PRINCIPAL
# =========================================================
class PhasorWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        main_layout = QtWidgets.QHBoxLayout(self)

        # =================================================
        # IZQUIERDA → DISPLAY
        # =================================================
        self.display = PhasorDisplay()
        main_layout.addWidget(self.display, stretch=3)

        # =================================================
        # DERECHA → CONTROLES
        # =================================================
        right_layout = QtWidgets.QVBoxLayout()

        # -------------------------
        # VOLTAJE
        # -------------------------
        volt_group = QtWidgets.QGroupBox("Voltaje")
        volt_layout = QtWidgets.QVBoxLayout(volt_group)

        self.volt_combo = QtWidgets.QComboBox()
        self.volt_combo.addItems([
            "2 V/div.",
            "5 V/div.",
            "10 V/div.",
            "20 V/div."
        ])

        volt_layout.addWidget(self.volt_combo)

        self.chk_e1 = QtWidgets.QCheckBox("E1")
        self.chk_e2 = QtWidgets.QCheckBox("E2")
        self.chk_e3 = QtWidgets.QCheckBox("E3")

        self.chk_e1.setStyleSheet("color: red;")
        self.chk_e2.setStyleSheet("color: lime;")
        self.chk_e3.setStyleSheet("color: blue;")

        volt_layout.addWidget(self.chk_e1)
        volt_layout.addWidget(self.chk_e2)
        volt_layout.addWidget(self.chk_e3)

        right_layout.addWidget(volt_group)

        # -------------------------
        # CORRIENTE
        # -------------------------
        curr_group = QtWidgets.QGroupBox("Corriente")
        curr_layout = QtWidgets.QVBoxLayout(curr_group)

        self.curr_combo = QtWidgets.QComboBox()
        self.curr_combo.addItems([
            "0.1 A/div.",
            "0.5 A/div.",
            "1 A/div.",
            "2 A/div."
        ])

        curr_layout.addWidget(self.curr_combo)

        self.chk_i1 = QtWidgets.QCheckBox("I1")
        self.chk_i2 = QtWidgets.QCheckBox("I2")
        self.chk_i3 = QtWidgets.QCheckBox("I3")

        self.chk_i1.setStyleSheet("color: red;")
        self.chk_i2.setStyleSheet("color: lime;")
        self.chk_i3.setStyleSheet("color: blue;")

        curr_layout.addWidget(self.chk_i1)
        curr_layout.addWidget(self.chk_i2)
        curr_layout.addWidget(self.chk_i3)

        right_layout.addWidget(curr_group)

        # -------------------------
        # FASOR DE REFERENCIA
        # -------------------------
        ref_group = QtWidgets.QGroupBox("Fasor de referencia")
        ref_layout = QtWidgets.QVBoxLayout(ref_group)

        self.ref_combo = QtWidgets.QComboBox()
        self.ref_combo.addItems(["E1", "E2", "E3"])

        ref_layout.addWidget(self.ref_combo)

        right_layout.addWidget(ref_group)

        # -------------------------
        # TABLA DE DATOS
        # -------------------------
        table_group = QtWidgets.QGroupBox("Datos de los fasores")
        table_layout = QtWidgets.QVBoxLayout(table_group)

        self.table = QtWidgets.QTableWidget(6, 3)
        self.table.setHorizontalHeaderLabels(["CA (RMS)", "Fase", "Frecuencia"])

        labels = ["E1 (V)", "E2 (V)", "E3 (V)", "I1 (A)", "I2 (A)", "I3 (A)"]

        for i, label in enumerate(labels):
            item = QtWidgets.QTableWidgetItem(label)
            self.table.setVerticalHeaderItem(i, item)

        table_layout.addWidget(self.table)

        right_layout.addWidget(table_group)

        # -------------------------
        right_layout.addStretch()
        main_layout.addLayout(right_layout, stretch=2)

    #FUNCION PARA RECIBIR DATOS
    def update_data(self, data):
        import numpy as np

        phasors = []

        def calc_phasor(signal):
            sig = np.array(signal)

            # RMS
            rms = np.sqrt(np.mean(sig**2))

            # frecuencia (aprox por FFT)
            fft = np.fft.fft(sig)
            freqs = np.fft.fftfreq(len(sig), d=1/2000)  # fs=2000

            idx = np.argmax(np.abs(fft[1:])) + 1
            freq = abs(freqs[idx])

            # fase
            phase = np.angle(fft[idx], deg=True)

            return rms, phase, freq

        mapping = [
            ("Va", "red"),
            ("Vb", "lime"),
            ("Vc", "blue"),
            ("Ia", "yellow"),
            ("Ib", "cyan"),
            ("Ic", "magenta"),
        ]

        table_data = []

        for key, color in mapping:
            sig = data.get(key)

            if sig is None:
                phasors.append((0, 0, color))
                table_data.append((0, 0, 0))
                continue

            rms, phase, freq = calc_phasor(sig)

            # normalizar magnitud para dibujar
            phasors.append((rms / 300, phase, color))
            table_data.append((rms, phase, freq))

        # actualizar display
        self.display.phasors = phasors
        self.display.update()

        # actualizar tabla
        for i, (rms, phase, freq) in enumerate(table_data):
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(f"{rms:.2f}"))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(f"{phase:.1f}°"))
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(f"{freq:.1f}"))