# Tienen que instalar PyQt6 con: pip install PyQt6

import os, sys
import time # Necesario para la pausa en la comunicación
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
permiso = 0 # Linea 332 masomenos
iniciador = 0 # Se encarga de establecer como primer valor de la lista en 2 para evitar errores en la comunicacion
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
        self.resize(1000, 700) # Aumentamos el tamaño para acomodar la nueva matriz

        # ---------------- Comunicación I2C ----------------
        self.I2C_ADDRESS = 0x27
        self.bus = None
        if SMBus: # Solo intenta inicializar si se importó la clase
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
        self.bloqueado_esperando_paso = False # tiempo real: bloqueo después de un paso (esperando *siguiente* señal)
        self.last_pressed_coords = None      # (fila, col) del último botón presionado, o "S", o "Destino"
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

        # Barra de simulación de señal externa (solo tiempo real)
        #barra_senal = QHBoxLayout()
        #barra_senal.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #self.entrada_senal_indicador = QLineEdit()
        #self.entrada_senal_indicador.setPlaceholderText("Valor Indicador (-3..9, 99)...")
        #self.entrada_senal_indicador.setFixedWidth(200)
        #self.entrada_senal_indicador.setStyleSheet("background-color: #FFFFFF; color: #303030; border: 1px solid #D0D0D0;")
        
        #self.entrada_senal_canicas = QLineEdit()
        #self.entrada_senal_canicas.setPlaceholderText("Num Canicas (0-99)...")
        #self.entrada_senal_canicas.setFixedWidth(150)
        #self.entrada_senal_canicas.setStyleSheet("background-color: #FFFFFF; color: #303030; border: 1px solid #D0D0D0;")
        
        self.comenzar = QPushButton("Comenzar")
        self.comenzar.setFixedSize(180, 40)
        self.comenzar.setStyleSheet(self.seleccionable())
        self.comenzar.clicked.connect(self.accion_comenzar)
        self.layout.addWidget(self.comenzar, alignment=Qt.AlignmentFlag.AlignCenter)
        
        #barra_senal.addWidget(self.entrada_senal_indicador)
        #barra_senal.addWidget(self.entrada_senal_canicas)
        #barra_senal.addWidget(self.boton_aplicar_data)
        #self.layout.addLayout(barra_senal)
        
        # Ocultar campos y botón de simulación
       # self.entrada_senal_indicador.hide()
        #self.entrada_senal_canicas.hide()
        self.comenzar.hide()


        # Cuadro de Número de Canicas
        texto_inicial = f"Número de canicas: {self.num_canicas}" #Esta linea indica el texto al usuario
        
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

        contenedor_matriz = QHBoxLayout() # Contenedor horizontal para la matriz de botones y la de indicadores
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
                # El botón solo registra la selección, ya no ilumina el indicador inmediatamente
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

        #self.boton_comenzar = QPushButton("Comenzar")
        #self.boton_comenzar.setFixedHeight(50)
        #self.boton_comenzar.setStyleSheet(self.seleccionable())
        #self.boton_comenzar.clicked.connect(self.accion_destino)
        #self.malla.addWidget(self.boton_comenzar, 0, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignLeft)

        #self.layout_vertical_principal.addWidget(self.boton_comenzar)
        #self.layout_vertical_principal.addLayout(self.malla)
        #self.setLayout(self.layout_vertical_principal)
        contenedor_matriz.addWidget(self.grid_widget, alignment=Qt.AlignmentFlag.AlignLeft)
        # ---------------- FIN Matriz de Botones ----------------


        # ---------------- Matriz de Indicadores Luminosos ----------------
        self.indicadores_widget = QWidget()
        self.indicadores_widget.setFixedWidth(250)
        self.malla_indicadores = QGridLayout(self.indicadores_widget)
        self.malla_indicadores.setHorizontalSpacing(5)
        self.malla_indicadores.setVerticalSpacing(5)
        self.malla_indicadores.setContentsMargins(10, 10, 10, 10)
        self.indicadores_widget.setStyleSheet("background-color: #EBE6E6; border: 1px solid #003865; border-radius: 10px;")

        # CORRECCIÓN DE MAPEO: El STM32 usa -1, -2, -3 para los Sensores, y 1-9 para los nodos.
        # Ajustamos el diccionario de indicadores para reflejar el valor real del STM32.
        indicadores_mapa_stm32 = {
            -1: "S1", -2: "S2", -3: "S3",
            1: "1", 2: "2", 3: "3",
            4: "4", 5: "5", 6: "6",
            7: "7", 8: "8", 9: "9",
            99: "Destino"
        }
        
        self.indicador_labels = {}
        
        # Mapear los valores del STM32 a etiquetas visuales en el Grid
        grid_pos = [
            (-1, 0, 0), (-2, 0, 1), (-3, 0, 2), # S1, S2, S3
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

        # Etiqueta "Destino" (valor 99)
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
        #self.boton_aplicar_data.clicked.connect(self.simular_actualizacion_externa)

    # ---------------- Función para enviar/recibir datos I2C ----------------
    def enviar_trayectoria_i2c(self):
        """
        Envía la trayectoria completa (Activacion_servo + Posicion_pasos) al STM32
        en modo 'trayectoria' (maestro push).
        """
        global Posicion_pasos
        global Activacion_servo
        global iniciador

        # Bloquea temporalmente el bucle si no hay bus I2C real
        if self.bus is None:
            print("⚠️ Ejecución I2C abortada: Bus no inicializado. Comunicación SIMULADA.")
            return

        # 1. Preparar la trayectoria a enviar
        # La trayectoria son los nodos (Posicion_pasos) precedidos por el servo a activar (Activacion_servo)
        datos_a_enviar = self.trayectoria

        if self.modo == "trayectoria":
            datos_a_enviar.insert(0, iniciador)
            datos_a_enviar.insert(-1, iniciador)

            print(f"INICIANDO ENVÍO DE TRAYECTORIA I2C: {datos_a_enviar}")

            try:
                global permiso
                global posicion

                # Iterar sobre la trayectoria completa (incluyendo Activacion_servo)
                for dato in datos_a_enviar:
                    byte_a_enviar = dato

                    # Enviar valor al STM32
                    self.bus.write_byte(self.I2C_ADDRESS, byte_a_enviar)
                    t0 = time.time()
                    print(f"Enviado al STM32: {dato} (Byte: {byte_a_enviar})")

                    # Intentar leer un byte de respuesta (ej. confirmación)
                    while GPIO.input(17) != 1:
                        # print("Procesando")
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

                    # Pausa para dar tiempo al bus I2C y al microcontrolador
                    time.sleep(0.5)
                time.sleep(30) 
            except OSError as e:
                print(f"⚠️ Error fatal de comunicación I2C: {e}")

            print("\n🛑 Ejecución de Trayectoria I2C finalizada.")
                            
    def enviar_trayectoria_i2c_TR(self, texto):
    
            # 1. Chequeo de Bus
            if self.bus is None:
                print("⚠️ Ejecución I2C abortada: Bus no inicializado. Comunicación SIMULADA.")
                return # Salida 1: Si no hay bus, salimos.

            # Mapear el texto a byte
            global Posicion
            datos_a_enviar = self._mapear_a_byte(texto)
            
            print (datos_a_enviar)
            
            # *Nota: Si quieres que S1, S2, S3 mapeen a algo diferente a 0, cambia esto:*

            print(f"INICIANDO ENVÍO DE PASO I2C: {datos_a_enviar}")

            try:
                # A. ENVÍO Y POLLING
                self.bus.write_byte(self.I2C_ADDRESS, datos_a_enviar)
                t0 = time.time()
                print(f"Enviado al STM32: {datos_a_enviar}")

                # Polling/Espera de la bandera GPIO 17 (HANDSHAKING)
                while GPIO.input(17) != 1:
                    time.sleep(0.005)
                    
                #respuesta = None
                
                # B. LECTURA DE RESPUESTA
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
                    
                    
                    
                    # 2. DECIDIR EL MENSAJE Y EL LOG
                    log_msgs = {0: "Mueve a derecha", 1: "Mueve a izquierda", 2: "Mueve a abajo", 3: "Mueve a destino"}
                    msg = log_msgs.get(respuesta, f"Respuesta desconocida: {respuesta}")
                    print(f"✅ STM32 confirmó. {msg}. Tiempo: {tiempo_res:.4f}s. Respuesta: {respuesta}")
                    self.actualizar_estado_indicador(Posicion)
                    QApplication.processEvents()

                except OSError as e:
                    # Si falla la lectura, imprimimos el error, pero continuamos para desbloquear,
                    # ASUMIENDO que el STM32 sí terminó el paso.
                    print(f"⚠️ Error al leer respuesta: {e}. Se asume que el paso terminó.")
                    
                
                # --- CÓDIGO DE DESBLOQUEO Y COMPROBACIÓN (Movido al final del bloque try) ---
                self.simular_actualizacion_externa() # ⬅️ Ejecutamos la función
                print(self.bloqueado_esperando_paso) # Imprimimos el estado para debugging

                
            except OSError as e:
                # Esto captura errores de bus.write_byte() o la lectura principal
                print(f"⚠️ Error fatal de comunicación I2C: {e}")
                    
            print("\n🛑 Ejecución de Trayectoria I2C finalizada.")

    # ---------------- Mapeo de Valores ----------------
    def _mapear_a_byte(self, texto):
        """Convierte el texto del botón al valor numérico (byte) esperado por el microcontrolador."""
        # Mapeo según el código de C++: S1=-1, S2=-2, S3=-3, Nodos=1-9, Destino=99
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
        
        return 0 # Valor por defecto/error

    # ---------------- Estilos y Utilidades (Sin cambios) ----------------
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
        # Estilo para indicador apagado (gris)
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
        # Estilo para indicador encendido (verde)
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
        """
        Método para ser llamado por la lógica externa (microcontrolador)
        para encender/apagar el indicador (LED).
        Valores válidos: -1, -2, -3, 1-9, 99.
        """
        print (valor)
        
        # Reiniciar todos los indicadores a gris
        for label in self.indicador_labels.values():
            label.setStyleSheet(self.estilo_indicador_gris())

        try:
            valor = int(valor)
        except (ValueError, TypeError):
            print(f"Error: Valor de señal '{valor}' no es un entero válido para el indicador. Indicadores apagados.")
            return

        # Aplicar estilo verde al indicador correspondiente
        if valor in self.indicador_labels:
            self.indicador_labels[valor].setStyleSheet(self.estilo_indicador_verde())
            print(f"DEBUG: Indicador activado para el valor: {valor}")
       # else:
         #   print(f"DEBUG: Valor de señal '{valor}' fuera de rango (-3 a 9, o 99).")

    def simular_actualizacion_externa(self):
        """
        Función de demostración que simula la recepción de datos del microcontrolador.
        Llama a actualizar_estado_indicador() y actualizar_estado_canicas().
        """
        # 1. Actualizar Indicador y Canicas (Esto simula el feedback del micro)
       # valor_indicador_str = self.entrada_senal_indicador.text().strip()
        #valor_canicas_str = self.entrada_senal_canicas.text().strip()
        #try:
         #   if valor_indicador_str:
          #      self.actualizar_estado_indicador(int(valor_indicador_str))
          #  else:
           #     self.actualizar_estado_indicador(0) # Valor 0 apaga todos los indicadores
       # except ValueError:
        #    print("ERROR: El valor introducido para el indicador no es un entero válido.")

        #try:
         #   if valor_canicas_str:
          #      self.actualizar_estado_canicas(int(valor_canicas_str))
           # else:
            #    self.actualizar_estado_canicas(None) # Pone 'Sin dato'
        #except ValueError:
         #   print("ERROR: El valor introducido para el contador de canicas no es un entero válido.")

        # 2. Lógica de Desbloqueo en modo Tiempo Real
        if self.modo == "tiempo_real":
            
            # 2.2 Desbloqueo por Paso (después de una selección del usuario)
            if self.bloqueado_esperando_paso:
                self.bloqueado_esperando_paso = False
                
                # 1. BLOQUEO TOTAL PRIMERO: Asegura que el estado base es BLOCKEADO y DIFUMINADO (solo S/Números)
                self.aplicar_bloqueo_total(True) 
                
                if self.last_pressed_coords == "S" and self.s_seleccionada is not None:
                    # Desbloquear el primer número en la columna S seleccionada (e.g., 1, 4, o 7)
                    columna = self.s_seleccionada
                    btn_1 = self.botones[1][columna] # Fila 1 (el '1', '2' o '3')
                    btn_1.setEnabled(True)
                    btn_1.setStyleSheet(self.seleccionable())
                    print(f"INFO: Desbloqueada primera celda numérica en columna S{columna + 1}.")
                    
                elif isinstance(self.last_pressed_coords, tuple) and self.last_pressed_coords[0] in (1, 2, 3):
                    # Desbloquear solo los adyacentes al último número presionado
                    fila, col = self.last_pressed_coords
                    ady = self.calcular_adyacentes(fila, col)
                    # La función habilitar_solo desactiva todos los números 1-9 y luego activa los de 'ady'
                    self.habilitar_solo(ady) 
                    
                    # Habilitar Destino si se está en la última fila
                    if fila == 3:
                        self.boton_destino.setEnabled(True)
                        self.boton_destino.setStyleSheet(self.seleccionable())

                    print(f"INFO: Desbloqueados adyacentes a {self.botones[fila][col].text()} y Destino (si aplica).")
                
                # Caso Destino: Si el último paso fue "Destino", no hay más pasos, se mantiene bloqueado.
                elif self.last_pressed_coords == "Destino":
                    print("INFO: Matriz bloqueada. El último paso fue Destino. Presione Reiniciar.")
            QApplication.processEvents()
            print("INFO: GUI forzada a redibujar después del desbloqueo.")


    # ---------------- Pantallas (Sin cambios) ----------------
    def mostrar_pantalla_inicial(self):
        """Muestra la pantalla de selección de modo y oculta la matriz."""
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
        #self.entrada_senal_indicador.hide()
        #self.entrada_senal_canicas.hide()
        self.comenzar.hide()
        
        self.reset_estado_logico() # <-- CORRECCIÓN: Llamar al reseteo lógico

    def configurar_estado_inicial_matriz(self):
        """Establece el estado inicial: S1-S3 y Destino activos, números 1-9 inactivos."""
        global comenzar
        if comenzar == 0 and self.modo == "tiempo_real":
                self.aplicar_bloqueo_total
        else:
                self.aplicar_bloqueo_total(False) # 1. Desbloquea todo (estilo 'seleccionable')
                
                # 2. Bloquear solo las filas de números (1, 2, 3)
                for f in (1, 2, 3):
                    for c in (0, 1, 2):
                        btn = self.botones[f][c]
                        btn.setEnabled(False)
                        btn.setStyleSheet(self.difuminado())
                
                # 3. Garantizar que la fila de sensores S1-S3 (Fila 0) está activa (redundante, pero explícito)
                for c in (0, 1, 2):
                    self.botones[0][c].setEnabled(True)
                    self.botones[0][c].setStyleSheet(self.seleccionable())

                # 4. Garantizar que Destino está activo
                self.boton_destino.setEnabled(False)
                self.boton_destino.setStyleSheet(self.difuminado())


    def cambiar_modo(self, modo):
        self.modo = modo
        # Ocultar pantalla inicial
        self.logo_label.hide()
        self.presentacion_label.hide()
        self.Boton_inicio.hide()
        self.Boton_TR.hide()
        
        # Mostrar controles de modo
        self.boton_atras.show()
        self.canicas_container.show()
        self.indicadores_widget.show()
        self.grid_widget.show()
        self.boton_destino.show()
        self.boton_reiniciar.show()
        
        # Configuración específica por modo
        if modo == "tiempo_real":
            self.aplicar_bloqueo_total(True)
            # Mostrar campos de simulación en Tiempo Real
            #self.entrada_senal_indicador.show()
            #self.entrada_senal_canicas.show()
            #self.boton_aplicar_data.show()
            self.comenzar.show()
            self.boton_listo.hide()
            
            self.esperando_senal = False 
            self.bloqueado_esperando_paso = False
            
            print("INFO: Modo Tiempo Real iniciado. Se espera selección de S1, S2, o S3.")
        else: # modo trayectoria
            # Ocultar campos de simulación en Trayectoria
            #self.entrada_senal_indicador.hide()
           # self.entrada_senal_canicas.hide()
            self.comenzar.hide()
            self.boton_listo.show()
           # self.boton_comenzar.hide()
            self.esperando_senal = False
            self.bloqueado_esperando_paso = False
            print("INFO: Modo Trayectoria iniciado. Se espera selección de S1, S2, o S3.")

        # Establecer estado inicial de la matriz (S1-S3 y Destino habilitados, 1-9 deshabilitados)
        self.configurar_estado_inicial_matriz()
        self.reset_estado_logico() # Reiniciar estado lógico
        
        self.actualizar_estado_canicas(None)
        self.actualizar_estado_indicador(0)


    # ---------------- Lógica de selección (Registro de Path) ----------------
    def boton_presionado(self, fila, columna, texto):
        
        # El microcontrolador espera un byte numérico para el dato
        dato_byte = self._mapear_a_byte(texto) 

        if self.modo == "tiempo_real":
            self.actualizar_estado_indicador(Posicion)
            QApplication.processEvents()
            # Si estamos esperando la señal externa (después de S o Número), ignorar el click.
            if self.bloqueado_esperando_paso:
                print("INFO: En modo Tiempo Real, la matriz está bloqueada. Presione 'Aplicar Data Externa' para desbloquear el siguiente paso.")
                return

            # 1. Registrar el comando
            # Nota: En TR, solo guardamos el último byte para saber qué desbloquear después, no la lista completa
            if dato_byte != 0:
                self.trayectoria = [dato_byte]
            #self.enviar_trayectoria_i2c_TR(str(self.trayectoria))
            #print(f"INFO: Modo Tiempo Real - Comando de paso registrado: {dato_byte}")
            
            # 2. Lógica de estado y bloqueo
            if fila == 0: # S1..S3 selection
                
                self.s_seleccionada = columna
                self.last_pressed_coords = "S"
                
            elif fila in (1, 2, 3): # Number selection
                self.last_pressed_coords = (fila, columna)
                # Bloquear filas superiores, permanentemente hasta reiniciar (Regla de bloqueo por fila)
                self.bloquear_filas_hasta(fila - 1) 

            # 3. Aplicar bloqueo total (S/Números), esperar señal externa
            self.aplicar_bloqueo_total(True)
            self.bloqueado_esperando_paso = True
            self.enviar_trayectoria_i2c_TR(texto)
            
        else: # Modo Trayectoria (Lógica de adyacentes y bloqueo por fila)

            boton = self.botones[fila][columna]
            if not boton.isEnabled():
                return

            # Selección de S1..S3 (Fila 0)
            if fila == 0:
                self.s_seleccionada = columna
                self.registrar_seleccion(dato_byte) # Guarda el byte
                
                # BLOQUEO DE FILA COMPLETA S1-S3 TRAS SELECCIÓN
                for j, b in enumerate(self.botones[0]):
                    b.setEnabled(False)
                    b.setStyleSheet(self.difuminado())
                    
                # Desbloquear solo el primer botón numérico en la columna seleccionada
                self.habilitar_solo([(1, columna)])
                
                # Habilitar destino
                self.boton_destino.setEnabled(True)
                self.boton_destino.setStyleSheet(self.seleccionable())


            # Selección de números (Filas 1, 2, 3)
            elif fila in (1, 2, 3):
                self.registrar_seleccion(dato_byte) # Guarda el byte
                # Lógica de adyacentes
                ady = self.calcular_adyacentes(fila, columna)
                self.habilitar_solo(ady)
                self.bloquear_filas_hasta(fila - 1)
                
                # Si llega a la última fila, también debe habilitar destino
                if fila == 3:
                    self.boton_destino.setEnabled(True)
                    self.boton_destino.setStyleSheet(self.seleccionable())
                else:
                    self.boton_destino.setEnabled(False)
                    self.boton_destino.setStyleSheet(self.difuminado())
                
            #print (self.trayectoria[-1])

            # Mensaje de registro (Muestra la lista de bytes)
            print(f"Selección registrada. Trayectoria actual (BYTES): {self.trayectoria}")

            self.boton_listo.setEnabled(False)
            self.boton_listo.setStyleSheet(self.difuminado())
            
            if self.modo == "tiempo_real" and len(self.trayectoria) > 1:
                self.trayectoria = [self.trayectoria[-1]]

        

    def bloquear_TR(self):
            print("DEBUG: La función bloquear_TR ha sido llamada.")
            self.aplicar_bloqueo_total(True)




    def calcular_adyacentes(self, fila, col):
        """Calcula coordenadas de celdas adyacentes (abajo, izquierda, derecha) en la matriz de 4x3."""
        coords = []
        # Izquierda
        
        if col - 1 >= 0:
            coords.append((fila, col - 1))
        # Derecha
        if col + 1 <= 2:
            coords.append((fila, col + 1))
        # Abajo (si no es la última fila)
        if fila + 1 <= 3:
            coords.append((fila + 1, col))
        return coords


    def habilitar_solo(self, coords_habilitadas):
        """Bloquea todos los números (1-9) y solo habilita los que están en coords_habilitadas."""
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
        
        """Bloquea filas de la 0 hasta la fila_limite (inclusive)."""
        for f in range(0, fila_limite + 1):
            for c in (0, 1, 2):
                b = self.botones[f][c]
                b.setEnabled(False)
                b.setStyleSheet(self.difuminado())

    def aplicar_bloqueo_total(self, bloquear):
        """Bloquea/Desbloquea todos los botones (S1-S3, 1-9, Destino) y aplica estilo difuminado."""
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
        self.ventana_opciones = VentanaOpcionesEjecutar(parent = self)
        self.ventana_opciones.ejecutar_seleccionado.connect(self.manejar_ejecucion_final)
        self.ventana_opciones.exec()
        self.ventana_opciones = None


    def accion_comenzar (self):
        global comenzar
        comenzar = 1
        self.comenzar.setEnabled(False)
        self.comenzar.setStyleSheet(self.difuminado())
        self.configurar_estado_inicial_matriz()
        #time.sleep(5)
        self.enviar_trayectoria_i2c_TR("0")
            

    # ---------------- Destino y Reiniciar ----------------

    def accion_destino(self):
          
        """
        Finaliza la selección de trayectoria o registra la acción en tiempo real.
        """
        # 1. Registrar el byte 99 ("Destino") en la trayectoria
        self.registrar_seleccion(99)
        
        # 2. Bloquear toda la matriz
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
            else :
                self.aplicar_bloqueo_total(True)
                print("INFO: Límite de 3 listas alcanzado. Matriz bloqueada.")
            # Asignar los valores a las variables globales para la comunicación I2C
            # El primer elemento es el byte del sensor S (-1, -2, o -3)
            #Activacion_servo = self.trayectoria [0] 
            # El resto son los pasos (nodos) incluyendo el Destino (99)
            #Posicion_pasos = self.trayectoria[1:]
            self.boton_listo.setEnabled(True)
            self.boton_listo.setStyleSheet(self.seleccionable())
            
            
            # TRAYECTORIA COMPLETA REGISTRADA
            print(f"INFO: Trayectoria completa registrada: {Posicion_pasos}.")
            print(f"INFO: Servo a activar: {Activacion_servo}.")
            
            # 3. LLAMAR A LA FUNCIÓN DE COMUNICACIÓN AQUÍ
            #self.enviar_trayectoria_i2c() # <-- LLAMADA DE ACCIÓN
            
        else: # Modo Tiempo Real
            # Lógica de tiempo real: el paso 'Destino' fue enviado, ahora espera la señal externa
            #self.bus.write_byte(self.I2C_ADDRESS, byte_a_enviar)
            self.enviar_trayectoria_i2c_TR("Destino")
            #print (f"Se envio {byte_a_enviar}")
            self.bloqueado_esperando_paso = True
            print("INFO: Modo Tiempo Real - Comando DESTINO registrado. Matriz bloqueada, esperando señal externa.")
        

    #def listo_activar(self):
     #   if self.trayectoria [-1] == str(99):
      #          self.boton_listo.setEnabled(True)
       #         self.boton_listo.setStyleSheet(self.seleccionable())
       # else:
        #    self.boton_listo.setEnabled(False)
           # self.boton_listo.setStyleSheet(self.difuminado())

    def lista_master(self):
        global TrayectoriaA
        global TrayectoriaB
        global TrayectoriaC
        global Orden_trayectorias
        self.aplicar_bloqueo_total(True)
        self.boton_listo.setEnabled(False)
        self.boton_listo.setStyleSheet(self.difuminado())

        #self.trayectoria_master = []
        for orden in Orden_trayectorias:
            if orden == "A" and len(TrayectoriaA) > 0:
                self.trayectoria=TrayectoriaA
                print(TrayectoriaA)
                self.enviar_trayectoria_i2c()
            elif orden == "B" and len(TrayectoriaB) > 0:
                self.trayectoria=TrayectoriaB
                print (TrayectoriaB)
                self.enviar_trayectoria_i2c()
            elif orden == "C"and len(TrayectoriaC) > 0:
                self.trayectoria=TrayectoriaC
                print (TrayectoriaC)
                self.enviar_trayectoria_i2c()
            else:
                pass

       # for sublista in self.trayectoria_master:
        #    self.trayectoria.extend(sublista)
       # print (self.trayectoria)
        #self.enviar_trayectoria_i2c()
       # self.trayectoria_master = []
        TrayectoriaA = []
        TrayectoriaB = []
        TrayectoriaC = []
        Orden_trayectorias = []
        global N_listas
        N_listas = 0

        time. sleep (2)
        self.aplicar_bloqueo_total(True)

    def accion_reiniciar(self):
        """Reinicia el estado lógico y la matriz de botones."""
        global comenzar
        
        
        if comenzar == 1:
                self.aplicar_bloqueo_total(True)
                self.comenzar.setStyleSheet(self.seleccionable())
                self.comenzar.setEnabled (True)
                comenzar = 0
        
        else:
            self.configurar_estado_inicial_matriz()
            self.actualizar_estado_indicador(0)
            self.actualizar_estado_canicas(None)
            self.boton_listo.setEnabled(False)
            self.boton_listo.setStyleSheet(self.difuminado())
        self.reset_estado_logico()

        
                
        print("INFO: Sistema reiniciado. Se espera selección de S1, S2, o S3.")

    def reset_estado_logico(self):
        """Reinicia todas las variables de estado lógico a su valor por defecto."""
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


# ---------------- Ejecución ----------------
class VentanaOpcionesEjecutar(QDialog):
    """Ventana emergente que permite seleccionar A, B, o C una vez y ejecutar."""
    
    ejecutar_seleccionado = pyqtSignal(list) 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Opciones de Ejecución")
        self.setFixedSize(300, 200)
        
        self.contador_selecciones = 0
        
        self.seleccion = [] # Almacena los valores de las selecciones A/B/C
        
        layout = QVBoxLayout(self)

        # 1. Contenedor Horizontal para A, B, C
        h_layout = QHBoxLayout()
        
        #  Definir las nuevas etiquetas que queremos usar
        etiquetas_botones = ["A", "B", "C"] 
        
        self.botones_s = {} 
        
        # Iterar sobre las nuevas etiquetas
        for nombre_btn in etiquetas_botones:
            
            # La etiqueta del botón es ahora "A", "B", o "C"
            btn = QPushButton(nombre_btn)
            
            # La función 'seleccionar_sensor' se conecta para recibir "A", "B", o "C"
            btn.clicked.connect(lambda _, n=nombre_btn: self.seleccionar_sensor(n))
            
            btn.setStyleSheet(parent.seleccionable()) 
            btn.setFixedSize(60, 40)
            h_layout.addWidget(btn)
            
            # La referencia en el diccionario usa "A", "B", o "C" como clave
            self.botones_s[nombre_btn] = btn
            
        layout.addLayout(h_layout)
        
        # 2. Botón Ejecutar
        self.boton_ejecutar = QPushButton("Ejecutar")
        self.boton_ejecutar.setStyleSheet(parent.seleccionable())
        self.boton_ejecutar.setFixedSize(200, 40)
        self.boton_ejecutar.clicked.connect(self.ejecutar_y_cerrar)
        self.boton_ejecutar.setEnabled(False)
        self.boton_ejecutar
        layout.addWidget(self.boton_ejecutar, alignment=Qt.AlignmentFlag.AlignCenter)

    def seleccionar_sensor(self, nombre_btn):
        """Maneja el click en A, B, o C, e incrementa el contador."""
        
        # 1. Lógica de selección única (solo si no está en la lista)
        if nombre_btn not in self.seleccion:
            self.seleccion.append(nombre_btn)
            
            # 🌟 INCREMENTAR EL CONTADOR INTERNO
            self.contador_selecciones += 1
            
            # Deshabilitar el botón recién presionado
            self.botones_s[nombre_btn].setEnabled(False)
            self.botones_s[nombre_btn].setStyleSheet(self.parent().difuminado())
            
            print(f"DEBUG: Sensor {nombre_btn} seleccionado. Contador: {self.contador_selecciones}")

        # 2. 🌟 COMPROBAR LA CONDICIÓN DE DESBLOQUEO
        if self.contador_selecciones == 3:
            # Desbloquear el botón "Ejecutar"
            self.boton_ejecutar.setEnabled(True)
            self.boton_ejecutar.setStyleSheet(self.parent().seleccionable())
            print("INFO: Botón 'Ejecutar' habilitado (3 selecciones hechas).")
        else:
            # Si el contador no es 3, nos aseguramos de que siga deshabilitado
            self.boton_ejecutar.setEnabled(False)
            self.boton_ejecutar.setStyleSheet(self.parent().difuminado())

    def ejecutar_y_cerrar(self):
        """Emite la señal y cierra la ventana."""
        # Se envía la lista de strings: ['A', 'C', 'B'], por ejemplo.
        self.ejecutar_seleccionado.emit(self.seleccion)
        self.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())
