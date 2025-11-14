#include <Servo.h>
#include <AccelStepper.h>

// ─────────────────────────────────────────────
// SERVOS
Servo servoMotor1;
Servo servoMotor2;
Servo servoMotor3;

// Pines de entrada para los switches (pull-down)
const int pinEntrada1 = PA11;
const int pinEntrada2 = PA12;
const int pinEntrada3 = PA15;

// Ángulos
const int ANGULO_ACTIVO  = 90;
const int ANGULO_REPOSO  = 180;

// Estados previos para saber cuándo regresar
bool estadoPrev1 = false;
bool estadoPrev2 = false;
bool estadoPrev3 = false;

// ─────────────────────────────────────────────
// MOTORES ACCELSTEPPER (CÓDIGO DEL OTRO SISTEMA)
#define STEP_H PA0
#define DIR_H  PA1
#define STEP_V PA2
#define DIR_V  PA3
#define BTN_START PB0
#define LED_STATUS PC13

const int STEPS_PER_REV = 200;
const float LEAD_SCREW_PITCH = 8;
const float SECTOR_DISTANCE = 100;
const float DROP_DISTANCE = 50;

const int STEPS_PER_MM = STEPS_PER_REV / LEAD_SCREW_PITCH;
const int STEPS_PER_SECTOR = SECTOR_DISTANCE * STEPS_PER_MM;
const int STEPS_DROP_S = DROP_DISTANCE * STEPS_PER_MM;

AccelStepper motorH(AccelStepper::DRIVER, STEP_H, DIR_H);
AccelStepper motorV(AccelStepper::DRIVER, STEP_V, DIR_V);

bool execute = false;
bool end_flag = false;
int Trayecto[] = {1, 4, 5, 4, 5, 4, 7, 8, 9, 99};
int n = 0;
int pos_actual = 2;
int pos_siguiente = 2;

// ─────────────────────────────────────────────
void setup() {
  Serial.begin(9600);

  // Entradas de los switches
  pinMode(pinEntrada1, INPUT);
  pinMode(pinEntrada2, INPUT);
  pinMode(pinEntrada3, INPUT);

  // Servos en pines verificados como PWM
  servoMotor1.attach(PB1);  
  servoMotor2.attach(PB8);
  servoMotor3.attach(PB9);

  // Colocar servos en reposo
  servoMotor1.write(ANGULO_REPOSO);
  servoMotor2.write(ANGULO_REPOSO);
  servoMotor3.write(ANGULO_REPOSO);

  // Sistema AccelStepper
  pinMode(BTN_START, INPUT_PULLUP);
  pinMode(LED_STATUS, OUTPUT);

  motorH.setMaxSpeed(700);
  motorH.setAcceleration(1100);
  motorV.setMaxSpeed(700);
  motorV.setAcceleration(1100);

  motorH.setCurrentPosition(0);
  motorV.setCurrentPosition(0);
}

