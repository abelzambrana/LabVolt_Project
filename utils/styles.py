# utils/styles.py - estilo simple para la app
def apply_app_style(window):
    css = """
    QMainWindow { background: #E6E6E6; color: #0b2b22; }
    QTabWidget::pane { border: 1px solid #444; background: #E6E6E6; }
    QGroupBox { color: #000; }
    QMenuBar { background: #f0f0f0; }
    """
    window.setStyleSheet(css)
