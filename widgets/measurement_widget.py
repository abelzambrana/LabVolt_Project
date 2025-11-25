# widgets/measurement_widget.py
# Contenedor 3x4 con los DisplayWidget (200x200).
from PySide6 import QtWidgets
from .display_widget import DisplayWidget

class MeasurementWidget(QtWidgets.QWidget):
    """
    Grid 3x4 con displays cuadrados 200x200 en el orden:
    fila1: E1, E2, E3, T
    fila2: I1, I2, I3, N
    fila3: PQS1, PQS2, PQS3, Pm
    """
    def __init__(self, channels_def, compact=True, parent=None):
        super().__init__(parent)
        self.channels = channels_def
        self.compact = compact
        self._build_ui()

    def _build_ui(self):
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(10)
        grid.setContentsMargins(8,8,8,8)
        rows, cols = 3, 4

        color_map = {
            "E": "#0078ff", "I": "#ff3b3b", "PQS": "#b14cff",
            "T": "#007a2f", "N": "#8b5a2b", "Pm": "#f2c94c"
        }

        self.display_objs = {}
        for idx, (title, ch_name, unit) in enumerate(self.channels):
            r = idx // cols
            c = idx % cols
            t_up = title.upper()
            if t_up.startswith("PQS"):
                key = "PQS"
            elif t_up.startswith("PM"):
                key = "Pm"
            else:
                key = t_up[0]
            title_color = color_map.get(key, "#0078ff")
            # asignación de mode_type (con excepción para N)
            if t_up.startswith("E") or t_up.startswith("I"):
                mode_type = "ca_cc"
            elif t_up.startswith("PQS"):
                mode_type = "pqs"
            elif t_up.startswith("T") or t_up.startswith("PM"):
                mode_type = "nc_c"
            elif t_up.startswith("N"):
                # N: mostrar botón pero sin función
                mode_type = "none_with_button"
            else:
                mode_type = "none"

            disp = DisplayWidget(id_label=title, ch_name=ch_name, unit=unit,
                                 title_color=title_color, mode_type=mode_type, compact=self.compact)
            grid.addWidget(disp, r, c)
            self.display_objs[ch_name] = disp

        # evitar que el grid expanda los widgets (mantener 200x200)
        for rr in range(rows):
            grid.setRowStretch(rr, 0)
        for cc in range(cols):
            grid.setColumnStretch(cc, 0)

        self.setLayout(grid)

    def set_value(self, ch_name, value):
        """Setea el valor numérico en el display indicado (None->apagar)."""
        disp = self.display_objs.get(ch_name)
        if disp is None:
            return
        if value is None:
            disp.set_force_off(True)
        else:
            disp.set_force_off(False)
            disp.set_value(value)

    def force_all_off(self):
        """Apaga todos los displays (placeholder cuando no hay datos)."""
        for d in self.display_objs.values():
            d.set_force_off(True)
