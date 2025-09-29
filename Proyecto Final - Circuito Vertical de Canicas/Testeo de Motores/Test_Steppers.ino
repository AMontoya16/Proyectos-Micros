/*
   Controlling a stepper with AccelStepper library
   Modified so that 0 is always consistent
   and the motor makes one full turn forward and back
*/

#include <AccelStepper.h>

// Definimos STEP en PA0 y DIR en PA1
#define STEP_PIN PA0
#define DIR_PIN  PA1

AccelStepper stepper(AccelStepper::DRIVER, STEP_PIN, DIR_PIN);

const int STEPS_PER_REV = 200;

void setup() {
  stepper.setMaxSpeed(700);
  stepper.setAcceleration(1100);
  stepper.setCurrentPosition(0);
}

void loop() {
  stepper.moveTo(-8 * STEPS_PER_REV);
  stepper.runToPosition();

  stepper.setCurrentPosition(0);

  stepper.moveTo(8 * STEPS_PER_REV);
  stepper.runToPosition();

  stepper.setCurrentPosition(0);
}
