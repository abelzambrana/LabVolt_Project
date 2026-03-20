from PySide6 import QtWidgets, QtGui, QtCore


class DataTableWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # =========================
        # TOOLBAR (fake Win95)
        # =========================
        """toolbar = QtWidgets.QToolBar()

        actions = ["📄", "📂", "💾", "🖨", "|", "✂", "📋", "📌", "|", "📊", "📈"]

        for a in actions:
            if a == "|":
                toolbar.addSeparator()
            else:
                act = QtGui.QAction(a, self)
                toolbar.addAction(act)"""
        
        toolbar = QtWidgets.QToolBar()

        # =========================
        # ACCIONES
        # =========================

        # 📄 Nueva tabla
        act_new = QtGui.QAction("📄", self)
        act_new.triggered.connect(self.new_table)
        toolbar.addAction(act_new)

        # 📂 Abrir
        act_open = QtGui.QAction("📂", self)
        act_open.triggered.connect(self.open_file)
        toolbar.addAction(act_open)

        # 💾 Guardar
        act_save = QtGui.QAction("💾", self)
        act_save.triggered.connect(self.save_file)
        toolbar.addAction(act_save)

        # 🖨 Exportar PDF
        act_print = QtGui.QAction("🖨", self)
        act_print.triggered.connect(self.export_pdf)
        toolbar.addAction(act_print)

        toolbar.addSeparator()

        # ➕ Insertar fila
        act_insert = QtGui.QAction("->|", self)
        act_insert.triggered.connect(self.insert_row)
        toolbar.addAction(act_insert)

        # ➖ Eliminar fila
        act_delete_row = QtGui.QAction("|->", self)
        act_delete_row.triggered.connect(self.delete_row)
        toolbar.addAction(act_delete_row)

        # ✂ Cortar
        act_cut = QtGui.QAction("✂", self)
        act_cut.triggered.connect(self.cut_cells)
        toolbar.addAction(act_cut)

        # 📋 Pegar
        act_paste = QtGui.QAction("📋", self)
        act_paste.triggered.connect(self.paste_cells)
        toolbar.addAction(act_paste)

        # 📄 Copiar
        act_copy = QtGui.QAction("📄📄", self)
        act_copy.triggered.connect(self.copy_cells)
        toolbar.addAction(act_copy)

        # 🗑 Eliminar tabla
        act_clear = QtGui.QAction("🗑", self)
        act_clear.triggered.connect(self.clear_table)
        toolbar.addAction(act_clear)

        toolbar.addSeparator()

        # 📈 Gráfico
        act_graph = QtGui.QAction("📈", self)
        act_graph.triggered.connect(self.open_graph)
        toolbar.addAction(act_graph)



        layout.addWidget(toolbar)

        # =========================
        # TABLA
        # =========================
        self.table = QtWidgets.QTableWidget(50, 10)

        # estilo Win95
        self.table.setStyleSheet("""
            QTableWidget {
                background: #ffffff;
                gridline-color: #a0a0a0;
                border: 2px solid #808080;
            }
            QHeaderView::section {
                background: #c0c0c0;
                border: 1px solid #808080;
                padding: 2px;
            }
        """)

        # encabezados
        for col in range(10):
            self.table.setHorizontalHeaderItem(col, QtWidgets.QTableWidgetItem(""))

        for row in range(50):
            self.table.setVerticalHeaderItem(row, QtWidgets.QTableWidgetItem(str(row)))

        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.table)

        # =========================
        # BARRA INFERIOR (status)
        # =========================
        status_layout = QtWidgets.QHBoxLayout()

        self.status_label = QtWidgets.QLabel("Fila: 0   Col: 0")
        self.status_label.setStyleSheet("background:#c0c0c0; border:1px solid #808080; padding:2px;")

        status_layout.addWidget(self.status_label)
        status_layout.addStretch()

        layout.addLayout(status_layout)

        # =========================
        # EVENTO DE SELECCIÓN
        # =========================
        self.table.currentCellChanged.connect(self.update_status)

    def update_status(self, row, col, *_):
        self.status_label.setText(f"Fila: {row}   Col: {col}")


    # =========================
    # FUNCIONES TOOLBAR
    # =========================

    def new_table(self):
        self.table.clearContents()


    def open_file(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Abrir archivo", "", "CSV (*.csv);;Excel (*.xlsx)"
        )
        if not path:
            return

        import csv
        if path.endswith(".csv"):
            with open(path, newline="") as f:
                reader = csv.reader(f)
                for r, row in enumerate(reader):
                    for c, val in enumerate(row):
                        self.table.setItem(r, c, QtWidgets.QTableWidgetItem(val))


    def save_file(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Guardar archivo", "", "CSV (*.csv)"
        )
        if not path:
            return

        import csv
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            for r in range(self.table.rowCount()):
                row_data = []
                for c in range(self.table.columnCount()):
                    item = self.table.item(r, c)
                    row_data.append(item.text() if item else "")
                writer.writerow(row_data)


    def export_pdf(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Exportar PDF", "", "PDF (*.pdf)"
        )
        if not path:
            return

        printer = QtGui.QPageLayout()
        doc = QtGui.QTextDocument()

        html = "<table border='1' cellspacing='0' cellpadding='2'>"

        for r in range(self.table.rowCount()):
            html += "<tr>"
            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                val = item.text() if item else ""
                html += f"<td>{val}</td>"
            html += "</tr>"

        html += "</table>"

        doc.setHtml(html)

        printer = QtGui.QPdfWriter(path)
        doc.print(printer)


    def insert_row(self):
        row = self.table.currentRow()
        self.table.insertRow(row + 1)


    def delete_row(self):
        row = self.table.currentRow()
        self.table.removeRow(row)


    def copy_cells(self):
        selected = self.table.selectedRanges()
        if not selected:
            return

        r = selected[0]
        text = ""

        for i in range(r.topRow(), r.bottomRow() + 1):
            row_text = []
            for j in range(r.leftColumn(), r.rightColumn() + 1):
                item = self.table.item(i, j)
                row_text.append(item.text() if item else "")
            text += "\t".join(row_text) + "\n"

        QtWidgets.QApplication.clipboard().setText(text)


    def cut_cells(self):
        self.copy_cells()
        for item in self.table.selectedItems():
            item.setText("")


    def paste_cells(self):
        text = QtWidgets.QApplication.clipboard().text()
        row = self.table.currentRow()
        col = self.table.currentColumn()

        for r, line in enumerate(text.split("\n")):
            for c, val in enumerate(line.split("\t")):
                self.table.setItem(row + r, col + c, QtWidgets.QTableWidgetItem(val))


    def clear_table(self):
        self.table.clearContents()


    def open_graph(self):
        from widgets.graph_widget import GraphWindow

        self.graph_window = GraphWindow()
        self.graph_window.show()