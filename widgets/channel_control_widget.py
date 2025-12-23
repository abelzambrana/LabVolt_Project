# widgets/channel_control_widget.py
# Control de canal del osciloscopio (estilo LabVolt / Windows 95)

from PySide6 import QtWidgets, QtGui, QtCore


class ChannelControlWidget(QtWidgets.QGroupBox):
    """
    Widget de control para un canal del osciloscopio.
    Incluye:
    - Selector de entrada
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
        entry_combo = QtWidgets.QComboBox()
        entry_combo.addItem("Ninguna")

        entry_row.addWidget(entry_label)
        entry_row.addWidget(entry_combo)
        layout.addLayout(entry_row)

        # Botones DC / AC / GND
        btn_row = QtWidgets.QHBoxLayout()

        self.btn_dc = QtWidgets.QPushButton("─")
        self.btn_ac = QtWidgets.QPushButton("∿")
        self.btn_gnd = QtWidgets.QPushButton("⏚")

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
                """
            )

        btn_row.addWidget(self.btn_dc)
        btn_row.addWidget(self.btn_ac)
        btn_row.addWidget(self.btn_gnd)

        layout.addLayout(btn_row)
