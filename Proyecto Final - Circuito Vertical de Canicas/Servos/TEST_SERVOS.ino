#include <Servo.h>

// Servos
Servo servoMotor1;
Servo servoMotor2;
Servo servoMotor3;

void setup() {
  // Adjuntar servos a pines compatibles del STM32
  servoMotor1.attach(PB1);   // Servo 1
  servoMotor2.attach(PB8);   // Servo 2
  servoMotor3.attach(PB9);   // Servo 3
}

void loop() {

  // Mover servo 1 a 90°
  servoMotor1.write(90);
  delay(2000);

  // Mover servo 2 a 90°
  servoMotor2.write(90);
  delay(2000);

  // Mover servo 3 a 90°
  servoMotor3.write(90);
  delay(2000);

  // Regresar los 3 servos a 180° (posición de reposo)
  servoMotor1.write(180);
  servoMotor2.write(180);
  servoMotor3.write(180);
  delay(2000);
}
