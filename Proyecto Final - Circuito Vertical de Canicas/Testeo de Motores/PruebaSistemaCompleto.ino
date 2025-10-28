#include <AccelStepper.h>

// ─────────────────────────────────────────────
// CONFIGURACIÓN DE PINES STM32
#define STEP_H PA0
#define DIR_H  PA1
#define STEP_V PA2
#define DIR_V  PA3
#define BTN_START PB0
#define LED_STATUS PC13

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
bool execute = false;     // indica si se está ejecutando el trayecto
bool end_flag = false;    // bandera de finalización
int Trayecto[] = {3, 2, 1, 2, 5, 4, 7, 8, 7, 8, 7, 99}; // 99 representa DESTINO
int n = 0;
int pos_actual = 2;
int pos_siguiente = 2;

// ─────────────────────────────────────────────
void setup() {
  pinMode(BTN_START, INPUT_PULLUP);  // Pull-up → LOW al presionar
  pinMode(LED_STATUS, OUTPUT);
  digitalWrite(LED_STATUS, LOW);     // LED apagado en idle

  // Configuración de los motores
  motorH.setMaxSpeed(700);
  motorH.setAcceleration(1100);
  motorV.setMaxSpeed(700);
  motorV.setAcceleration(1100);

  // Posición inicial
  motorH.setCurrentPosition(0);
  motorV.setCurrentPosition(0);
}

// ─────────────────────────────────────────────
void loop() {
  // ────────────────────────────────
  // ESTADO IDLE (espera botón)
  // ────────────────────────────────
  if (!execute) {
    digitalWrite(LED_STATUS, HIGH);  // LED apagado mientras está idle
    if (digitalRead(BTN_START) == LOW) {  // botón presionado (pull-up)
      delay(200);  // antirrebote
      execute = true;
      end_flag = false;
      n = 0;
      pos_actual = Trayecto[n];
      pos_siguiente = Trayecto[n + 1];

      digitalWrite(LED_STATUS, LOW);  // LED encendido durante ejecución
      Start();  // ejecutar etapa START antes del trayecto
    } else {
      return;  // sigue esperando
    }
  }

  // ────────────────────────────────
  // SECUENCIA PRINCIPAL DE MOVIMIENTO
  // ────────────────────────────────
  if (pos_siguiente == 99) {  // llegó al destino
    // Bajar al nivel S (descenso leve)
    motorV.move(STEPS_DROP_S);
    while (motorV.distanceToGo() != 0) motorV.run();
    delay(1000);  // delay entre movimientos

    // Regresar al nivel inicial (posición 2)
    regreso(pos_actual);
    delay(1000);

    detenerYReiniciar(); // finalizar ejecución y volver a idle
    return;
  }

  // Movimiento entre casillas según trayectoria
  moverEntreCasillas(pos_actual, pos_siguiente);
  delay(1000); // delay de 1 segundo entre movimientos

  // Actualizar posiciones
  n++;
  pos_actual = Trayecto[n];
  pos_siguiente = Trayecto[n + 1];
}

// ─────────────────────────────────────────────
// FUNCIÓN START (inicio de trayectoria)
void Start() {
  if (Trayecto[0] == 1) {
    // Mover de posición 2 → 1 (izquierda)
    motorH.move(-STEPS_PER_SECTOR);
  } 
  else if (Trayecto[0] == 3) {
    // Mover de posición 2 → 3 (derecha)
    motorH.move(STEPS_PER_SECTOR);
  } 
  else if (Trayecto[0] == 2) {
    // Esperar señal inicial (sin movimiento)
    delay(1000);
  }

  while (motorH.distanceToGo() != 0) motorH.run();
  motorH.setCurrentPosition(0);
  motorV.setCurrentPosition(0);
}

// ─────────────────────────────────────────────
// FUNCIÓN PARA MOVER ENTRE CASILLAS
void moverEntreCasillas(int actual, int siguiente) {
  if (siguiente == 99 || siguiente <= 0) return;

  if (siguiente == actual + 1) {      // derecha
    motorH.move(STEPS_PER_SECTOR);
  } 
  else if (siguiente == actual - 1) { // izquierda
    motorH.move(-STEPS_PER_SECTOR);
  } 
  else if (siguiente == actual + 3) { // abajo
    motorV.move(STEPS_PER_SECTOR);
  } 

  while (motorH.distanceToGo() != 0 || motorV.distanceToGo() != 0) {
    motorH.run();
    motorV.run();
  }
}

// ─────────────────────────────────────────────
// FUNCIÓN DE REGRESO AL NIVEL DEFAULT (2)
void regreso(int pos_actual) {
  // Subir desde nivel S
  motorV.move(-STEPS_DROP_S);
  while (motorV.distanceToGo() != 0) motorV.run();
  delay(1000);

  // Lógica del diagrama (solo 7, 8, 9)
  if (pos_actual == 7) {
    // Derecha y luego subir 2 sectores
    motorH.move(STEPS_PER_SECTOR);
    while (motorH.distanceToGo() != 0) motorH.run();
    delay(1000);

    for (int i = 0; i < 2; i++) {
      motorV.move(-STEPS_PER_SECTOR);
      while (motorV.distanceToGo() != 0) motorV.run();
      delay(1000);
    }
  }
  else if (pos_actual == 8) {
    // Solo subir 2 sectores
    for (int i = 0; i < 2; i++) {
      motorV.move(-STEPS_PER_SECTOR);
      while (motorV.distanceToGo() != 0) motorV.run();
      delay(1000);
    }
  }
  else if (pos_actual == 9) {
    // Izquierda y luego subir 2 sectores
    motorH.move(-STEPS_PER_SECTOR);
    while (motorH.distanceToGo() != 0) motorH.run();
    delay(1000);

    for (int i = 0; i < 2; i++) {
      motorV.move(-STEPS_PER_SECTOR);
      while (motorV.distanceToGo() != 0) motorV.run();
      delay(1000);
    }
  }

  // Reset de posición
  motorH.setCurrentPosition(0);
  motorV.setCurrentPosition(0);
}

// ─────────────────────────────────────────────
// FUNCIÓN PARA DETENER Y VOLVER A IDLE
void detenerYReiniciar() {
  execute = false;
  motorH.stop();
  motorV.stop();
  digitalWrite(LED_STATUS, HIGH); // LED apagado = idle
  delay(300);
}

