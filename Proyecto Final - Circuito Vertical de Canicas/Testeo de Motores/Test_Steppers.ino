/*
   Controlling a stepper with AccelStepper library
   Modified so that 0 is always consistent
   and the motor makes one full turn forward and back
*/

#include <AccelStepper.h>

// Driver con 2 pines: STEP=2, DIR=5
AccelStepper stepper(AccelStepper::DRIVER, 2, 5);

const int STEPS_PER_REV = 200; // ajusta según tu motor/driver

void setup() {
  stepper.setMaxSpeed(1000);       // velocidad máxima
  stepper.setAcceleration(500);   // aceleración
  stepper.setCurrentPosition(0);  // referencia inicial
}

void loop() {
  // ---- Ir hacia adelante una vuelta ----
  stepper.moveTo(-8*STEPS_PER_REV);
  stepper.runToPosition();

  // ---- Reiniciar el origen para consistencia ----
  stepper.setCurrentPosition(0);

  stepper.moveTo(8*STEPS_PER_REV);
  stepper.runToPosition();

  stepper.setCurrentPosition(0);
}
