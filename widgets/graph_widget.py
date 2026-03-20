from PySide6 import QtWidgets, QtGui, QtCore
import math


class GraphDisplay(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.setMinimumSize(500, 400)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        w = self.width()
        h = self.height()

        # Fondo gris exterior
        painter.fillRect(self.rect(), QtGui.QColor("#c0c0c0"))

        # Área de gráfico (verde)
        margin = 20
        rect = QtCore.QRect(margin, margin, w - 2*margin, h - 2*margin)

        painter.fillRect(rect, QtGui.QColor("#0a7f7f"))

        # Ejes
        pen = QtGui.QPen(QtGui.QColor("white"))
        pen.setWidth(1)
        painter.setPen(pen)

        # eje X
        painter.drawLine(rect.left(), rect.bottom(), rect.right(), rect.bottom())

        # eje Y
        painter.drawLine(rect.left(), rect.top(), rect.left(), rect.bottom())

        # ticks X
        for i in range(21):
            x = rect.left() + i * rect.width() / 20
            painter.drawLine(int(x), rect.bottom() - 5, int(x), rect.bottom() + 5)

        # ticks Y
        for i in range(11):
            y = rect.bottom() - i * rect.height() / 10
            painter.drawLine(rect.left() - 5, int(y), rect.left() + 5, int(y))

        # números
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)

        # eje X números
        for i in range(5):
            x = rect.left() + i * rect.width() / 4
            painter.drawText(int(x), rect.bottom() + 15, str(i))

        # eje Y números
        for i in range(6):
            y = rect.bottom() - i * rect.height() / 5
            painter.drawText(rect.left() - 25, int(y), f"{i*0.2:.1f}")


class GraphWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gráfico")
        self.resize(800, 500)

        self._build_ui()

    def _build_ui(self):
        # Menú tipo Win95
        menubar = self.menuBar()
        menubar.addMenu("Archivo")
        menubar.addMenu("Ver")
        menubar.addMenu("Opciones")
        menubar.addMenu("Ayuda")

        # Toolbar simple
        toolbar = self.addToolBar("Tools")
        toolbar.addAction("📂")
        toolbar.addAction("📊")
        toolbar.addAction("📈")

        # Layout principal
        central = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(central)

        # Panel izquierdo
        left_panel = QtWidgets.QVBoxLayout()

        # Eje X
        group_x = QtWidgets.QGroupBox("Eje X")
        gx_layout = QtWidgets.QVBoxLayout(group_x)

        combo = QtWidgets.QComboBox()
        combo.addItems(["Nro. de muestra"])
        gx_layout.addWidget(combo)

        left_panel.addWidget(group_x)

        # Eje Y
        group_y = QtWidgets.QGroupBox("Eje Y")
        gy_layout = QtWidgets.QGridLayout(group_y)

        for i in range(10):
            gy_layout.addWidget(QtWidgets.QCheckBox(f""), i, 0)
            gy_layout.addWidget(QtWidgets.QCheckBox(f""), i, 1)

        left_panel.addWidget(group_y)

        layout.addLayout(left_panel, 1)

        # Área de gráfico
        self.graph = GraphDisplay()
        layout.addWidget(self.graph, 3)

        self.setCentralWidget(central)