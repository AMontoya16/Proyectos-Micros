# Tienen que instalar PyQt6 con pip install PyQt6 desde la terminal
import os
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QPixmap,QIcon
from PyQt6.QtCore import Qt, QUrl, QPropertyAnimation, QEasingCurve

class VentanaPrincipal(QMainWindow): # Aquí se genera la ventana principal y el título de la ventana
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Proyecto MT-7003")
        self.resize(400, 300)

        # Este central widget contiene todos los demás widgets
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        central_widget.setStyleSheet("background-color: #F0EBEB;")
        pathicono= os.path.join(os.path.dirname(__file__), "pixel art of a micro.png")  
        self.setWindowIcon(QIcon(pathicono))  # No esta leyendo la imagen, descargar y probar en la misma carpeta

        # Logo de la institución en la esquina superior izquierda
        logo_label = QLabel()
        pathlogo = os.path.join(os.path.dirname(__file__), "LogoTEC_.png")  # No esta leyendo la imagen, descargar y probar en la misma carpeta
        logo_pixmap = QPixmap(pathlogo)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        layout.addWidget(logo_label, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)


        # Texto de presentación con integrantes y proyecto
        # Se presenta en QLabel con formato HTML para negritas y saltos de línea
        presentacion_label = QLabel(
            "<b>Proyecto MT-7003</b><br>"
            "<b>Microcontroladores y Microprocesadores</b><br><br>"
            "Cristhian Araya Chaves - 2022067611<br>"
            "Jason Brenes Vázquez - <br>"
            "Greivin Esquivel Salazar -  <br>"
            "Andrés Montoya Viales - <br><br>"
            "II Semestre 2025"
        )
        layout.addWidget(presentacion_label)
        presentacion_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        presentacion_label.setStyleSheet("font-size: 30px; font-family: Arial, 'MSI Sans Serif', sans-serif; color: #303030;")

        # Botón de inicio centrado en la parte inferior
        Boton_inicio = QPushButton("Iniciar")
        layout.addWidget(Boton_inicio, alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom)
        Boton_inicio.setFixedSize(100, 40)
        #QPush Button y QPushButton:hover cambian las características del botón al pasar el mouse sobre él
        Boton_inicio.setStyleSheet("""
            QPushButton {
                background-color: #EBE6E6;
                color: #303030;
                border: 2px solid #003865;
                font-size: 20px;
                border-radius: 15px;
                font-family: MSI Sans Serif;
            }
            QPushButton:hover {
                background-color: #003865;
                color: #EBE6E6;
                border: 2px solid #EF3340;
            }
        """)

# Aquí se inicia la aplicación
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())
