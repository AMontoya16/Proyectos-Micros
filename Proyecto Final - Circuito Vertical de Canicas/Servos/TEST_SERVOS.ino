#include <Servo.h>

// Declaramos la variable para controlar el servo
Servo servoMotor1;
Servo servoMotor2;
Servo servoMotor3;

// Pines de entrada digital

void setup() {
  // Inicializamos el monitor serie (opcional)
  // Iniciamos el servo en el pin 9
  servoMotor1.attach(9);
  servoMotor2.attach(10);
  servoMotor3.attach(11);
}

void loop() {
  // Leemos el estado de las entradas digitales
  // Lógica de control
  // se gira 90 grados en direccion de las manecillas del reloj par dejar caer las canicas

    servoMotor1.write(90);   // Posición 90°
    delay(2000);
 
    servoMotor2.write(90);  // Posición 90°
    delay(2000);

    servoMotor3.write(90);  // Posición 90°
    delay(2000); 

    servoMotor1.write(180);    // Ninguna entrada: posición 180°
    servoMotor2.write(180);     //Posicion de esperar para dejar caer la canica
    servoMotor3.write(180); 
 	delay(2000); // Pequeña pausa para estabilidad
}
