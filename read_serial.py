import sys
import serial
import sqlite3
import numpy as np
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QTabWidget
import pyqtgraph as pg
import pyqtgraph.opengl as gl

# Importar tus funciones
import Funciones
from Funciones import guardar_medidas, guardar_usuario

# CONFIGURACIÓN
PUERTO = "COM9"
BAUDRATE = 9600
LIMITE = 50
MAX_POINTS = 200
MAX_AXIS = 50  # tamaño máximo visible en la gráfica 3D

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Medidas del Sensor")
        self.resize(1200, 700)

        # Conectar Arduino
        try:
            self.arduino = serial.Serial(PUERTO, BAUDRATE, timeout=1)
        except Exception as e:
            print("ERROR: No se pudo conectar al Arduino:", e)
            sys.exit()

        # ------------------------------
        # Layout principal
        # ------------------------------
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # Pestañas
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # ------------------------------
        # Pestaña 1: Tiempo real + 3D
        # ------------------------------
        self.tab_realtime = QWidget()
        self.tabs.addTab(self.tab_realtime, "Tiempo Real")
        layout_tab = QHBoxLayout()
        self.tab_realtime.setLayout(layout_tab)

        # Panel izquierdo: Combo + gráfica 2D
        layout_izq = QVBoxLayout()
        layout_tab.addLayout(layout_izq, stretch=3)

        self.combo_dias = QComboBox()
        self.combo_dias.addItem("Seleccionar día")
        self.combo_dias.addItems(self.obtener_dias_bd())
        self.combo_dias.currentTextChanged.connect(self.cambiar_dia_reporte)
        layout_izq.addWidget(self.combo_dias)

        self.graph = pg.PlotWidget(title="Medidas del Sensor en Tiempo Real")
        self.graph.setBackground("w")
        self.graph.showGrid(x=True, y=True)
        self.graph.addLegend()
        layout_izq.addWidget(self.graph, stretch=1)

        self.time = []
        self.data_x = []
        self.data_y = []
        self.data_z = []
        self.t = 0

        self.line_x = self.graph.plot([], [], name="X", pen=pg.mkPen('r', width=2))
        self.line_y = self.graph.plot([], [], name="Y", pen=pg.mkPen('g', width=2))
        self.line_z = self.graph.plot([], [], name="Z", pen=pg.mkPen('b', width=2))

        # Panel derecho: vector 3D
        self.view3D = gl.GLViewWidget()
        layout_tab.addWidget(self.view3D, stretch=1)
        self.view3D.setCameraPosition(distance=MAX_AXIS * 1.5)
        self.view3D.setBackgroundColor('w')

        # Ejes 3D
        self.axis3d = gl.GLAxisItem()
        self.axis3d.setSize(MAX_AXIS, MAX_AXIS, MAX_AXIS)
        # Cambiar color del eje X a rojo
        self.axis3d.axisColor = [(1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1)]
        self.view3D.addItem(self.axis3d)

        # Vector 3D (línea azul)
        self.vector_line = gl.GLLinePlotItem(pos=np.array([[0, 0, 0], [0, 0, 0]]),
                                             color=(0, 0, 1, 1), width=3, antialias=True)
        self.view3D.addItem(self.vector_line)

        # ------------------------------
        # Pestaña 2: Reporte por día
        # ------------------------------
        self.tab_reporte = QWidget()
        self.tabs.addTab(self.tab_reporte, "Reporte del Día")
        self.reporte_layout = QVBoxLayout()
        self.tab_reporte.setLayout(self.reporte_layout)

        self.graph_reporte = pg.PlotWidget(title="Reporte del Día")
        self.graph_reporte.setBackground("w")
        self.graph_reporte.addLegend()
        self.reporte_layout.addWidget(self.graph_reporte)

        self.plot_x_reporte = self.graph_reporte.plot(pen=pg.mkPen('r', width=2), name="X")
        self.plot_y_reporte = self.graph_reporte.plot(pen=pg.mkPen('g', width=2), name="Y")
        self.plot_z_reporte = self.graph_reporte.plot(pen=pg.mkPen('b', width=2), name="Z")

        # ------------------------------
        # Timer para lectura Arduino
        # ------------------------------
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    # -------------------------------------------------
    # Funciones para vector 3D
    # -------------------------------------------------
    def actualizar_vector_3D(self, x, y, z):
        mag = np.sqrt(x**2 + y**2 + z**2)
        factor = MAX_AXIS / mag if mag > 0 else 0
        vx, vy, vz = x * factor, y * factor, z * factor
        self.vector_line.setData(pos=np.array([[0, 0, 0], [vx, vy, vz]]),
                                 color=(0, 0, 1, 1))

    # -------------------------------------------------
    # Leer Arduino y actualizar gráficas
    # -------------------------------------------------
    def update_plot(self):
        if self.arduino.in_waiting > 0:
            raw = self.arduino.readline().decode("utf-8").strip()
            if not raw:
                return
            partes = raw.split(",")
            codigo = partes[0]

            # Código 2: guardar usuario
            if codigo == "2" and len(partes) == 3:
                ok = guardar_usuario(raw)
                return

            # Código 1: medidas sensor
            if codigo == "1" and len(partes) == 4:
                try:
                    x = float(partes[1])
                    y = float(partes[2])
                    z = float(partes[3])
                except:
                    return

                # Guardar en BD
                conn = sqlite3.connect("data.db")
                guardar_medidas(LIMITE, raw, conn)
                conn.close()

                # Buffers
                self.data_x.append(x)
                self.data_y.append(y)
                self.data_z.append(z)
                self.time.append(self.t)
                self.t += 1

                if len(self.data_x) > MAX_POINTS:
                    self.data_x.pop(0)
                    self.data_y.pop(0)
                    self.data_z.pop(0)
                    self.time.pop(0)

                # Actualizar gráfica
                self.line_x.setData(self.time, self.data_x)
                self.line_y.setData(self.time, self.data_y)
                self.line_z.setData(self.time, self.data_z)

                # Actualizar vector 3D
                self.actualizar_vector_3D(x, y, z)

    # -------------------------------------------------
    # Obtener días de la BD
    # -------------------------------------------------
    def obtener_dias_bd(self):
        try:
            conn = sqlite3.connect("data.db")
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT DATE(timestamp) FROM medidas ORDER BY DATE(timestamp) DESC")
            dias = [row[0] for row in cursor.fetchall()]
        except:
            dias = []
        finally:
            conn.close()
        return dias

    # -------------------------------------------------
    # Cambiar día de reporte
    # -------------------------------------------------
    def cambiar_dia_reporte(self, dia):
        if dia == "Seleccionar día":
            return
        self.actualizar_reporte(dia)

    def actualizar_reporte(self, dia):
        # Obtener datos de X,Y,Z
        x_data = Funciones.obtener_dia_x(dia)
        y_data = Funciones.obtener_dia_y(dia)
        z_data = Funciones.obtener_dia_z(dia)

        # Eje tiempo
        n = len(x_data)
        time_axis = [i * 5 for i in range(n)]

        # Actualizar gráfica
        self.plot_x_reporte.setData(time_axis, x_data)
        self.plot_y_reporte.setData(time_axis, y_data)
        self.plot_z_reporte.setData(time_axis, z_data)
        self.graph_reporte.setTitle(f"Reporte del Día: {dia}")


# ------------------------------
# INICIAR APP
# ------------------------------
app = QtWidgets.QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec())
