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
<<<<<<< Updated upstream
  stepper.setMaxSpeed(1000);
  stepper.setAcceleration(500);
=======
  stepper.setMaxSpeed(700);
  stepper.setAcceleration(1100);
>>>>>>> Stashed changes
  stepper.setCurrentPosition(0);
}

void loop() {
<<<<<<< Updated upstream
  stepper.moveTo(-4 * STEPS_PER_REV);
=======
  stepper.moveTo(-8 * STEPS_PER_REV);
>>>>>>> Stashed changes
  stepper.runToPosition();

  stepper.setCurrentPosition(0);

<<<<<<< Updated upstream
  stepper.moveTo(2 * STEPS_PER_REV);
=======
  stepper.moveTo(8 * STEPS_PER_REV);
>>>>>>> Stashed changes
  stepper.runToPosition();

  stepper.setCurrentPosition(0);
}
