#include <Servo.h>

// Declaramos la variable para controlar el servo
Servo servoMotor1;
Servo servoMotor2;
Servo servoMotor3;

// Pines de entrada digital
const int pinEntrada1 = 2;
const int pinEntrada2 = 3;
const int pinEntrada3 = 4; 

void setup() {
  // Inicializamos el monitor serie (opcional)
  Serial.begin(9600);

  // Configuramos los pines de entrada
  pinMode(pinEntrada1, INPUT);
  pinMode(pinEntrada2, INPUT);
  pinMode(pinEntrada3, INPUT);

  // Iniciamos el servo en el pin 9
  servoMotor1.attach(9);
  servoMotor2.attach(10);
  servoMotor3.attach(11);
}

void loop() {
  // Leemos el estado de las entradas digitales
  int estado1 = digitalRead(pinEntrada1);
  int estado2 = digitalRead(pinEntrada2);
  int estado3 = digitalRead(pinEntrada3); 
  // Lógica de control
  // se gira 90 grados en direccion de las manecillas del reloj par dejar caer las canicas
  if (estado1 == HIGH) {
    servoMotor1.write(90);   // Posición 90°
    Serial.println("Servo a 90 grados");
    delay(2000);
  } 
  else if (estado2 == HIGH) {
    servoMotor2.write(90);  // Posición 90°
    Serial.println("Servo a 180 grados");
    delay(2000);
  } 
    else if (estado3 == HIGH) {
    servoMotor3.write(90);  // Posición 90°
    Serial.println("Servo a 180 grados");
    delay(2000); 
  } 
  else {
    servoMotor1.write(180);    // Ninguna entrada: posición 180°
    servoMotor2.write(180);     //Posicion de esperar para dejar caer la canica
    servoMotor3.write(180); 
    Serial.println("Servo a 0 grados");
  }

  delay(200); // Pequeña pausa para estabilidad
}