// ─────────────────────────────────────────────
void loop() {

  // ─────────────────────────────────────────────
  // *** CONTROL DE SERVOS (NO BLOQUEANTE) ***
  // ─────────────────────────────────────────────
  bool s1 = digitalRead(pinEntrada1);
  bool s2 = digitalRead(pinEntrada2);
  bool s3 = digitalRead(pinEntrada3);

  // Servo 1
  if (s1 && !estadoPrev1) {
    servoMotor1.write(ANGULO_ACTIVO);
  } else if (!s1 && estadoPrev1) {
    servoMotor1.write(ANGULO_REPOSO);
  }
  estadoPrev1 = s1;

  // Servo 2
  if (s2 && !estadoPrev2) {
    servoMotor2.write(ANGULO_ACTIVO);
  } else if (!s2 && estadoPrev2) {
    servoMotor2.write(ANGULO_REPOSO);
  }
  estadoPrev2 = s2;

  // Servo 3
  if (s3 && !estadoPrev3) {
    servoMotor3.write(ANGULO_ACTIVO);
  } else if (!s3 && estadoPrev3) {
    servoMotor3.write(ANGULO_REPOSO);
  }
  estadoPrev3 = s3;

  // ─────────────────────────────────────────────
  // *** CÓDIGO ACCELSTEPPER ORIGINAL ***
  //     (NO MODIFICADO, SOLO REUBICADO)
  // ─────────────────────────────────────────────

  if (!execute) {
    digitalWrite(LED_STATUS, HIGH);
    if (digitalRead(BTN_START) == LOW) {
      delay(200);
      execute = true;
      end_flag = false;
      n = 0;
      pos_actual = Trayecto[n];
      pos_siguiente = Trayecto[n + 1];

      digitalWrite(LED_STATUS, LOW);
      Start();
    } else {
      motorH.run();
      motorV.run();
      return;
    }
  }

  if (pos_siguiente == 99) {
    motorV.move(STEPS_DROP_S);
    while (motorV.distanceToGo()) motorV.run();

    delay(1000);

    regreso(pos_actual);
    delay(1000);

    detenerYReiniciar();
    return;
  }

  moverEntreCasillas(pos_actual, pos_siguiente);
  delay(1000);

  n++;
  pos_actual = Trayecto[n];
  pos_siguiente = Trayecto[n + 1];
}

// ─────────────────────────────────────────────
// FUNCIONES ORIGINALES ACCELSTEPPER
// (NO SE MODIFICARON)
// ─────────────────────────────────────────────

void Start() {
  if (Trayecto[0] == 1) motorH.move(-STEPS_PER_SECTOR);
  else if (Trayecto[0] == 3) motorH.move(STEPS_PER_SECTOR);
  else if (Trayecto[0] == 2) delay(1000);

  while (motorH.distanceToGo()) motorH.run();
  motorH.setCurrentPosition(0);
  motorV.setCurrentPosition(0);
}

void moverEntreCasillas(int actual, int siguiente) {
  if (siguiente == 99 || siguiente <= 0) return;

  if (siguiente == actual + 1) motorH.move(STEPS_PER_SECTOR);
  else if (siguiente == actual - 1) motorH.move(-STEPS_PER_SECTOR);
  else if (siguiente == actual + 3) motorV.move(STEPS_PER_SECTOR);

  while (motorH.distanceToGo() != 0 || motorV.distanceToGo() != 0) {
    motorH.run();
    motorV.run();
  }
}

void regreso(int pos_actual) {
  motorV.move(-STEPS_DROP_S);
  while (motorV.distanceToGo()) motorV.run();
  delay(1000);

  if (pos_actual == 7) {
    motorH.move(STEPS_PER_SECTOR);
    while (motorH.distanceToGo()) motorH.run();
    delay(1000);

    for (int i = 0; i < 2; i++) {
      motorV.move(-STEPS_PER_SECTOR);
      while (motorV.distanceToGo()) motorV.run();
      delay(1000);
    }
  }
  else if (pos_actual == 8) {
    for (int i = 0; i < 2; i++) {
      motorV.move(-STEPS_PER_SECTOR);
      while (motorV.distanceToGo()) motorV.run();
      delay(1000);
    }
  }
  else if (pos_actual == 9) {
    motorH.move(-STEPS_PER_SECTOR);
    while (motorH.distanceToGo()) motorH.run();
    delay(1000);

    for (int i = 0; i < 2; i++) {
      motorV.move(-STEPS_PER_SECTOR);
      while (motorV.distanceToGo()) motorV.run();
      delay(1000);
    }
  }

  motorH.setCurrentPosition(0);
  motorV.setCurrentPosition(0);
}

void detenerYReiniciar() {
  execute = false;
  motorH.stop();
  motorV.stop();
  digitalWrite(LED_STATUS, HIGH);
  delay(300);
}
