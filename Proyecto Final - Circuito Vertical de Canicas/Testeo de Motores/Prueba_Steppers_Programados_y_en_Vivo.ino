#include <Wire.h>
#include <AccelStepper.h>
#include <stdlib.h>

// ─────────────────────────────────────────────
// CONFIGURACIÓN DE PINES STM32
#define STEP_H PA0
#define DIR_H  PA1
#define STEP_V PA2
#define DIR_V  PA3
#define BTN_START PB0
#define LED_STATUS PC13

// ─────────────────────────────────────────────
// CONFIGURACIÓN I2C
#define I2C_ADDRESS 0x27

// ─────────────────────────────────────────────
// CONSTANTES MECÁNICAS
const int STEPS_PER_REV = 200;
const float LEAD_SCREW_PITCH = 8;
const float SECTOR_DISTANCE = 100;
const float DROP_DISTANCE = 50;

const int STEPS_PER_MM = STEPS_PER_REV / LEAD_SCREW_PITCH;
const int STEPS_PER_SECTOR = SECTOR_DISTANCE * STEPS_PER_MM;
const int STEPS_DROP_S = DROP_DISTANCE * STEPS_PER_MM;

// ─────────────────────────────────────────────
// INSTANCIAS DE LOS MOTORES
AccelStepper motorH(AccelStepper::DRIVER, STEP_H, DIR_H);
AccelStepper motorV(AccelStepper::DRIVER, STEP_V, DIR_V);

// ─────────────────────────────────────────────
// VARIABLES DE CONTROL
volatile int *Trayecto = NULL;
volatile int trayectoLength = 0;
volatile bool listaCargada = false;

bool execute = false;
bool end_flag = false;
int n = 0;
int pos_actual = 2;
int pos_siguiente = 2;
bool modoVivo = false; // Control del modo “en vivo”

// ─────────────────────────────────────────────
// EVENTOS I2C
void receiveEvent(int numBytes) {
  if (numBytes <= 0)
    return;

  // Leer primer byte → determina modo
  uint8_t header = Wire.read();

  if (header == 0xA1) {
    // ────────────────────────────────
    // MODO PROGRAMADO
    // ────────────────────────────────
    modoVivo = false;
    listaCargada = false;

    // Limpiar trayecto anterior si existía
    if (Trayecto != NULL) {
      free((void *)Trayecto);
      Trayecto = NULL;
      trayectoLength = 0;
    }

    // Leer resto de la lista
    while (Wire.available()) {
      int dato = Wire.read();

      // Redimensionar el arreglo
      int *temp = (int *)realloc((void *)Trayecto, (trayectoLength + 1) * sizeof(int));
      if (temp == NULL) {
        Serial.println("Error de memoria (realloc).");
        return;
      }

      Trayecto = temp;
      Trayecto[trayectoLength++] = dato;

      if (dato == 99) {
        listaCargada = true;
        break;
      }
    }
  }

  else if (header == 0xA2) {
    // ────────────────────────────────
    // MODO EN VIVO
    // ────────────────────────────────
    modoVivo = true;
    int siguiente = -1;

    if (Wire.available())
      siguiente = Wire.read(); // Leer posición destino inmediata

    if (siguiente > 0 && siguiente != 99) {
      Serial.print("Movimiento en vivo a: ");
      Serial.println(siguiente);
      moverEntreCasillas(pos_actual, siguiente);
      pos_actual = siguiente;
    } else if (siguiente == 99) {
      Serial.println("Fin de movimiento libre");
    }
  }
}

void requestEvent() {
  // Flag para que el maestro sepa si la lista está lista
  if (listaCargada) {
    Wire.write(2);
    listaCargada = false;
  } else {
    Wire.write(0);
  }
}

