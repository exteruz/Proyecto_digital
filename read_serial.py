from PyQt6 import QtWidgets, QtCore
import pyqtgraph as pg
import numpy as np
import Funciones  # tu módulo con funciones de DB

def generar_eje_x(array_y, intervalo_segundos=5):
    """Genera eje X en segundos para un array de valores Y"""
    n = len(array_y)
    return [i * intervalo_segundos for i in range(n)]

class SensorReportTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # --- Layout principal horizontal ---
        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        # --- Izquierda: etiquetas + gráfica ---
        left_layout = QtWidgets.QVBoxLayout()
        layout.addLayout(left_layout, stretch=3)

        # Etiquetas de último valor / Danger
        self.labels_layout = QtWidgets.QHBoxLayout()
        left_layout.addLayout(self.labels_layout)
        self.label_danger = QtWidgets.QLabel("Danger: 0")
        self.labels_layout.addWidget(self.label_danger)
        self.labels_layout.addStretch()

        # Gráfica de tendencia
        self.plot_widget = pg.PlotWidget(title="Tendencia X,Y,Z")
        self.plot_widget.setBackground("#D3D3D3")
        left_layout.addWidget(self.plot_widget)

        # Configurar ejes en negro
        self.plot_widget.getAxis("left").setPen(pg.mkPen("#000000", width=2))
        self.plot_widget.getAxis("bottom").setPen(pg.mkPen("#000000", width=2))
        self.plot_widget.getAxis("left").setTextPen(pg.mkPen("#000000"))
        self.plot_widget.getAxis("bottom").setTextPen(pg.mkPen("#000000"))

        # Líneas de cada eje
        self.plot_x = self.plot_widget.plot(pen=pg.mkPen(color=(255, 0, 0), width=2), name="X")
        self.plot_y = self.plot_widget.plot(pen=pg.mkPen(color=(0, 255, 0), width=2), name="Y")
        self.plot_z = self.plot_widget.plot(pen=pg.mkPen(color=(0, 0, 255), width=2), name="Z")

        # --- Derecha: tabla de estadísticas ---
        right_layout = QtWidgets.QVBoxLayout()
        layout.addLayout(right_layout, stretch=1)
        right_layout.addStretch()  # empuja la tabla hacia abajo

        self.stats_table = QtWidgets.QTableWidget()
        self.stats_table.setColumnCount(4)
        self.stats_table.setHorizontalHeaderLabels(["Eje", "Promedio", "Máximo", "Mínimo"])
        self.stats_table.setRowCount(3)
        self.stats_table.setVerticalHeaderLabels(["X", "Y", "Z"])
        right_layout.addWidget(self.stats_table)

        # --- Botones debajo del layout horizontal ---
        self.buttons_layout = QtWidgets.QHBoxLayout()
        left_layout.addLayout(self.buttons_layout)
        self.refresh_button = QtWidgets.QPushButton("Actualizar")
        self.buttons_layout.addWidget(self.refresh_button)
        self.refresh_button.clicked.connect(self.actualizar_reporte)

        # Inicializar reporte
        self.actualizar_reporte()

    def actualizar_reporte(self):
        # Obtener datos desde la base de datos
        x_data = Funciones.obtener_dia_x("2025-11-22")
        y_data = Funciones.obtener_dia_y("2025-11-22")
        z_data = Funciones.obtener_dia_z("2025-11-22")

        if not x_data or not y_data or not z_data:
            return

        # Evaluar Danger si algún valor supera límite
        danger = int(any(val > 100 for val in [x_data[-1], y_data[-1], z_data[-1]]))
        self.label_danger.setText(f"Danger: {danger}")

        # Actualizar gráfica
        time_axis = generar_eje_x(x_data, intervalo_segundos=5)
        self.plot_x.setData(time_axis, x_data)
        self.plot_y.setData(time_axis, y_data)
        self.plot_z.setData(time_axis, z_data)

        # Calcular estadísticas
        stats = [
            ("X", np.mean(x_data), np.max(x_data), np.min(x_data)),
            ("Y", np.mean(y_data), np.max(y_data), np.min(y_data)),
            ("Z", np.mean(z_data), np.max(z_data), np.min(z_data)),
        ]

        for i, row in enumerate(stats):
            for j, val in enumerate(row[1:], 1):
                self.stats_table.setItem(i, j, QtWidgets.QTableWidgetItem(f"{val:.2f}"))

# -------------------- Código principal --------------------
app = QtWidgets.QApplication([])

main_window = QtWidgets.QMainWindow()
main_window.setWindowTitle("Dashboard Sensores")
main_window.resize(1200, 700)

tabs = QtWidgets.QTabWidget()
main_window.setCentralWidget(tabs)

# Agregar la pestaña del sensor
sensor_tab = SensorReportTab()
tabs.addTab(sensor_tab, "Reporte Sensor")

main_window.show()
app.exec()
