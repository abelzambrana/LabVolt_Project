# widgets/display_widget.py
# Display final 200x200 (LCD y dígitos mantienen tamaño actual), editable expandible,
# unidad con misma anchura que editable (texto a la derecha), botón vacío para 'N'.
from PySide6 import QtWidgets, QtGui, QtCore
import os

# Ruta absoluta a la fuente (confirmada por el usuario)
_FONT_ABS_PATH = r"C:\Users\Tepsi\Documents\LabVolt_Project\fonts\digital-7.ttf"

class ClickableLabel(QtWidgets.QLabel):
    """QLabel que emite clicked() al pulsar (usado para nombre del display)."""
    clicked = QtCore.Signal()
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.clicked.emit()

def _load_7seg_font():
    """Intenta cargar la fuente 7-seg desde la ruta absoluta. Devuelve family o None."""
    try:
        p = os.path.normpath(_FONT_ABS_PATH)
        if os.path.exists(p):
            font_id = QtGui.QFontDatabase.addApplicationFont(p)
            if font_id != -1:
                families = QtGui.QFontDatabase.applicationFontFamilies(font_id)
                if families:
                    return families[0]
    except Exception:
        pass
    return None

class DisplayWidget(QtWidgets.QFrame):
    """
    Display compacto cuadrado 200x200:
      - nombre izquierda (clicable) con apariencia botón hundido
      - editable derecha (apariencia botón hundido) - texto centrado y EXPANDIBLE
      - LCD central verde (misma altura y tamaño de dígitos que tenés ahora)
      - botón inferior izquierdo (modo) y unidad inferior derecha (MISMA anchura que editable,
        texto alineado a la derecha)
      - para el display 'N' el mode_type 'none_with_button' muestra botón sin texto y deshabilitado.
    """
    def __init__(self, id_label="E1", ch_name="Va", unit="V",
                 title_color="#0078ff", mode_type="ca_cc", compact=True, parent=None):
        super().__init__(parent)
        # propiedades del widget
        self.id_label = id_label
        self.ch_name = ch_name
        self.unit_base = unit
        self.title_color = title_color
        self.mode_type = mode_type
        self.compact = compact

        # estado interno y modos disponibles
        self.value_visible = True
        self._last_value = None
        self._mode_index = 0
        self._modes = {
            "ca_cc": (["CA", "CC"], [self.unit_base, self.unit_base]),
            "nc_c":  (["NC", "C"], [self.unit_base, self.unit_base]),
            "pqs":   (["P1", "Q1", "S1"], ["W", "VAR", "VA"]),
            "none":  ([""], [self.unit_base]),
            "none_with_button": ([""], [self.unit_base]),
        }

        # cargo la fuente 7-seg (si existe)
        self._seven_family = _load_7seg_font()

        # construyo UI y fijo tamaño cuadrado 200x200
        self._build_ui()
        self.setFixedSize(200, 200)

    def _build_ui(self):
        # panel con fondo gris claro
        self.setFrameShape(QtWidgets.QFrame.Panel)
        self.setLineWidth(2)
        self.setStyleSheet("QFrame { background: #E6E6E6; }")

        # layout vertical principal
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setContentsMargins(6,6,6,6)
        vbox.setSpacing(6)

        # ---------- TOP ROW: [NAME][EDITABLE (expandible)] ----------
        top_row = QtWidgets.QHBoxLayout()
        top_row.setSpacing(6)

        # NAME: ancho fijo, clicable, estilo hundido
        self.name_label = ClickableLabel(self.id_label)
        self.name_label.setFixedWidth(44)
        f_title = QtGui.QFont("Arial", 9, QtGui.QFont.Bold)
        self.name_label.setFont(f_title)
        self.name_label.setStyleSheet(
            "QLabel { background: #f0f0f0; color: %s; padding:2px; "
            "border-top: 2px solid #ffffff; border-left: 2px solid #ffffff; "
            "border-bottom: 2px solid #7a7a7a; border-right: 2px solid #7a7a7a; }" % self.title_color
        )
        self.name_label.setAlignment(QtCore.Qt.AlignCenter)
        self.name_label.clicked.connect(self._on_name_clicked)

        # EDITABLE: expandible para ocupar todo el ancho restante (centrado)
        self.edit_label = QtWidgets.QLineEdit()
        self.edit_label.setPlaceholderText(self.id_label)
        self.edit_label.setFixedHeight(20)
        # expandible: ocupa el espacio restante de la fila superior
        self.edit_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.edit_label.setAlignment(QtCore.Qt.AlignCenter)  # texto centrado
        self.edit_label.setStyleSheet(
            "QLineEdit { background: #f0f0f0; padding:2px; "
            "border-top: 2px solid #ffffff; border-left: 2px solid #ffffff; "
            "border-bottom: 2px solid #7a7a7a; border-right: 2px solid #7a7a7a; }"
        )

        top_row.addWidget(self.name_label)
        top_row.addWidget(self.edit_label)   # expandible por defecto
        vbox.addLayout(top_row)

        # ---------- CENTER: LCD (mantenemos EXACTO tamaño que confirmaste) ----------
        lcd_height = 90  # mantenido
        self.value_label = QtWidgets.QLabel(" 0.000 ", alignment=QtCore.Qt.AlignCenter)
        self.value_label.setFixedHeight(lcd_height)

        # fuente: misma que ya tienes (mantener tamaño actual)
        if self._seven_family:
            lcd_font = QtGui.QFont(self._seven_family, 45)
            # intento activar cursiva — la fuente puede o no soportarla
            lcd_font.setItalic(True)
        else:
            lcd_font = QtGui.QFont("Courier", 40, QtGui.QFont.Bold)
            lcd_font.setItalic(True)
        self.value_label.setFont(lcd_font)

        # estilo LCD verde con borde tipo inset
        lcd_css = (
            "QLabel { color: #00ff66; "
            "background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #006e2d, stop:1 #004616); "
            "border-top: 2px solid #a8e0b8; border-left: 2px solid #a8e0b8; "
            "border-bottom: 2px solid #08381f; border-right: 2px solid #08381f; padding:4px; }"
        )
        self.value_label.setStyleSheet(lcd_css)
        vbox.addWidget(self.value_label, stretch=1)

        # ---------- BOTTOM ROW: [MODE BUTTON] [UNIT (same width as editable)] ----------
        bottom_row = QtWidgets.QHBoxLayout()
        bottom_row.setSpacing(6)

        # boton modo: ancho fijo (consistente con name_label)
        self.mode_button = QtWidgets.QPushButton()
        self.mode_button.setFixedSize(44, 22)
        self.mode_button.setFont(QtGui.QFont("Arial", 8))
        self.mode_button.setStyleSheet(
            "QPushButton { background:#f0f0f0; border-top:2px solid #ffffff; border-left:2px solid #ffffff; "
            "border-bottom:2px solid #7a7a7a; border-right:2px solid #7a7a7a; }"
            "QPushButton:pressed { border-top:2px solid #7a7a7a; border-left:2px solid #7a7a7a; "
            "border-bottom:2px solid #ffffff; border-right:2px solid #ffffff; }"
        )
        # Conexión del botón (salvo si es 'none_with_button')
        self.mode_button.clicked.connect(self._on_mode_clicked)

        # UNIT: misma anchura visual que edit_label (ambos expandibles),
        # usando QSizePolicy.Expanding para que compartan el mismo espacio relativo.
        self.unit_label = QtWidgets.QLabel(self.unit_base)
        self.unit_label.setFixedHeight(20)
        self.unit_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.unit_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)  # texto a la derecha
        self.unit_label.setStyleSheet(
            "QLabel { background: #f0f0f0; padding-right:6px; "
            "border-top: 2px solid #ffffff; border-left: 2px solid #ffffff; "
            "border-bottom: 2px solid #7a7a7a; border-right: 2px solid #7a7a7a; }"
        )

        bottom_row.addWidget(self.mode_button)
        bottom_row.addWidget(self.unit_label)
        vbox.addLayout(bottom_row)

        # Inicializar modo / unidad
        modes, units = self._modes.get(self.mode_type, ([""], [self.unit_base]))
        if self.mode_type == "none":
            self.mode_button.hide()
        elif self.mode_type == "none_with_button":
            # mostrar botón pero sin texto y deshabilitado (para N)
            self.mode_button.setText("")
            self.mode_button.setEnabled(False)
        else:
            self.mode_button.setText(modes[self._mode_index])
            self.unit_label.setText(units[self._mode_index])

    # ---------- Interacciones ----------
    def _on_name_clicked(self):
        """Al clicar el nombre, sólo se oscurece el valor central (no todo el cuadro)."""
        self.value_visible = not self.value_visible
        if not self.value_visible:
            # Apagar SOLO el LCD
            self.value_label.setStyleSheet("QLabel { background: black; color: black; border:2px solid #111; }")
            self.value_label.setText("")
        else:
            # Restaurar font y estilo LCD (mismo tamaño)
            if self._seven_family:
                f = QtGui.QFont(self._seven_family, 45)
                f.setItalic(True)
                self.value_label.setFont(f)
            else:
                f = QtGui.QFont("Courier", 40, QtGui.QFont.Bold)
                f.setItalic(True)
                self.value_label.setFont(f)
            lcd_css = (
                "QLabel { color: #00ff66; "
                "background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #006e2d, stop:1 #004616); "
                "border-top: 2px solid #a8e0b8; border-left: 2px solid #a8e0b8; "
                "border-bottom: 2px solid #08381f; border-right: 2px solid #08381f; padding:4px; }"
            )
            self.value_label.setStyleSheet(lcd_css)
            if self._last_value is None:
                self.value_label.setText(" 0.000 ")
            else:
                try:
                    self.value_label.setText(f"{self._last_value:7.3f}")
                except Exception:
                    self.value_label.setText(str(self._last_value))

    def _on_mode_clicked(self):
        # Si es 'none_with_button' no hace nada
        if self.mode_type == "none_with_button":
            return
        modes, units = self._modes.get(self.mode_type, ([""], [self.unit_base]))
        if not modes:
            return
        self._mode_index = (self._mode_index + 1) % len(modes)
        self.mode_button.setText(modes[self._mode_index])
        self.unit_label.setText(units[self._mode_index])

    # ---------- API pública ----------
    def set_value(self, value):
        """Actualiza el valor mostrado (si el LCD está encendido)."""
        try:
            self._last_value = float(value)
        except Exception:
            self._last_value = None
        if not getattr(self, "value_visible", True):
            return
        if self._last_value is None:
            self.value_label.setText("   -   ")
        else:
            try:
                self.value_label.setText(f"{self._last_value:7.3f}")
            except Exception:
                self.value_label.setText(str(self._last_value))

    def set_force_off(self, enable=True):
        """Forzar LCD apagado/encendido."""
        if enable:
            self.value_visible = False
            self.value_label.setStyleSheet("QLabel { background: black; color: black; border:2px solid #111; }")
            self.value_label.setText("")
        else:
            self.value_visible = True
            if self._seven_family:
                f = QtGui.QFont(self._seven_family, 45)
                f.setItalic(True)
                self.value_label.setFont(f)
            else:
                f = QtGui.QFont("Courier", 40, QtGui.QFont.Bold)
                f.setItalic(True)
                self.value_label.setFont(f)
            lcd_css = (
                "QLabel { color: #00ff66; "
                "background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #006e2d, stop:1 #004616); "
                "border-top: 2px solid #a8e0b8; border-left: 2px solid #a8e0b8; "
                "border-bottom: 2px solid #08381f; border-right: 2px solid #08381f; padding:4px; }"
            )
            self.value_label.setStyleSheet(lcd_css)
            if self._last_value is None:
                self.value_label.setText(" 0.000 ")
            else:
                try:
                    self.value_label.setText(f"{self._last_value:7.3f}")
                except Exception:
                    self.value_label.setText(str(self._last_value))

