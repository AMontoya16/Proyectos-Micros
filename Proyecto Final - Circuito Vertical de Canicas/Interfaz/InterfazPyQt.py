# Tienen que instalar PyQt6 con pip install PyQt6 desde la terminal
import os, sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QGridLayout, QLineEdit, QHBoxLayout
)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Proyecto MT-7003")
        self.resize(600, 500)

        # Estado
        self.modo = None                  # "trayectoria" | "tiempo_real"
        self.trayectoria = []             # lista de selección
        self.s_seleccionada = None        # columna del S elegido (0..2)
        self.esperando_senal = False      # tiempo real: bloqueo inicial

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
        self.Boton_inicio.setFixedSize(120, 45)
        self.Boton_inicio.setStyleSheet(self.seleccionable())
        botones_layout.addWidget(self.Boton_inicio)
        self.Boton_TR = QPushButton("Tiempo real")
        self.Boton_TR.setFixedSize(120, 45)
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

        # Barra de señal (solo tiempo real)
        barra_senal = QHBoxLayout()
        barra_senal.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.entrada_senal = QLineEdit()
        self.entrada_senal.setPlaceholderText("Valor de señal externa...")
        self.entrada_senal.setFixedWidth(200)
        self.entrada_senal.setStyleSheet("background-color: #FFFFFF; color: #303030;")
        self.boton_senal = QPushButton("Aplicar señal")
        self.boton_senal.setFixedSize(130, 40)
        self.boton_senal.setStyleSheet(self.seleccionable())
        barra_senal.addWidget(self.entrada_senal)
        barra_senal.addWidget(self.boton_senal)
        self.layout.addLayout(barra_senal)
        self.entrada_senal.hide()
        self.boton_senal.hide()

        # Contenedor para matriz más arriba (alineado arriba-izquierda con margen)
        self.matriz_layout = QVBoxLayout()
        self.matriz_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.addLayout(self.matriz_layout)

        contenedor_matriz = QHBoxLayout()
        contenedor_matriz.setAlignment(Qt.AlignmentFlag.AlignLeft)
        contenedor_matriz.setContentsMargins(20, 0, 0, 0)  # margen izquierdo
        self.matriz_layout.addLayout(contenedor_matriz)

        # Matriz y controles
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

        contenedor_matriz.addWidget(self.grid_widget, alignment=Qt.AlignmentFlag.AlignLeft)

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
        self.boton_senal.clicked.connect(self.recibir_senal_externa)

    # ---------------- Estilos ----------------
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

    # ---------------- Pantallas ----------------
    def mostrar_pantalla_inicial(self):
        self.grid_widget.hide()
        self.boton_destino.hide()
        self.boton_reiniciar.hide()
        self.logo_label.show()
        self.presentacion_label.show()
        self.Boton_inicio.show()
        self.Boton_TR.show()
        self.boton_atras.hide()
        self.entrada_senal.hide()
        self.boton_senal.hide()
        self.reset_estado()

    def cambiar_modo(self, modo):
        self.modo = modo
        self.logo_label.hide()
        self.presentacion_label.hide()
        self.Boton_inicio.hide()
        self.Boton_TR.hide()
        self.boton_atras.show()

        if modo == "tiempo_real":
            self.entrada_senal.show()
            self.boton_senal.show()
            self.esperando_senal = True
        else:
            self.entrada_senal.hide()
            self.boton_senal.hide()
            self.esperando_senal = False

        self.grid_widget.show()
        self.boton_destino.show()
        self.boton_reiniciar.show()
        self.reset_estado()
        if self.modo == "tiempo_real":
            self.aplicar_bloqueo_total(True)

    # ---------------- Lógica de selección ----------------
    def boton_presionado(self, fila, columna, texto):
        if self.modo == "tiempo_real" and self.esperando_senal:
            return
        boton = self.botones[fila][columna]
        if not boton.isEnabled():
            return

        # Selección de S1..S3
        if fila == 0:
            self.s_seleccionada = columna
            for j, b in enumerate(self.botones[0]):
                if j != columna:
                    b.setEnabled(False)
                    b.setStyleSheet(self.difuminado())
            # Habilitar solo el número debajo del S elegido
            for f in (1, 2, 3):
                for c in (0, 1, 2):
                    btn = self.botones[f][c]
                    if f == 1 and c == columna:
                        btn.setEnabled(True)
                        btn.setStyleSheet(self.seleccionable())
                    else:
                        btn.setEnabled(False)
                        btn.setStyleSheet(self.difuminado())
            self.registrar_seleccion(texto)

        # Selección de números
        elif fila in (1, 2, 3):
            self.registrar_seleccion(texto)
            # Adyacentes: izquierda, derecha, abajo
            ady = self.calcular_adyacentes(fila, columna)
            self.habilitar_solo(ady)
            # Bloquear filas anteriores (incluye S)
            self.bloquear_filas_hasta(fila - 1)

        # Mensaje en trayectoria
        if self.modo == "trayectoria":
            print(f"Se ha seleccionado {texto}")

        # Tiempo real: mantener un único valor
        if self.modo == "tiempo_real" and len(self.trayectoria) > 1:
            self.trayectoria = [self.trayectoria[-1]]

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

    def registrar_seleccion(self, texto):
        self.trayectoria.append(texto)

    # ---------------- Señal externa (tiempo real) ----------------
    def recibir_senal_externa(self):
        valor = self.entrada_senal.text().strip()
        if valor:
            self.esperando_senal = False
            # Tras señal, permitir elegir S1..S3 y bloquear números
            for j, b in enumerate(self.botones[0]):
                b.setEnabled(True)
                b.setStyleSheet(self.seleccionable())
            for f in (1, 2, 3):
                for c in (0, 1, 2):
                    btn = self.botones[f][c]
                    btn.setEnabled(False)
                    btn.setStyleSheet(self.difuminado())
            print(f"Señal externa recibida: {valor}")

    # ---------------- Destino y Reiniciar ----------------
    def accion_destino(self):
        if self.modo == "trayectoria":
            print("Resultado trayectoria:", " -> ".join(self.trayectoria))
        else:
            print("Tiempo real - último valor:", self.trayectoria[-1] if self.trayectoria else "N/A")

    def accion_reiniciar(self):
        self.reset_estado()
        if self.modo == "tiempo_real":
            self.esperando_senal = True
            self.aplicar_bloqueo_total(True)

    def aplicar_bloqueo_total(self, bloquear=True):
        for fila in self.botones:
            for b in fila:
                b.setEnabled(not bloquear)
                b.setStyleSheet(self.difuminado() if bloquear else self.seleccionable())

    def reset_estado(self):
        self.trayectoria.clear()
        self.s_seleccionada = None
        for f in range(len(self.botones)):
            for c in range(len(self.botones[f])):
                b = self.botones[f][c]
                b.setEnabled(True)
                b.setStyleSheet(self.seleccionable())

# Esto ejecuta la aplicación
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())


