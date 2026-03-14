# widgets/channel_control_widget.py
# Control de canal del osciloscopio (estilo LabVolt / Windows 95)

from PySide6 import QtWidgets, QtGui, QtCore


class ChannelControlWidget(QtWidgets.QGroupBox):
    """
    Widget de control para un canal del osciloscopio.
    Incluye:
    - Selector de entrada
    - Selector de amplitud
    - Botones DC / AC / GND (solo visuales por ahora)
    """

    def __init__(self, title="Can1", color=QtGui.QColor("green"), parent=None):
        super().__init__(parent)

        self.setTitle(title)
        self.setStyleSheet(
            f"""
            QGroupBox {{
                font-weight: bold;
                color: {color.name()};
                border: 2px solid #808080;
                margin-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 4px;
            }}
            """
        )

        self._build_ui()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(4)

        # Entrada
        entry_row = QtWidgets.QHBoxLayout()
        entry_label = QtWidgets.QLabel("Entrada")
        self.entry_combo = QtWidgets.QComboBox()
        self.entry_combo.addItems([
            "Ninguna",
            "E1",
            "E2",
            "E3",
            "I1",
            "I2",
            "I3",
            "P1",
            "P2",
            "P3",
            "T",
            "N",
            "Pm",
            "EA-1",
            "EA-2",
            "EA-3",
            "EA-4",
            "EA-5",
            "EA-6",
            "EA-7",
            "EA-8"
        ])
        entry_row.addWidget(entry_label)
        entry_row.addWidget(self.entry_combo)
        layout.addLayout(entry_row)
        
        # Lista desplegable de Amplitud por división
        
        volt_row = QtWidgets.QHBoxLayout()
        volt_label = QtWidgets.QLabel("Amplitud")

        self.volt_combo = QtWidgets.QComboBox()
        volt_row.addWidget(volt_label)
        volt_row.addWidget(self.volt_combo)
        layout.addLayout(volt_row)

        self.entry_combo.currentTextChanged.connect(self.update_amplitude_options)


        # Botones DC / AC / GND
        btn_row = QtWidgets.QHBoxLayout()

        #self.btn_dc = QtWidgets.QPushButton("─")
        self.btn_dc = QtWidgets.QPushButton("⎓")
        self.btn_ac = QtWidgets.QPushButton("∿")
        self.btn_gnd = QtWidgets.QPushButton("⏚")


        for btn in (self.btn_dc, self.btn_ac, self.btn_gnd):
            btn.setCheckable(True)
        
        self.coupling_group = QtWidgets.QButtonGroup(self)
        self.coupling_group.setExclusive(True)

        self.coupling_group.addButton(self.btn_dc)
        self.coupling_group.addButton(self.btn_ac)
        self.coupling_group.addButton(self.btn_gnd)

        self.btn_dc.setChecked(True)

        for btn in (self.btn_dc, self.btn_ac, self.btn_gnd):
            btn.setFixedSize(26, 22)
            btn.setStyleSheet(
                """
                QPushButton {
                    background: #e0e0e0;
                    border-top: 2px solid #ffffff;
                    border-left: 2px solid #ffffff;
                    border-bottom: 2px solid #7a7a7a;
                    border-right: 2px solid #7a7a7a;
                }
                QPushButton:pressed {
                    border-top: 2px solid #7a7a7a;
                    border-left: 2px solid #7a7a7a;
                    border-bottom: 2px solid #ffffff;
                    border-right: 2px solid #ffffff;
                }

                QPushButton:checked {
                    background: #c6c6c6;
                    border-top: 2px solid #7a7a7a;
                    border-left: 2px solid #7a7a7a;
                    border-bottom: 2px solid #ffffff;
                    border-right: 2px solid #ffffff;
                }

                """
            )

        btn_row.addWidget(self.btn_dc)
        btn_row.addWidget(self.btn_ac)
        btn_row.addWidget(self.btn_gnd)

        layout.addLayout(btn_row)


    def update_amplitude_options(self, text):

            self.volt_combo.clear()

    # ---------------- VOLTAJE ----------------
            if text.startswith("E") or text.startswith("EA"):
                self.volt_combo.addItems([
                    "2 V/div.",
                    "5 V/div.",
                    "10 V/div.",
                    "20 V/div.",
                    "50 V/div.",
                    "100 V/div.",
                    "200 V/div."
                ])

    # ---------------- CORRIENTE ----------------
            elif text.startswith("I"):
                self.volt_combo.addItems([
                    "0.05 A/div.",
                    "0.1 A/div.",
                    "0.2 A/div.",
                    "0.5 A/div.",
                    "1 A/div.",
                    "2 A/div.",
                    "5 A/div."
                ])

    # ---------------- POTENCIA ----------------
            elif text.startswith("P"):
                self.volt_combo.addItems([
                    "5 W/div.",
                    "10 W/div.",
                    "20 W/div.",
                    "50 W/div.",
                    "100 W/div.",
                    "200 W/div.",
                    "500 W/div."
                ])

    # ---------------- TORQUE ----------------
            elif text == "T":
                self.volt_combo.addItems([
                    "0.1 N.m/div.",
                    "0.2 N.m/div.",
                    "0.5 N.m/div.",
                    "1 N.m/div.",
                    "2 N.m/div.",
                    "5 N.m/div.",
                    "10 N.m/div."
                ])

    # ---------------- VELOCIDAD ----------------
            elif text == "N":
                self.volt_combo.addItems([
                    "20 rpm/div.",
                    "50 rpm/div.",
                    "100 rpm/div.",
                    "200 rpm/div.",
                    "500 rpm/div.",
                    "1000 rpm/div.",
                    "2000 rpm/div."
                ])

    # ---------------- NINGUNA ----------------
            else:
                self.volt_combo.addItem("Sin señal")