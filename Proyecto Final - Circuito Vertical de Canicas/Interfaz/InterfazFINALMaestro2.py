# Tienen que instalar PyQt6 con: pip install PyQt6

import os, sys
import time  # Necesario para la pausa en la comunicación
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QGridLayout, QLineEdit, QHBoxLayout, QFrame, QDialog, QMessageBox
)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)

# Intentar importar smbus/smbus2. Si falla, el bus será None y la comunicación se simulará.
try:
    # Usamos smbus, que es el que tenías originalmente
    from smbus import SMBus
except ImportError:
    # Intento con smbus2 si smbus no está disponible
    try:
        from smbus2 import SMBus
        print("AVISO: Usando smbus2 en lugar de smbus.")
    except ImportError:
        SMBus = None
        print("AVISO: smbus/smbus2 no encontrado. La comunicación I2C será simulada.")

# ---------------- Variables globales de envio ----------------

# NOTA: Estas variables serán actualizadas por accion_destino,
# pero se accederán dentro de la clase usando 'global'.
N_listas = 0
Posicion = 0
Posicion_pasos = []
Activacion_servo = 0
permiso = 0  # Linea 332 masomenos
iniciador = 0  # Se encarga de establecer como primer valor de la lista en 2 para evitar errores en la comunicacion
comenzar = 0
Orden_trayectorias = []
TrayectoriaA = []
TrayectoriaB = []
TrayectoriaC = []


