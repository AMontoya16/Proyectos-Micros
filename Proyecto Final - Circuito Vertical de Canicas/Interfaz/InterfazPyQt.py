# Tienen que instalar PyQt6 con: pip install PyQt6
import os, sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QGridLayout, QLineEdit, QHBoxLayout, QFrame
)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QTimer


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Proyecto MT-7003 - Visualizador")
        self.resize(1000, 700) # Aumentamos el tamaño para acomodar la nueva matriz

        # Estado
        self.modo = None                    # "trayectoria" | "tiempo_real"
        self.trayectoria = []               # lista de selección (ALMACENA VALORES NUMÉRICOS/BYTES)
        self.s_seleccionada = None          # columna del S elegido (0..2)
        
        # --- ESTADOS PARA TIEMPO REAL ---
        self.esperando_senal = False        
        self.bloqueado_esperando_paso = False # tiempo real: bloqueo después de un paso (esperando *siguiente* señal)
        self.last_pressed_coords = None     # (fila, col) del último botón presionado, o "S", o "Destino"
        # ----------------------------------------
        
        self.num_canicas = None             # Estado para el número de canicas

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
            "Jason Brenes Vázquez<br>"
            "Greivin Esquivel Salazar<br>"
            "Andrés Montoya Viales<br><br>"
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
        barra_senal = QHBoxLayout()
        barra_senal.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.entrada_senal_indicador = QLineEdit()
        self.entrada_senal_indicador.setPlaceholderText("Valor Indicador (-3..9, 99)...")
        self.entrada_senal_indicador.setFixedWidth(200)
        self.entrada_senal_indicador.setStyleSheet("background-color: #FFFFFF; color: #303030; border: 1px solid #D0D0D0;")
        
        self.entrada_senal_canicas = QLineEdit()
        self.entrada_senal_canicas.setPlaceholderText("Num Canicas (0-99)...")
        self.entrada_senal_canicas.setFixedWidth(150)
        self.entrada_senal_canicas.setStyleSheet("background-color: #FFFFFF; color: #303030; border: 1px solid #D0D0D0;")
        
        self.boton_aplicar_data = QPushButton("Aplicar Data Externa")
        self.boton_aplicar_data.setFixedSize(180, 40)
        self.boton_aplicar_data.setStyleSheet(self.seleccionable())
        
        barra_senal.addWidget(self.entrada_senal_indicador)
        barra_senal.addWidget(self.entrada_senal_canicas)
        barra_senal.addWidget(self.boton_aplicar_data)
        self.layout.addLayout(barra_senal)
        
        # Ocultar campos y botón de simulación
        self.entrada_senal_indicador.hide()
        self.entrada_senal_canicas.hide()
        self.boton_aplicar_data.hide()


        # Cuadro de Número de Canicas
        self.canicas_container = QFrame()
        self.canicas_container.setFrameShape(QFrame.Shape.Box)
        self.canicas_container.setFrameShadow(QFrame.Shadow.Raised)
        self.canicas_container.setStyleSheet("background-color: #FFFFFF; border: 2px solid #003865; border-radius: 10px; padding: 5px;")
        canicas_layout = QHBoxLayout(self.canicas_container)
        self.label_canicas = QLabel("Número de canicas: Sin dato")
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
        self.boton_aplicar_data.clicked.connect(self.simular_actualizacion_externa)

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
    def actualizar_estado_canicas(self, entero=None):
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
        else:
            print(f"DEBUG: Valor de señal '{valor}' fuera de rango (-3 a 9, o 99).")

    def simular_actualizacion_externa(self):
        """
        Función de demostración que simula la recepción de datos del microcontrolador.
        Llama a actualizar_estado_indicador() y actualizar_estado_canicas().
        """
        # 1. Actualizar Indicador y Canicas (Esto simula el feedback del micro)
        valor_indicador_str = self.entrada_senal_indicador.text().strip()
        valor_canicas_str = self.entrada_senal_canicas.text().strip()
        try:
            if valor_indicador_str:
                self.actualizar_estado_indicador(int(valor_indicador_str))
            else:
                self.actualizar_estado_indicador(0) # Valor 0 apaga todos los indicadores
        except ValueError:
            print("ERROR: El valor introducido para el indicador no es un entero válido.")

        try:
            if valor_canicas_str:
                self.actualizar_estado_canicas(int(valor_canicas_str))
            else:
                self.actualizar_estado_canicas(None) # Pone 'Sin dato'
        except ValueError:
            print("ERROR: El valor introducido para el contador de canicas no es un entero válido.")

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
        self.entrada_senal_indicador.hide()
        self.entrada_senal_canicas.hide()
        self.boton_aplicar_data.hide()
        
        self.reset_estado_logico() # <-- CORRECCIÓN: Llamar al reseteo lógico

    def configurar_estado_inicial_matriz(self):
        """Establece el estado inicial: S1-S3 y Destino activos, números 1-9 inactivos."""
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
        self.boton_destino.setEnabled(True)
        self.boton_destino.setStyleSheet(self.seleccionable())


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
            # Mostrar campos de simulación en Tiempo Real
            self.entrada_senal_indicador.show()
            self.entrada_senal_canicas.show()
            self.boton_aplicar_data.show()
            
            self.esperando_senal = False 
            self.bloqueado_esperando_paso = False
            print("INFO: Modo Tiempo Real iniciado. Se espera selección de S1, S2, o S3.")
        else: # modo trayectoria
            # Ocultar campos de simulación en Trayectoria
            self.entrada_senal_indicador.hide()
            self.entrada_senal_canicas.hide()
            self.boton_aplicar_data.hide()
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
            # Si estamos esperando la señal externa (después de S o Número), ignorar el click.
            if self.bloqueado_esperando_paso:
                print("INFO: En modo Tiempo Real, la matriz está bloqueada. Presione 'Aplicar Data Externa' para desbloquear el siguiente paso.")
                return

            # 1. Registrar el comando
            # Nota: En TR, solo guardamos el último byte para saber qué desbloquear después, no la lista completa
            if dato_byte != 0:
                self.trayectoria = [dato_byte]
            print(f"INFO: Modo Tiempo Real - Comando de paso registrado: {dato_byte}")
            
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

            # Mensaje de registro (Muestra la lista de bytes)
            print(f"Selección registrada. Trayectoria actual (BYTES): {self.trayectoria}")
            
            if self.modo == "tiempo_real" and len(self.trayectoria) > 1:
                self.trayectoria = [self.trayectoria[-1]]


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

    def registrar_seleccion(self, dato_byte):
        """Guarda el valor numérico (byte) en la lista de trayectoria."""
        self.trayectoria.append(dato_byte)

    # ---------------- Destino y Reiniciar ----------------
    def accion_destino(self):
        """
        Finaliza la selección de trayectoria o registra la acción en tiempo real.
        """
        dato_byte = self._mapear_a_byte("Destino") # 99
        self.registrar_seleccion(dato_byte)
        
        # 1. BLOQUEAR TODA LA MATRIZ DE SENSORES/NÚMEROS
        self.aplicar_bloqueo_total(True)
        
        # 2. BLOQUEAR EL BOTÓN DE DESTINO
        self.boton_destino.setEnabled(False) 
        self.boton_destino.setStyleSheet(self.difuminado())
        
        if self.modo == "trayectoria":
            # TRAYECTORIA COMPLETA REGISTRADA
            print(f"INFO: Trayectoria completa registrada: {self.trayectoria}. Esperando ejecución simulada.")
            
        else: # Modo Tiempo Real
            # COMANDO DESTINO ÚNICO REGISTRADO
            print(f"INFO: Tiempo real - comando Destino (99) registrado. Matriz bloqueada hasta Reiniciar.")
            self.last_pressed_coords = "Destino"
            self.bloqueado_esperando_paso = False 

    def accion_reiniciar(self):
        """Reinicia el estado lógico y visual a la configuración inicial de cada modo."""

        self.reset_estado_logico()
        
        self.actualizar_estado_indicador(0) # Apagar todos los indicadores
        self.actualizar_estado_canicas(None) # Reiniciar canicas a 'Sin dato'
        
        # Volver al estado inicial: S1-S3 y Destino activos, números 1-9 inactivos
        self.configurar_estado_inicial_matriz()

    def aplicar_bloqueo_total(self, bloquear=True):
        """Bloquea o desbloquea todos los botones de la matriz de sensores/números (S1-S3 y 1-9)."""
        # Botones S1-S3 y 1-9
        for fila in self.botones:
            for b in fila:
                b.setEnabled(not bloquear)
                b.setStyleSheet(self.difuminado() if bloquear else self.seleccionable())
        
        # El botón Destino (99) NO está incluido en este bloqueo total.

    def reset_estado_logico(self):
        """Reinicia solo las variables de estado lógico."""
        self.trayectoria.clear() # Lista vacía de bytes
        self.s_seleccionada = None
        self.last_pressed_coords = None 
        self.esperando_senal = False
        self.bloqueado_esperando_paso = False

# Esto ejecuta la aplicación
if __name__ == '__main__':
 
    app = QApplication(sys.argv)
    
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())




