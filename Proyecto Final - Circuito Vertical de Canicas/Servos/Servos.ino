#include <Servo.h>

// Servos
Servo servoMotor1;
Servo servoMotor2;
Servo servoMotor3;

// Pines de entrada digital (con resistencias pull-down externas)
const int pinEntrada1 = PA11;
const int pinEntrada2 = PA12;
const int pinEntrada3 = PA15;

void setup() {
  Serial.begin(9600);

  // Configurar entradas con pull-down externo
  pinMode(pinEntrada1, INPUT);
  pinMode(pinEntrada2, INPUT);
  pinMode(pinEntrada3, INPUT);

  // Servos en pines PWM compatibles
  servoMotor1.attach(PB1);
  servoMotor2.attach(PB8);
  servoMotor3.attach(PB9);

  // Inicial: todos en reposo
  servoMotor1.write(180);
  servoMotor2.write(180);
  servoMotor3.write(180);
}

void loop() {
  // Leer estado de los switches
  int estado1 = digitalRead(pinEntrada1);
  int estado2 = digitalRead(pinEntrada2);
  int estado3 = digitalRead(pinEntrada3);

  // --- Servo 1 ---
  if (estado1 == HIGH) {
    servoMotor1.write(90);
    Serial.println("Servo 1 → 90°");
  } else {
    servoMotor1.write(180);
  }

  // --- Servo 2 ---
  if (estado2 == HIGH) {
    servoMotor2.write(90);
    Serial.println("Servo 2 → 90°");
  } else {
    servoMotor2.write(180);
  }

  // --- Servo 3 ---
  if (estado3 == HIGH) {
    servoMotor3.write(90);
    Serial.println("Servo 3 → 90°");
  } else {
    servoMotor3.write(180);
  }

  delay(50); // Lectura estable sin delay grande
}