// ─────────────────────────────────────────────
// SETUP
void setup() {
  Serial.begin(115200);
  while (!Serial);
  Serial.println("STM32 I2C esclavo listo");

  pinMode(BTN_START, INPUT_PULLUP);
  pinMode(LED_STATUS, OUTPUT);
  digitalWrite(LED_STATUS, HIGH);

  Wire.setSDA(PB7);
  Wire.setSCL(PB6);
  Wire.begin(I2C_ADDRESS);
  Wire.onReceive(receiveEvent);
  Wire.onRequest(requestEvent);

  motorH.setMaxSpeed(700);
  motorH.setAcceleration(1100);
  motorV.setMaxSpeed(700);
  motorV.setAcceleration(1100);
  motorH.setCurrentPosition(0);
  motorV.setCurrentPosition(0);
}

// ─────────────────────────────────────────────
// LOOP PRINCIPAL
void loop() {
  if (modoVivo) {
    // En modo en vivo no se hace nada aquí.
    // Todo ocurre dentro del evento I2C.
    return;
  }

  // MODO PROGRAMADO
  if (!execute && trayectoLength > 0) {
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
      return;
    }
  }

  if (execute) {
    if (pos_siguiente == 99) {
      motorV.move(STEPS_DROP_S);
      while (motorV.distanceToGo() != 0)
        motorV.run();
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
}

// ─────────────────────────────────────────────
// FUNCIÓN START
void Start() {
  if (Trayecto[0] == 1) {
    motorH.move(-STEPS_PER_SECTOR);
  } else if (Trayecto[0] == 3) {
    motorH.move(STEPS_PER_SECTOR);
  } else if (Trayecto[0] == 2) {
    delay(1000);
  }

  while (motorH.distanceToGo() != 0)
    motorH.run();
  motorH.setCurrentPosition(0);
  motorV.setCurrentPosition(0);
}

// ─────────────────────────────────────────────
// FUNCIÓN PARA MOVER ENTRE CASILLAS
void moverEntreCasillas(int actual, int siguiente) {
  if (siguiente == 99 || siguiente <= 0)
    return;

  if (siguiente == actual + 1) {      // derecha
    motorH.move(STEPS_PER_SECTOR);
  } else if (siguiente == actual - 1) { // izquierda
    motorH.move(-STEPS_PER_SECTOR);
  } else if (siguiente == actual + 3) { // abajo
    motorV.move(STEPS_PER_SECTOR);
  }

  while (motorH.distanceToGo() != 0 || motorV.distanceToGo() != 0) {
    motorH.run();
    motorV.run();
  }
}

// ─────────────────────────────────────────────
// FUNCIÓN DE REGRESO (idéntica al código base)
void regreso(int pos_actual) {
  motorV.move(-STEPS_DROP_S);
  while (motorV.distanceToGo() != 0)
    motorV.run();
  delay(1000);

  if (pos_actual == 7) {
    motorH.move(STEPS_PER_SECTOR);
    while (motorH.distanceToGo() != 0)
      motorH.run();
    delay(1000);

    for (int i = 0; i < 2; i++) {
      motorV.move(-STEPS_PER_SECTOR);
      while (motorV.distanceToGo() != 0)
        motorV.run();
      delay(1000);
    }
  } else if (pos_actual == 8) {
    for (int i = 0; i < 2; i++) {
      motorV.move(-STEPS_PER_SECTOR);
      while (motorV.distanceToGo() != 0)
        motorV.run();
      delay(1000);
    }
  } else if (pos_actual == 9) {
    motorH.move(-STEPS_PER_SECTOR);
    while (motorH.distanceToGo() != 0)
      motorH.run();
    delay(1000);

    for (int i = 0; i < 2; i++) {
      motorV.move(-STEPS_PER_SECTOR);
      while (motorV.distanceToGo() != 0)
        motorV.run();
      delay(1000);
    }
  }

  motorH.setCurrentPosition(0);
  motorV.setCurrentPosition(0);
}

// ─────────────────────────────────────────────
// FUNCIÓN PARA DETENER Y VOLVER A IDLE
void detenerYReiniciar() {
  execute = false;
  motorH.stop();
  motorV.stop();
  digitalWrite(LED_STATUS, HIGH);
  delay(300);
}