class VentanaPrincipal(QMainWindow):

    def manejar_ejecucion_final(self, seleccion_sensores):
        print(seleccion_sensores)
        global Orden_trayectorias
        self.aplicar_bloqueo_total(True)
        self.boton_listo.setEnabled(False)
        self.boton_listo.setStyleSheet(self.difuminado())
        Orden_trayectorias = seleccion_sensores
        self.lista_master()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Proyecto MT-7003 - Visualizador")
        self.resize(1000, 700)  # Aumentamos el tamaño para acomodar la nueva matriz

        # ---------------- Comunicación I2C ----------------
        self.I2C_ADDRESS = 0x27
        self.bus = None
        if SMBus:  # Solo intenta inicializar si se importó la clase
            try:
                self.bus = SMBus(1)
                print("INFO: Bus I2C 1 inicializado correctamente.")
            except FileNotFoundError:
                print("AVISO: No se puede abrir /dev/i2c-1. ¿Estás en una Raspberry Pi con I2C habilitado?")
            except Exception as e:
                print(f"ERROR: Fallo al inicializar I2C: {e}")
        else:
            print("AVISO: La comunicación I2C será simulada (SMBus no disponible).")
        # ---------------- FIN Comunicación I2C ----------------

        # Estado
        self.modo = None                     # "trayectoria" | "tiempo_real"
        self.trayectoria = []                # lista de selección (ALMACENA VALORES NUMÉRICOS/BYTES)
        self.s_seleccionada = None           # columna del S elegido (0..2)

        # --- ESTADOS PARA TIEMPO REAL ---
        self.esperando_senal = False
        self.bloqueado_esperando_paso = False  # tiempo real: bloqueo después de un paso (esperando *siguiente* señal)
        self.last_pressed_coords = None        # (fila, col) del último botón presionado, o "S", o "Destino"
        # ----------------------------------------

        self.num_canicas = None              # Estado para el número de canicas

        # Widget central y layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout()
        central_widget.setLayout(self.layout)
        central_widget.setStyleSheet("background-color: #F0EBEB;")

        # Ícono de la ventana
        pathicono = os.path.join(os.path.dirname(__file__), "pixel art of a micro.png")
        if os.path.exists(pathicono):
            self.setWindowIcon(QIcon(pathicono))

        # Logo
        self.logo_label = QLabel()
        pathlogo = os.path.join(os.path.dirname(__file__), "LogoTEC_.png")
        if os.path.exists(pathlogo):
            self.logo_label.setPixmap(QPixmap(pathlogo))
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # Presentación
        self.presentacion_label = QLabel(
            "<b>Proyecto MT-7003</b><br>"
            "<b>Microcontroladores y Microprocesadores</b><br><br>"
            "Cristhian Araya Chaves - 2022067611<br>"
            "Jason Brenes Vázquez - 2023057374<br>"
            "Greivin Esquivel Salazar<br>"
            "Andrés Montoya Viales - 2023063390 <br><br>"
            "II Semestre 2025"
        )
        self.presentacion_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.presentacion_label.setStyleSheet("font-size: 30px; font-family: Arial, 'MSI Sans Serif'; color: #303030;")
        self.layout.addWidget(self.presentacion_label)

        # Botones principales juntos (horizontal)
        botones_layout = QHBoxLayout()
        botones_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.Boton_inicio = QPushButton("Trayectoria")
        self.Boton_inicio.setFixedSize(150, 45)
        self.Boton_inicio.setStyleSheet(self.seleccionable())
        botones_layout.addWidget(self.Boton_inicio)
        self.Boton_TR = QPushButton("Tiempo real")
        self.Boton_TR.setFixedSize(150, 45)
        self.Boton_TR.setStyleSheet(self.seleccionable())
        botones_layout.addWidget(self.Boton_TR)
        self.layout.addLayout(botones_layout)
        self.Boton_TR.clicked.connect(self.bloquear_TR)

        # Botón Atrás (rojo)
        self.boton_atras = QPushButton("Atrás")
        self.boton_atras.setFixedSize(120, 45)
        self.boton_atras.setStyleSheet("""
            QPushButton {
                background-color: #EF3340;
                color: #EBE6E6;
                border: 2px solid #EF3340;
                font-size: 20px;
                border-radius: 15px;
                font-family: MSI Sans Serif;
            }
            QPushButton:hover {
                background-color: #EBE6E6;
                color: #303030;
                border: 2px solid #EF3340;
            }
        """)
        self.layout.addWidget(self.boton_atras, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        self.boton_atras.hide()

        self.comenzar = QPushButton("Comenzar")
        self.comenzar.setFixedSize(180, 40)
        self.comenzar.setStyleSheet(self.seleccionable())
        self.comenzar.clicked.connect(self.accion_comenzar)
        self.layout.addWidget(self.comenzar, alignment=Qt.AlignmentFlag.AlignCenter)
        self.comenzar.hide()

        # Cuadro de Número de Canicas
        texto_inicial = f"Número de canicas: {self.num_canicas}"

        self.canicas_container = QFrame()
        self.canicas_container.setFrameShape(QFrame.Shape.Box)
        self.canicas_container.setFrameShadow(QFrame.Shadow.Raised)
        self.canicas_container.setStyleSheet("background-color: #FFFFFF; border: 2px solid #003865; border-radius: 10px; padding: 5px;")
        canicas_layout = QHBoxLayout(self.canicas_container)
        self.label_canicas = QLabel(texto_inicial, self)
        self.label_canicas.setStyleSheet("font-size: 20px; font-weight: bold; color: #303030;")
        canicas_layout.addWidget(self.label_canicas)
        self.canicas_container.hide()
        self.layout.addWidget(self.canicas_container, alignment=Qt.AlignmentFlag.AlignCenter)

        # Contenedor para matriz de botones Y matriz de indicadores
        self.matriz_layout = QVBoxLayout()
        self.matriz_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.addLayout(self.matriz_layout)

        contenedor_matriz = QHBoxLayout()  # Contenedor horizontal para la matriz de botones y la de indicadores
        contenedor_matriz.setAlignment(Qt.AlignmentFlag.AlignCenter)
        contenedor_matriz.setContentsMargins(20, 0, 20, 0)
        self.matriz_layout.addLayout(contenedor_matriz)

        # ---------------- Matriz de Botones ----------------
        self.grid_widget = QWidget()
        self.malla = QGridLayout(self.grid_widget)
        self.malla.setHorizontalSpacing(5)
        self.malla.setVerticalSpacing(5)

        self.botones = []
        etiquetas = [
            ["S1", "S2", "S3"],
            ["1", "2", "3"],
            ["4", "5", "6"],
            ["7", "8", "9"]
        ]
        for fila, row in enumerate(etiquetas):
            fila_botones = []
            for col, texto in enumerate(row):
                boton = QPushButton(texto)
                boton.setFixedSize(80, 80)
                boton.setStyleSheet(self.seleccionable())
                boton.clicked.connect(lambda _, f=fila, c=col, t=texto: self.boton_presionado(f, c, t))
                self.malla.addWidget(boton, fila, col)
                fila_botones.append(boton)
            self.botones.append(fila_botones)

        # Botón Destino bajo la matriz (colspan 3 y centrado)
        self.boton_destino = QPushButton("Destino")
        self.boton_destino.setFixedHeight(50)
        self.boton_destino.setStyleSheet(self.seleccionable())
        self.boton_destino.clicked.connect(self.accion_destino)
        self.malla.addWidget(self.boton_destino, 4, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)

        self.boton_listo = QPushButton("Listo")
        self.boton_listo.setFixedHeight(50)
        self.boton_listo.setStyleSheet(self.difuminado())
        self.boton_listo.setEnabled(False)
        self.boton_listo.clicked.connect(self.accion_listo)
        self.malla.addWidget(self.boton_listo, 4, 2, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)

        self.layout_vertical_principal = QVBoxLayout()

        contenedor_matriz.addWidget(self.grid_widget, alignment=Qt.AlignmentFlag.AlignLeft)

        # ---------------- Matriz de Indicadores Luminosos ----------------
        self.indicadores_widget = QWidget()
        self.indicadores_widget.setFixedWidth(250)
        self.malla_indicadores = QGridLayout(self.indicadores_widget)
        self.malla_indicadores.setHorizontalSpacing(5)
        self.malla_indicadores.setVerticalSpacing(5)
        self.malla_indicadores.setContentsMargins(10, 10, 10, 10)
        self.indicadores_widget.setStyleSheet("background-color: #EBE6E6; border: 1px solid #003865; border-radius: 10px;")

        indicadores_mapa_stm32 = {
            -1: "S1", -2: "S2", -3: "S3",
            1: "1", 2: "2", 3: "3",
            4: "4", 5: "5", 6: "6",
            7: "7", 8: "8", 9: "9",
            99: "Destino"
        }

        self.indicador_labels = {}

        grid_pos = [
            (-1, 0, 0), (-2, 0, 1), (-3, 0, 2),
            (1, 1, 0), (2, 1, 1), (3, 1, 2),
            (4, 2, 0), (5, 2, 1), (6, 2, 2),
            (7, 3, 0), (8, 3, 1), (9, 3, 2)
        ]

        for valor_stm32, f, c in grid_pos:
            texto = indicadores_mapa_stm32[valor_stm32]
            label = QLabel(texto)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setFixedSize(60, 60)
            label.setStyleSheet(self.estilo_indicador_gris())
            self.malla_indicadores.addWidget(label, f, c)
            self.indicador_labels[valor_stm32] = label

        self.label_destino_ind = QLabel("Destino")
        self.label_destino_ind.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_destino_ind.setFixedHeight(40)
        self.label_destino_ind.setStyleSheet(self.estilo_indicador_gris())
        self.malla_indicadores.addWidget(self.label_destino_ind, 4, 0, 1, 3)
        self.indicador_labels[99] = self.label_destino_ind

        contenedor_matriz.addWidget(self.indicadores_widget, alignment=Qt.AlignmentFlag.AlignRight)
        self.indicadores_widget.hide()
        # ---------------- FIN Matriz de Indicadores ----------------

        # Botón Reiniciar alineado a la izquierda, justo debajo
        self.boton_reiniciar = QPushButton("Reiniciar")
        self.boton_reiniciar.setFixedHeight(45)
        self.boton_reiniciar.setStyleSheet(self.seleccionable())
        self.boton_reiniciar.clicked.connect(self.accion_reiniciar)
        self.matriz_layout.addWidget(self.boton_reiniciar, alignment=Qt.AlignmentFlag.AlignLeft)

        # Ocultar matriz y controles hasta entrar a modo
        self.grid_widget.hide()
        self.boton_destino.hide()
        self.boton_reiniciar.hide()

        # Conexiones
        self.Boton_inicio.clicked.connect(lambda: self.cambiar_modo("trayectoria"))
        self.Boton_TR.clicked.connect(lambda: self.cambiar_modo("tiempo_real"))
        self.boton_atras.clicked.connect(self.mostrar_pantalla_inicial)
    # ---------------- Función para enviar/recibir datos I2C ----------------
    def enviar_trayectoria_i2c(self):
        global Posicion_pasos
        global Activacion_servo
        global iniciador
        self.leer_canicas_estatico()
        if self.bus is None:
            print("⚠️ Ejecución I2C abortada: Bus no inicializado. Comunicación SIMULADA.")
            return

        datos_a_enviar = self.trayectoria

        if self.modo == "trayectoria":
            datos_a_enviar.insert(0, iniciador)
            datos_a_enviar.insert(-1, iniciador)

            print(f"INICIANDO ENVÍO DE TRAYECTORIA I2C: {datos_a_enviar}")

            try:
                global permiso
                global posicion

                for dato in datos_a_enviar:
                    byte_a_enviar = dato

                    self.bus.write_byte(self.I2C_ADDRESS, byte_a_enviar)
                    t0 = time.time()
                    print(f"Enviado al STM32: {dato} (Byte: {byte_a_enviar})")

                    while GPIO.input(17) != 1:
                        time.sleep(0.005)

                        try:
                            respuesta = self.bus.read_byte(self.I2C_ADDRESS)
                            if respuesta == 255:
                                respuesta = -1
                            elif respuesta == 254:
                                respuesta = -2
                            elif respuesta == 253:
                                respuesta = -3
                            if dato == 0:
                                respuesta = 0

                            t1 = time.time()
                            tiempo_res = (t1 - t0)
                            self.actualizar_estado_indicador(respuesta)
                            QApplication.processEvents()

                            if respuesta == 1:
                                print("✅ STM32 confirmó recepción del dato. Mueve a izquierda")
                                print(respuesta)
                                print(tiempo_res)
                            elif respuesta == 0:
                                print("STM32 confirmó recepción del dato. Mueve a derecha")
                                print(tiempo_res)
                                print(respuesta)
                            elif respuesta == 2:
                                print("STM32 confirmó recepción del dato. Mueve a abajo.")
                                print(tiempo_res)
                                print(respuesta)
                            elif respuesta == 3:
                                print("STM32 confirmó recepción del dato. Mueve a destino.")
                                print(tiempo_res)
                                print(respuesta)
                            else:
                                print(f"⚠️ Respuesta desconocida: {respuesta}")

                        except OSError as e:
                            print(f"⚠️ Error al leer respuesta: {e}")

                    time.sleep(0.5)
                time.sleep(30)
                self.leer_canicas_estatico()
            except OSError as e:
                print(f"⚠️ Error fatal de comunicación I2C: {e}")

            print("\n🛑 Ejecución de Trayectoria I2C finalizada.")

    def enviar_trayectoria_i2c_TR(self, texto):
        if self.bus is None:
            print("⚠️ Ejecución I2C abortada: Bus no inicializado. Comunicación SIMULADA.")
            return

        global Posicion
        datos_a_enviar = self._mapear_a_byte(texto)
        self.leer_canicas_estatico()
        print(datos_a_enviar)
        print(f"INICIANDO ENVÍO DE PASO I2C: {datos_a_enviar}")

        try:
            self.bus.write_byte(self.I2C_ADDRESS, datos_a_enviar)
            t0 = time.time()
            print(f"Enviado al STM32: {datos_a_enviar}")

            while GPIO.input(17) != 1:
                time.sleep(0.005)

            try:
                respuesta = self.bus.read_byte(self.I2C_ADDRESS)
                if respuesta == 255:
                    respuesta = -1
                elif respuesta == 254:
                    respuesta = -2
                elif respuesta == 253:
                    respuesta = -3
                Posicion = respuesta
                t1 = time.time()
                tiempo_res = (t1 - t0)

                log_msgs = {0: "Mueve a derecha", 1: "Mueve a izquierda", 2: "Mueve a abajo", 3: "Mueve a destino"}
                msg = log_msgs.get(respuesta, f"Respuesta desconocida: {respuesta}")
                print(f"✅ STM32 confirmó. {msg}. Tiempo: {tiempo_res:.4f}s. Respuesta: {respuesta}")
                self.leer_canicas_estatico()
                self.actualizar_estado_indicador(Posicion)
                QApplication.processEvents()

            except OSError as e:
                print(f"⚠️ Error al leer respuesta: {e}. Se asume que el paso terminó.")

            self.simular_actualizacion_externa()
            print(self.bloqueado_esperando_paso)

        except OSError as e:
            print(f"⚠️ Error fatal de comunicación I2C: {e}")

        print("\n🛑 Ejecución de Trayectoria I2C finalizada.")

    def _mapear_a_byte(self, texto):
        if texto == "S1": return -1
        if texto == "S2": return -2
        if texto == "S3": return -3

        try:
            num = int(texto)
            if 1 <= num <= 9:
                return num
        except ValueError:
            pass

        if texto == "Destino": return 99

        return 0

    def seleccionable(self):
        return """
            QPushButton {
                background-color: #EBE6E6;
                color: #303030;
                border: 2px solid #003865;
                font-size: 18px;
                border-radius: 10px;
                font-family: MSI Sans Serif;
            }
            QPushButton:hover {
                background-color: #003865;
                color: #EBE6E6;
                border: 2px solid #EBE6E6;
            }"""

    def difuminado(self):
        return """
            QPushButton {
                background-color: #C0C0C0;
                color: #707070;
                border: 2px solid #A0A0A0;
                font-size: 18px;
                border-radius: 10px;
                font-family: MSI Sans Serif;
            }"""

    def estilo_indicador_gris(self):
        return """
            QLabel {
                background-color: #C0C0C0;
                color: #303030;
                border: 1px solid #707070;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }"""

    def estilo_indicador_verde(self):
        return """
            QLabel {
                background-color: #4CAF50;
                color: #FFFFFF;
                border: 1px solid #388E3C;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }"""

    # ---------------- Lógica de Actualización Externa (API) (Sin cambios) ----------------
    # >>>>>>>>>>>>>>>>> FUNCIÓN HX711 INTEGRADA AQUÍ <<<<<<<<<<<<<<<<<
    def leer_canicas_estatico(self):
        """
        Lee la celda de carga HX711, calcula la cantidad de canicas
        y actualiza la GUI con:
            self.actualizar_estado_canicas(self.canicas)
        """
        if not hasattr(self, "hx_inicializado"):
            from hx711 import HX711
            DT_PIN = 6
            SCK_PIN = 5

            self.factor_calibracion = 212.0
            self.peso_por_canica = 5
            self.hist = 1
            self.muestras = 10
            
            self.canicas = 0
            
            self.peso_referencia = 0

            self.hx = HX711(dout_pin=DT_PIN, pd_sck_pin=SCK_PIN)

            self.hx.reset()
            self.hx.zero()

            self.offset = self.hx.get_data_mean(self.muestras)
            self.hx_inicializado = True

        lectura = self.hx.get_data_mean(self.muestras)
        if lectura is None:
            return

        peso_actual = (lectura - self.offset) / self.factor_calibracion
        diferencia = peso_actual - self.peso_referencia

        if diferencia > (self.peso_por_canica - self.hist):
            nuevas = round(diferencia / self.peso_por_canica)
            self.canicas += nuevas
            self.peso_referencia += nuevas * self.peso_por_canica

        if diferencia < -(self.peso_por_canica - self.hist):
            retiradas = round(abs(diferencia) / self.peso_por_canica)
            self.canicas -= retiradas
            if self.canicas < 0:
                self.canicas = 0
            self.peso_referencia -= retiradas * self.peso_por_canica
            
        self.actualizar_estado_canicas(self.canicas)
        print(self.canicas)

    def actualizar_estado_canicas(self, entero):
        """
        Método para ser llamado por la lógica externa (microcontrolador)
        para actualizar el contador de canicas.
        """
        self.num_canicas = entero
        if entero is not None and isinstance(entero, int):
            self.label_canicas.setText(f"Número de canicas: {entero}")
        else:
            self.label_canicas.setText("Número de canicas: Sin dato")
        print(f"DEBUG: Canicas actualizadas a: {self.num_canicas}")

    def actualizar_estado_indicador(self, valor):
        print(valor)

        for label in self.indicador_labels.values():
            label.setStyleSheet(self.estilo_indicador_gris())

        try:
            valor = int(valor)
        except (ValueError, TypeError):
            print(f"Error: Valor de señal '{valor}' no es un entero válido para el indicador. Indicadores apagados.")
            return

        if valor in self.indicador_labels:
            self.indicador_labels[valor].setStyleSheet(self.estilo_indicador_verde())
            print(f"DEBUG: Indicador activado para el valor: {valor}")

    def simular_actualizacion_externa(self):
        if self.modo == "tiempo_real":
            if self.bloqueado_esperando_paso:
                self.bloqueado_esperando_paso = False
                self.aplicar_bloqueo_total(True)

                if self.last_pressed_coords == "S" and self.s_seleccionada is not None:
                    columna = self.s_seleccionada
                    btn_1 = self.botones[1][columna]
                    btn_1.setEnabled(True)
                    btn_1.setStyleSheet(self.seleccionable())
                    print(f"INFO: Desbloqueada primera celda numérica en columna S{columna + 1}.")
                elif isinstance(self.last_pressed_coords, tuple) and self.last_pressed_coords[0] in (1, 2, 3):
                    fila, col = self.last_pressed_coords
                    ady = self.calcular_adyacentes(fila, col)
                    self.habilitar_solo(ady)

                    if fila == 3:
                        self.boton_destino.setEnabled(True)
                        self.boton_destino.setStyleSheet(self.seleccionable())

                    print(f"INFO: Desbloqueados adyacentes a {self.botones[fila][col].text()} y Destino (si aplica).")
                elif self.last_pressed_coords == "Destino":
                    print("INFO: Matriz bloqueada. El último paso fue Destino. Presione Reiniciar.")
            QApplication.processEvents()
            print("INFO: GUI forzada a redibujar después del desbloqueo.")
    def mostrar_pantalla_inicial(self):
        self.grid_widget.hide()
        self.boton_destino.hide()
        self.boton_reiniciar.hide()
        self.indicadores_widget.hide()
        self.canicas_container.hide()
        self.logo_label.show()
        self.presentacion_label.show()
        self.Boton_inicio.show()
        self.Boton_TR.show()
        self.boton_atras.hide()
        self.comenzar.hide()
        self.reset_estado_logico()

    def configurar_estado_inicial_matriz(self):
        global comenzar
        if comenzar == 0 and self.modo == "tiempo_real":
            self.aplicar_bloqueo_total
        else:
            self.aplicar_bloqueo_total(False)

            for f in (1, 2, 3):
                for c in (0, 1, 2):
                    btn = self.botones[f][c]
                    btn.setEnabled(False)
                    btn.setStyleSheet(self.difuminado())

            for c in (0, 1, 2):
                self.botones[0][c].setEnabled(True)
                self.botones[0][c].setStyleSheet(self.seleccionable())

            self.boton_destino.setEnabled(False)
            self.boton_destino.setStyleSheet(self.difuminado())

    def cambiar_modo(self, modo):
        self.modo = modo
        self.logo_label.hide()
        self.presentacion_label.hide()
        self.Boton_inicio.hide()
        self.Boton_TR.hide()

        self.boton_atras.show()
        self.canicas_container.show()
        self.indicadores_widget.show()
        self.grid_widget.show()
        self.boton_destino.show()
        self.boton_reiniciar.show()

        if modo == "tiempo_real":
            self.aplicar_bloqueo_total(True)
            self.comenzar.show()
            self.boton_listo.hide()

            self.esperando_senal = False
            self.bloqueado_esperando_paso = False

            print("INFO: Modo Tiempo Real iniciado. Se espera selección de S1, S2, o S3.")
        else:
            self.comenzar.hide()
            self.boton_listo.show()
            self.esperando_senal = False
            self.bloqueado_esperando_paso = False
            print("INFO: Modo Trayectoria iniciado. Se espera selección de S1, S2, o S3.")

        self.configurar_estado_inicial_matriz()
        self.reset_estado_logico()

       # self.actualizar_estado_canicas(None)
        self.actualizar_estado_indicador(0)

    def boton_presionado(self, fila, columna, texto):
        dato_byte = self._mapear_a_byte(texto)

        if self.modo == "tiempo_real":
            self.actualizar_estado_indicador(Posicion)
            QApplication.processEvents()
            if self.bloqueado_esperando_paso:
                print("INFO: En modo Tiempo Real, la matriz está bloqueada. Presione 'Aplicar Data Externa' para desbloquear el siguiente paso.")
                return

            if dato_byte != 0:
                self.trayectoria = [dato_byte]

            if fila == 0:
                self.s_seleccionada = columna
                self.last_pressed_coords = "S"
            elif fila in (1, 2, 3):
                self.last_pressed_coords = (fila, columna)
                self.bloquear_filas_hasta(fila - 1)

            self.aplicar_bloqueo_total(True)
            self.bloqueado_esperando_paso = True
            self.enviar_trayectoria_i2c_TR(texto)

        else:
            boton = self.botones[fila][columna]
            if not boton.isEnabled():
                return

            if fila == 0:
                self.s_seleccionada = columna
                self.registrar_seleccion(dato_byte)

                for j, b in enumerate(self.botones[0]):
                    b.setEnabled(False)
                    b.setStyleSheet(self.difuminado())

                self.habilitar_solo([(1, columna)])

                self.boton_destino.setEnabled(True)
                self.boton_destino.setStyleSheet(self.seleccionable())

            elif fila in (1, 2, 3):
                self.registrar_seleccion(dato_byte)
                ady = self.calcular_adyacentes(fila, columna)
                self.habilitar_solo(ady)
                self.bloquear_filas_hasta(fila - 1)

                if fila == 3:
                    self.boton_destino.setEnabled(True)
                    self.boton_destino.setStyleSheet(self.seleccionable())
                else:
                    self.boton_destino.setEnabled(False)
                    self.boton_destino.setStyleSheet(self.difuminado())

            print(f"Selección registrada. Trayectoria actual (BYTES): {self.trayectoria}")

            self.boton_listo.setEnabled(False)
            self.boton_listo.setStyleSheet(self.difuminado())

            if self.modo == "tiempo_real" and len(self.trayectoria) > 1:
                self.trayectoria = [self.trayectoria[-1]]

    def bloquear_TR(self):
        print("DEBUG: La función bloquear_TR ha sido llamada.")
        self.aplicar_bloqueo_total(True)

    def calcular_adyacentes(self, fila, col):
        coords = []
        if col - 1 >= 0:
            coords.append((fila, col - 1))
        if col + 1 <= 2:
            coords.append((fila, col + 1))
        if fila + 1 <= 3:
            coords.append((fila + 1, col))
        return coords

    def habilitar_solo(self, coords_habilitadas):
        coords = set(coords_habilitadas)

        for f in (1, 2, 3):
            for c in (0, 1, 2):
                b = self.botones[f][c]
                if (f, c) in coords:
                    b.setEnabled(True)
                    b.setStyleSheet(self.seleccionable())
                else:
                    b.setEnabled(False)
                    b.setStyleSheet(self.difuminado())

    def bloquear_filas_hasta(self, fila_limite):
        for f in range(0, fila_limite + 1):
            for c in (0, 1, 2):
                b = self.botones[f][c]
                b.setEnabled(False)
                b.setStyleSheet(self.difuminado())

    def aplicar_bloqueo_total(self, bloquear):
        for f in range(len(self.botones)):
            for c in range(len(self.botones[f])):
                b = self.botones[f][c]
                b.setEnabled(not bloquear)
                if bloquear:
                    b.setStyleSheet(self.difuminado())
                else:
                    b.setStyleSheet(self.seleccionable())

        self.boton_destino.setEnabled(not bloquear)
        if bloquear:
            self.boton_destino.setStyleSheet(self.difuminado())
        else:
            self.boton_destino.setStyleSheet(self.seleccionable())

    def registrar_seleccion(self, dato_byte):
        global N_listas
        global TrayectoriaA
        global TrayectoriaB
        global TrayectoriaC
        if N_listas == 0:
            TrayectoriaA.append(dato_byte)
        elif N_listas == 1:
            TrayectoriaB.append(dato_byte)
        elif N_listas == 2:
            TrayectoriaC.append(dato_byte)
        print(TrayectoriaA)
        print(TrayectoriaB)
        print(TrayectoriaC)

    def accion_listo(self):
        self.ventana_opciones = VentanaOpcionesEjecutar(parent=self)
        self.ventana_opciones.ejecutar_seleccionado.connect(self.manejar_ejecucion_final)
        self.ventana_opciones.exec()
        self.ventana_opciones = None

    def accion_comenzar(self):
        global comenzar
        comenzar = 1
        self.comenzar.setEnabled(False)
        self.comenzar.setStyleSheet(self.difuminado())
        self.configurar_estado_inicial_matriz()
        self.enviar_trayectoria_i2c_TR("0")

    def accion_destino(self):
        self.registrar_seleccion(99)
        self.last_pressed_coords = "Destino"

        if self.modo == "trayectoria":
            global Posicion_pasos
            global Activacion_servo
            global N_listas
            self.boton_listo.setEnabled(True)
            self.boton_listo.setStyleSheet(self.seleccionable())

            if N_listas < 2:
                N_listas += 1
                self.aplicar_bloqueo_total(False)
                self.configurar_estado_inicial_matriz()
            else:
                self.aplicar_bloqueo_total(True)
                print("INFO: Límite de 3 listas alcanzado. Matriz bloqueada.")

            self.boton_listo.setEnabled(True)
            self.boton_listo.setStyleSheet(self.seleccionable())

            print(f"INFO: Trayectoria completa registrada: {Posicion_pasos}.")
            print(f"INFO: Servo a activar: {Activacion_servo}.")

        else:
            self.enviar_trayectoria_i2c_TR("Destino")
            self.bloqueado_esperando_paso = True
            print("INFO: Modo Tiempo Real - Comando DESTINO registrado. Matriz bloqueada, esperando señal externa.")

    def lista_master(self):
        global TrayectoriaA
        global TrayectoriaB
        global TrayectoriaC
        global Orden_trayectorias
        self.aplicar_bloqueo_total(True)
        self.boton_listo.setEnabled(False)
        self.boton_listo.setStyleSheet(self.difuminado())

        for orden in Orden_trayectorias:
            if orden == "A" and len(TrayectoriaA) > 0:
                self.trayectoria = TrayectoriaA
                print(TrayectoriaA)
                self.enviar_trayectoria_i2c()
            elif orden == "B" and len(TrayectoriaB) > 0:
                self.trayectoria = TrayectoriaB
                print(TrayectoriaB)
                self.enviar_trayectoria_i2c()
            elif orden == "C" and len(TrayectoriaC) > 0:
                self.trayectoria = TrayectoriaC
                print(TrayectoriaC)
                self.enviar_trayectoria_i2c()
            else:
                pass

        TrayectoriaA = []
        TrayectoriaB = []
        TrayectoriaC = []
        Orden_trayectorias = []
        global N_listas
        N_listas = 0

        time.sleep(2)
        self.aplicar_bloqueo_total(True)

    def accion_reiniciar(self):
        self.leer_canicas_estatico()
        global comenzar
    
        if comenzar == 1:
            self.aplicar_bloqueo_total(True)
            self.comenzar.setStyleSheet(self.seleccionable())
            self.comenzar.setEnabled(True)
            comenzar = 0
        else:
            self.configurar_estado_inicial_matriz()
            self.actualizar_estado_indicador(0)
           # self.actualizar_estado_canicas(None)
            self.boton_listo.setEnabled(False)
            self.boton_listo.setStyleSheet(self.difuminado())
        self.reset_estado_logico()

        print("INFO: Sistema reiniciado. Se espera selección de S1, S2, o S3.")

    def reset_estado_logico(self):
        global Posicion_pasos
        global Activacion_servo
        global N_listas
        global comenzar
        N_listas = 0
        comenzar = 0
        global iniciador
        iniciador = 0
        global permiso
        permiso = 0
        global Posicion
        Posicion_pasos = []
        Activacion_servo = 0
        self.trayectoria = []
        Posicion = 0
        self.s_seleccionada = None
        self.num_canicas = None
        self.esperando_senal = False
        self.bloqueado_esperando_paso = False
        self.last_pressed_coords = None
        global Orden_trayectorias
        Orden_trayectorias = []


class VentanaOpcionesEjecutar(QDialog):
    ejecutar_seleccionado = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Opciones de Ejecución")
        self.setFixedSize(300, 200)

        self.contador_selecciones = 0
        self.seleccion = []

        layout = QVBoxLayout(self)

        h_layout = QHBoxLayout()
        etiquetas_botones = ["A", "B", "C"]

        self.botones_s = {}

        for nombre_btn in etiquetas_botones:
            btn = QPushButton(nombre_btn)
            btn.clicked.connect(lambda _, n=nombre_btn: self.seleccionar_sensor(n))
            btn.setStyleSheet(parent.seleccionable())
            btn.setFixedSize(60, 40)
            h_layout.addWidget(btn)
            self.botones_s[nombre_btn] = btn

        layout.addLayout(h_layout)

        self.boton_ejecutar = QPushButton("Ejecutar")
        self.boton_ejecutar.setStyleSheet(parent.seleccionable())
        self.boton_ejecutar.setFixedSize(200, 40)
        self.boton_ejecutar.clicked.connect(self.ejecutar_y_cerrar)
        self.boton_ejecutar.setEnabled(False)
        layout.addWidget(self.boton_ejecutar, alignment=Qt.AlignmentFlag.AlignCenter)

    def seleccionar_sensor(self, nombre_btn):
        if nombre_btn not in self.seleccion:
            self.seleccion.append(nombre_btn)
            self.contador_selecciones += 1

            self.botones_s[nombre_btn].setEnabled(False)
            self.botones_s[nombre_btn].setStyleSheet(self.parent().difuminado())

            print(f"DEBUG: Sensor {nombre_btn} seleccionado. Contador: {self.contador_selecciones}")

        if self.contador_selecciones == 3:
            self.boton_ejecutar.setEnabled(True)
            self.boton_ejecutar.setStyleSheet(self.parent().seleccionable())
            print("INFO: Botón 'Ejecutar' habilitado (3 selecciones hechas).")
        else:
            self.boton_ejecutar.setEnabled(False)
            self.boton_ejecutar.setStyleSheet(self.parent().difuminado())

    def ejecutar_y_cerrar(self):
        self.ejecutar_seleccionado.emit(self.seleccion)
        self.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())
    

