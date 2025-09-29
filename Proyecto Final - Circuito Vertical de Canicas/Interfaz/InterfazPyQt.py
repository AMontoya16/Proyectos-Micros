# Tienen que instalar PyQt6 con pip install PyQt6 desde la terminal
import os
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Proyecto MT-7003")
        self.resize(400, 300)

        # Widget central y layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout()
        central_widget.setLayout(self.layout)
        central_widget.setStyleSheet("background-color: #F0EBEB;")

        # Ícono de la ventana
        pathicono = os.path.join(os.path.dirname(__file__), "pixel art of a micro.png")  
        self.setWindowIcon(QIcon(pathicono))

        # Logo institucional
        self.logo_label = QLabel()
        pathlogo = os.path.join(os.path.dirname(__file__), "LogoTEC_.png")
        logo_pixmap = QPixmap(pathlogo)
        self.logo_label.setPixmap(logo_pixmap)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # Texto de presentación
        self.presentacion_label = QLabel(
            "<b>Proyecto MT-7003</b><br>"
            "<b>Microcontroladores y Microprocesadores</b><br><br>"
            "Cristhian Araya Chaves - 2022067611<br>"
            "Jason Brenes Vázquez - <br>"
            "Greivin Esquivel Salazar -  <br>"
            "Andrés Montoya Viales - <br><br>"
            "II Semestre 2025"
        )
        self.presentacion_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.presentacion_label.setStyleSheet("font-size: 30px; font-family: Arial, 'MSI Sans Serif', sans-serif; color: #303030;")
        self.layout.addWidget(self.presentacion_label)

        # Botón de inicio
        self.Boton_inicio = QPushButton("Iniciar")
        self.Boton_inicio.setFixedSize(100, 40)
        self.Boton_inicio.setStyleSheet("""
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
                border: 2px solid #EBE6E6;
            }
        """)
        self.layout.addWidget(self.Boton_inicio, alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom)

        self.nuevo_boton1 = QPushButton("Atrás") 
        self.nuevo_boton2 = QPushButton("Botón 2") 
        self.nuevo_boton1.setFixedSize(120, 45) 
        self.nuevo_boton2.setFixedSize(120, 45) 
        self.nuevo_boton1.setStyleSheet("""
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
        self.nuevo_boton2.setStyleSheet("background-color: #003865; color: white; font-size: 18px; border-radius: 15px;") 
        self.layout.addWidget(self.nuevo_boton1, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop) 
        self.layout.addWidget(self.nuevo_boton2, alignment=Qt.AlignmentFlag.AlignCenter| Qt.AlignmentFlag.AlignLeft) 
        self.nuevo_boton1.hide() 
        self.nuevo_boton2.hide()
        # Conexiones
        self.Boton_inicio.clicked.connect(self.ocultar_componentes)
        self.nuevo_boton1.clicked.connect(self.mostrar_pantalla_inicial)

    def mostrar_pantalla_inicial(self):
        self.logo_label.show()
        self.presentacion_label.show()
        self.Boton_inicio.show()
        self.nuevo_boton1.hide()
        self.nuevo_boton2.hide()
      

    def ocultar_componentes(self):
        self.logo_label.hide()
        self.presentacion_label.hide()
        self.Boton_inicio.hide()
        self.nuevo_boton1.show()
        self.nuevo_boton2.show()
        self.nuevo_boton1.setFocus()

# Ejecutar aplicación
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())
