import sys
import serial
import sqlite3
<<<<<<< HEAD
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
=======
import math
from datetime import date
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QTabWidget, QMessageBox,
    QLabel, QSpacerItem, QSizePolicy, QTableWidget, QTableWidgetItem, QPushButton,
    QHeaderView
)
import pyqtgraph as pg

# Importar funciones externas
import Funciones
from Funciones import guardar_medidas, guardar_usuario, obtener_usuarios, obtener_todos_incidentes

# CONFIGURACIÓN
PUERTO = "COM3"
BAUDRATE = 115200
LIMITE = 4000
MAX_POINTS = 200
INCIDENTS_LIMIT = 200  # máximo filas a mostrar en tabla de incidentes
>>>>>>> b4f9df8 (agregando)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Medidas del Sensor")
        self.resize(1200, 700)

<<<<<<< HEAD
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
=======
        # Evitar ventanas repetidas de peligro
        self.peligro_mostrado = False

        # Conectar UART
        try:
            self.arduino = serial.Serial(PUERTO, BAUDRATE, timeout=1)
        except Exception as e:
            print("ERROR: No se pudo conectar al dispositivo:", e)
            sys.exit()

        # ------------------------------
        # Layout principal
        # ------------------------------
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # ------------------------------
        # Pestaña 1: Tiempo real
        # ------------------------------
        self.tab_realtime = QWidget()
        self.tabs.addTab(self.tab_realtime, "Tiempo Real")
        layout_tab = QHBoxLayout()
        self.tab_realtime.setLayout(layout_tab)

        # --- Layout izquierdo: controles + gráfico
        layout_izq = QVBoxLayout()
        layout_tab.addLayout(layout_izq, stretch=3)

        self.combo_dias = QComboBox()
        self.combo_dias.addItem("Seleccionar día")
        # Poblamos días excluyendo el día actual
        self.combo_dias.addItems(self.obtener_dias_bd_excluyendo_hoy())
        self.combo_dias.currentTextChanged.connect(self.cambiar_dia_reporte)
        layout_izq.addWidget(self.combo_dias)

        # Gráfico tiempo real
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

        # --- Layout derecho: recuadro de magnitud y espacio para más widgets
        layout_der = QVBoxLayout()
        layout_tab.addLayout(layout_der, stretch=1)

        # Recuadro de magnitud (arriba a la derecha)
        self.mag_label = QLabel("Magnitud:\n0.00")
        self.mag_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.mag_label.setFixedSize(180, 80)
        # Estilo inicial (blanco con borde gris)
        self.mag_label.setStyleSheet("""
            QLabel {
                background-color: #ffffff;
                border: 2px solid #8c8c8c;
                border-radius: 8px;
                font-size: 18px;
                font-weight: bold;
                color: #000000;
            }
        """)
        layout_der.addWidget(self.mag_label, alignment=QtCore.Qt.AlignmentFlag.AlignTop)

        # Espaciador para empujar el recuadro hacia arriba
        layout_der.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

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
        # Pestaña 3: Usuarios (tabla)
        # ------------------------------
        self.tab_usuarios = QWidget()
        self.tabs.addTab(self.tab_usuarios, "Usuarios")
        usuarios_layout = QVBoxLayout()
        self.tab_usuarios.setLayout(usuarios_layout)

        # Botón para refrescar
        refresh_btn = QPushButton("Refrescar lista de usuarios")
        refresh_btn.clicked.connect(self.refresh_users_table)
        usuarios_layout.addWidget(refresh_btn, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)

        # Tabla de usuarios
        self.table_users = QTableWidget()
        self.table_users.setColumnCount(3)
        self.table_users.setHorizontalHeaderLabels(["ID", "User", "Password (SHA256)"])
        self.table_users.horizontalHeader().setStretchLastSection(True)
        # Ocultar numeración de filas (encabezado vertical)
        self.table_users.verticalHeader().setVisible(False)
        usuarios_layout.addWidget(self.table_users)

        # Cargar inicialmente
        self.refresh_users_table()

        # ------------------------------
        # Pestaña 4: Incidentes (tabla scrollable)
        # ------------------------------
        self.tab_incidentes = QWidget()
        self.tabs.addTab(self.tab_incidentes, "Incidentes")
        inc_layout = QVBoxLayout()
        self.tab_incidentes.setLayout(inc_layout)

        # Botón refrescar incidentes
        refresh_inc_btn = QPushButton("Refrescar incidentes")
        refresh_inc_btn.clicked.connect(self.refresh_incidents_table)
        inc_layout.addWidget(refresh_inc_btn, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)

        # Tabla de incidentes (scrollable por defecto)
        self.table_incidents = QTableWidget()
        self.table_incidents.setColumnCount(5)
        self.table_incidents.setHorizontalHeaderLabels(["Timestamp", "X", "Y", "Z", "Danger"])
        self.table_incidents.horizontalHeader().setStretchLastSection(False)
        # permitir scroll vertical y horizontal si es necesario (está por defecto)
        self.table_incidents.setMinimumHeight(200)
        self.table_incidents.verticalHeader().setVisible(False)

        # Ajustes de tamaños: timestamp más grande, otras columnas automáticas
        header = self.table_incidents.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)       # timestamp estira
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        inc_layout.addWidget(self.table_incidents)

        # Cargar inicialmente incidentes
        self.refresh_incidents_table()

        # ------------------------------
        # Timer UART
        # ------------------------------
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)  # 100 ms
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    # =======================================
    # LECTURA UART
    # =======================================
    def update_plot(self):
        if self.arduino.in_waiting > 0:
            raw = self.arduino.readline().decode("utf-8", errors="ignore").strip()
            if not raw:
                return

            partes = raw.split(",")
            codigo = partes[0]

            # =======================================
            # Código 2 → Guardar usuario
            # =======================================
            if codigo == "2" and len(partes) == 3:
                ok = guardar_usuario(raw)
                msg = QMessageBox()
                msg.setWindowTitle("Usuario Guardado")
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setText(f"El usuario '{partes[1]}' fue guardado correctamente.")
                msg.exec()
                # refrescar tabla de usuarios automáticamente (solo añadir nuevos)
                self.refresh_users_table()
                return

            # =======================================
            # Código 3 → LOGIN
            # =======================================
            if codigo == "3" and len(partes) == 3:
                ok = Funciones.comprobar_login(raw)
                if ok:
                    self.arduino.write(b"T\n")
                else:
                    self.arduino.write(b"F\n")
                msg = QMessageBox()
                msg.setWindowTitle("Inicio de Sesión")
                if ok:
                    msg.setIcon(QMessageBox.Icon.Information)
                    msg.setText(f"Inicio de sesión exitoso para el usuario '{partes[1]}'")
                else:
                    msg.setIcon(QMessageBox.Icon.Warning)
                    msg.setText("Usuario o contraseña incorrectos")
                msg.exec()
                return

            # =======================================
            # Código 1 → Medidas del sensor
            # =======================================
            if codigo == "1" and len(partes) == 4:
                try:
                    x = float(partes[1])
                    y = float(partes[2])
                    z = float(partes[3])
                except ValueError:
                    return

                # Calcula magnitud (para mostrar en recuadro)
                magnitud = math.sqrt(x**2 + y**2 + z**2)

                # Guardar medida y obtener danger
                conn = sqlite3.connect("data.db")
                danger = guardar_medidas(LIMITE, raw, conn)
                conn.close()

                # Mostrar alerta solo una vez si DANGER
                if danger == 1:
                    self.arduino.write(b"4\n")
                    if not self.peligro_mostrado:
                        self.peligro_mostrado = True
                        msg = QMessageBox()
                        msg.setWindowTitle("PELIGRO DE MEDICIÓN")
                        msg.setIcon(QMessageBox.Icon.Critical)
                        msg.setText("⚠️ Se detectó una medición peligrosa.\nRevisa el sensor.")
                        msg.exec()
                else:
                    self.peligro_mostrado = False

                # Actualizar recuadro de magnitud
                self.actualizar_recuadro_magnitud(magnitud, danger)

                # Si es incidente, refrescar tabla de incidentes (añadir nuevos)
                if danger == 1:
                    self.refresh_incidents_table()

                # Actualizar buffers gráfico
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

                self.line_x.setData(self.time, self.data_x)
                self.line_y.setData(self.time, self.data_y)
                self.line_z.setData(self.time, self.data_z)

                return  # ya procesamos la línea

            # =======================================
            # Código 5 → Cambiar contraseña
            # =======================================
            if codigo == "5" and len(partes) == 3:
                usuario = partes[1]
                nueva_contraseña = partes[2]

                ok = Funciones.cambiar_contraseña(raw)  # raw = "5,usuario,nueva_contraseña"

                if ok:
                    self.arduino.write(b"T\n")
                    msg = QMessageBox()
                    msg.setWindowTitle("Cambio de Contraseña")
                    msg.setIcon(QMessageBox.Icon.Information)
                    msg.setText(f"Contraseña de '{usuario}' actualizada correctamente.")
                    msg.exec()
                    # refrescar tabla de usuarios por si cambió (añadir nuevos/modificaciones)
                    self.refresh_users_table()
                else:
                    self.arduino.write(b"F\n")
                    msg = QMessageBox()
                    msg.setWindowTitle("Cambio de Contraseña")
                    msg.setIcon(QMessageBox.Icon.Warning)
                    msg.setText(f"No se pudo actualizar la contraseña de '{usuario}'.")
                    msg.exec()
                return

    # Función auxiliar para actualizar el recuadro de magnitud
    def actualizar_recuadro_magnitud(self, magnitud, danger):
        # Actualiza el texto
        self.mag_label.setText(f"Magnitud:\n{magnitud:.2f}")

        # Cambia el estilo si es danger
        if danger == 1:
            # Rojo claro de fondo y borde rojo
            self.mag_label.setStyleSheet("""
                QLabel {
                    background-color: #ffe6e6;
                    border: 2px solid #d9534f;
                    border-radius: 8px;
                    font-size: 18px;
                    font-weight: bold;
                    color: #8b0000;
                }
            """)
        else:
            # Estilo normal
            self.mag_label.setStyleSheet("""
                QLabel {
                    background-color: #ffffff;
                    border: 2px solid #8c8c8c;
                    border-radius: 8px;
                    font-size: 18px;
                    font-weight: bold;
                    color: #000000;
                }
            """)

    # =======================================
    # Días almacenados en BD (excluir hoy)
    # =======================================
    def obtener_dias_bd_excluyendo_hoy(self):
        """
        Devuelve lista de días (YYYY-MM-DD) donde hay medidas,
        excluyendo la fecha actual (local).
        """
        try:
            conn = sqlite3.connect("data.db")
            cursor = conn.cursor()
            # Usamos date('now','localtime') para comparar en hora local
            cursor.execute("""
                SELECT DISTINCT DATE(timestamp)
                FROM medidas
                WHERE DATE(timestamp) < DATE('now','localtime')
                ORDER BY DATE(timestamp) DESC
            """)
            dias = [row[0] for row in cursor.fetchall() if row[0] is not None]
        except Exception:
            dias = []
        finally:
            conn.close()

        return dias

    def cambiar_dia_reporte(self, dia):
        if dia != "Seleccionar día":
            self.actualizar_reporte(dia)

    # =======================================
    # Reporte del día
    # =======================================
    def actualizar_reporte(self, dia):
        x_data = Funciones.obtener_dia_x(dia)
        y_data = Funciones.obtener_dia_y(dia)
        z_data = Funciones.obtener_dia_z(dia)

        n = len(x_data)
        time_axis = [i * 5 for i in range(n)]

        self.plot_x_reporte.setData(time_axis, x_data)
        self.plot_y_reporte.setData(time_axis, y_data)
        self.plot_z_reporte.setData(time_axis, z_data)

        self.graph_reporte.setTitle(f"Reporte del Día: {dia}")

    # =======================================
    # TAB USUARIOS: rellenar / refrescar tabla (solo añadir nuevos)
    # =======================================
    def refresh_users_table(self):
        """
        Añade a la tabla de usuarios únicamente los usuarios que no estén ya presentes.
        """
        rows = obtener_usuarios()  # (id, user, password)
        # Obtener set de ids ya en la tabla
        existing_ids = set()
        for r in range(self.table_users.rowCount()):
            item = self.table_users.item(r, 0)
            if item:
                try:
                    existing_ids.add(int(item.text()))
                except ValueError:
                    pass

        # Añadir solo los que no están
        for row in rows:
            try:
                uid = int(row[0])
            except Exception:
                continue
            if uid in existing_ids:
                continue  # ya existe, saltar

            r_idx = self.table_users.rowCount()
            self.table_users.insertRow(r_idx)
            id_item = QTableWidgetItem(str(row[0]))
            user_item = QTableWidgetItem(str(row[1]))
            pass_item = QTableWidgetItem(str(row[2]))
            # poner no editable
            id_item.setFlags(id_item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
            user_item.setFlags(user_item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
            pass_item.setFlags(pass_item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
            self.table_users.setItem(r_idx, 0, id_item)
            self.table_users.setItem(r_idx, 1, user_item)
            self.table_users.setItem(r_idx, 2, pass_item)

    # =======================================
    # TAB INCIDENTES: rellenar / refrescar tabla (solo añadir nuevos)
    # =======================================
    def refresh_incidents_table(self, limit=INCIDENTS_LIMIT):
        """
        Añade a la tabla de incidentes solo las filas nuevas (no duplicar).
        Los incidentes se insertan arriba (fila 0) para que los más recientes queden al tope.
        """
        rows = obtener_todos_incidentes(limit=limit)  # lista de (timestamp, x, y, z, danger)

        # Obtener timestamps existentes para detección rápida de duplicados
        existing_ts = set()
        for r in range(self.table_incidents.rowCount()):
            item = self.table_incidents.item(r, 0)
            if item:
                existing_ts.add(item.text())

        # rows viene ORDER BY timestamp DESC (nuevo primero).
        # Iteramos en orden inverso y hacemos insertRow(0) para mantener orden descendente y añadir nuevos arriba.
        for row in reversed(rows):
            ts = str(row[0])
            if ts in existing_ts:
                continue  # ya está en la tabla
            # insertar en la parte superior
            self.table_incidents.insertRow(0)
            ts_item = QTableWidgetItem(ts)
            x_item = QTableWidgetItem(f"{row[1]:.3f}")
            y_item = QTableWidgetItem(f"{row[2]:.3f}")
            z_item = QTableWidgetItem(f"{row[3]:.3f}")
            danger_item = QTableWidgetItem(str(row[4]))
            # no editable
            for it in (ts_item, x_item, y_item, z_item, danger_item):
                it.setFlags(it.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
            self.table_incidents.setItem(0, 0, ts_item)
            self.table_incidents.setItem(0, 1, x_item)
            self.table_incidents.setItem(0, 2, y_item)
            self.table_incidents.setItem(0, 3, z_item)
            self.table_incidents.setItem(0, 4, danger_item)
            existing_ts.add(ts)  # marcar como existente para siguientes iteraciones

# ------------------------------
# INICIAR APP
# ------------------------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

