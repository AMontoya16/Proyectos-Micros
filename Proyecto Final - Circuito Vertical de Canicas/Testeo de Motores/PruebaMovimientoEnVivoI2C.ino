#include <Wire.h>
#include <AccelStepper.h>

// ─────────────────────────────────────────────
// CONFIG I2C
#define I2C_ADDRESS 0x27
#define DESTINO 99
// Test 100
volatile uint8_t respuestaI2C = 4;
volatile bool respuesta_lista = false;

// ─────────────────────────────────────────────
// PINES MOTORES
#define STEP_H PA0
#define DIR_H  PA1
#define STEP_V PA2
#define DIR_V  PA3

#define LED_READY PB10

// ─────────────────────────────────────────────
// CONSTANTES MECÁNICAS
const int STEPS_PER_REV = 200;
const float LEAD_SCREW_PITCH = 8;
const float SECTOR_DISTANCE = 100;
const float DROP_DISTANCE = 150;

const int STEPS_PER_MM = STEPS_PER_REV / LEAD_SCREW_PITCH;
const int STEPS_PER_SECTOR = SECTOR_DISTANCE * STEPS_PER_MM;
const int STEPS_DROP_S = DROP_DISTANCE * STEPS_PER_MM;

// ─────────────────────────────────────────────
// MOTORES
AccelStepper motorH(AccelStepper::DRIVER, STEP_H, DIR_H);
AccelStepper motorV(AccelStepper::DRIVER, STEP_V, DIR_V);

// ─────────────────────────────────────────────
// ESTADOS - NUEVA LÓGICA
int estado_pasado = 2;
int estado_actual = 2;

volatile bool movimiento_pendiente = false;
volatile int objetivo_pendiente = 0;

// ─────────────────────────────────────────────
// EVENTO: maestro envia
void receiveEvent(int howMany) {

    if (howMany <= 0) return;

    int recibido = (int8_t)Wire.read();  // leer incluidos negativos
    respuesta_lista = false;
    digitalWrite(LED_READY, LOW);

    // ============================================================
    // 1. Si recibe -1, -2, -3  → mover a 1, 2, 3
    // ============================================================
    if (recibido == -1 || recibido == -2 || recibido == -3) {

        objetivo_pendiente = -recibido;  // -1→1, -2→2, -3→3
        estado_actual = objetivo_pendiente;

        // Hacer el movimiento real del motor
        moverSegunCambio(estado_pasado, estado_actual);

        estado_pasado = estado_actual;
        movimiento_pendiente = true;

        respuestaI2C = 4;  // NO se envía nada todavía
    }

    // ============================================================
    // 2. Confirmación: si llega el valor positivo esperado
    // ============================================================
    else if (movimiento_pendiente && recibido == objetivo_pendiente) {

        movimiento_pendiente = false;

        // Ahora sí enviar la posición actual real
        respuestaI2C = estado_actual;
    }

    // ============================================================
    // 3. Lógica original completa para derecha/izquierda/abajo/destino
    // ============================================================
    else {

        estado_actual = recibido;

        if (estado_actual == DESTINO) {

            respuestaI2C = 3;
            moverDrop();
            regreso(estado_pasado);
            estado_pasado = 2;
            estado_actual = 2;
        }
        else if (estado_actual == estado_pasado + 1) {

            respuestaI2C = 0;   // derecha
            moverSegunCambio(estado_pasado, estado_actual);
            estado_pasado = estado_actual;
        }
        else if (estado_actual == estado_pasado - 1) {

            respuestaI2C = 1;   // izquierda
            moverSegunCambio(estado_pasado, estado_actual);
            estado_pasado = estado_actual;
        }
        else if (estado_actual == estado_pasado + 3) {

            respuestaI2C = 2;   // abajo
            moverSegunCambio(estado_pasado, estado_actual);
            estado_pasado = estado_actual;
        }
        else {

            respuestaI2C = 4;  // inválido
        }
    }

    // Finalizada la acción → maestro puede leer
    respuesta_lista = true;
    digitalWrite(LED_READY, HIGH);
}

// ─────────────────────────────────────────────
// EVENTO: maestro solicita
void requestEvent() {
    Wire.write(respuestaI2C);
    respuesta_lista = false;
    digitalWrite(LED_READY, LOW);
}

// ─────────────────────────────────────────────
void setup() {

    pinMode(LED_READY, OUTPUT);
    digitalWrite(LED_READY, LOW);

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
// LOOP
void loop() {
    // vacío
}

// ─────────────────────────────────────────────
// MOVIMIENTOS SEGÚN CAMBIO
void moverSegunCambio(int pasado, int actual) {

    if (actual == pasado + 1) {
        motorH.move(STEPS_PER_SECTOR);
    }
    else if (actual == pasado - 1) {
        motorH.move(-STEPS_PER_SECTOR);
    }
    else if (actual == pasado + 3) {
        motorV.move(STEPS_PER_SECTOR);
    }
    else {
        return;
    }

    while (motorH.distanceToGo() != 0 || motorV.distanceToGo() != 0) {
        motorH.run();
        motorV.run();
    }
}

// ─────────────────────────────────────────────
// DESCENSO LIGERO EN DESTINO
void moverDrop() {
    motorV.move(STEPS_DROP_S);
    while (motorV.distanceToGo() != 0) motorV.run();
    delay(400);
}

// ─────────────────────────────────────────────
// REGRESO A POSICIÓN DEFAULT (2)
void regreso(int pos_actual) {

    motorV.move(-STEPS_DROP_S);
    while (motorV.distanceToGo() != 0) motorV.run();
    delay(400);

    if (pos_actual == 7) {

        motorH.move(STEPS_PER_SECTOR);
        while (motorH.distanceToGo() != 0) motorH.run();

        for (int i = 0; i < 2; i++) {
            motorV.move(-STEPS_PER_SECTOR);
            while (motorV.distanceToGo() != 0) motorV.run();
        }
    }
    else if (pos_actual == 8) {

        for (int i = 0; i < 2; i++) {
            motorV.move(-STEPS_PER_SECTOR);
            while (motorV.distanceToGo() != 0) motorV.run();
        }
    }
    else if (pos_actual == 9) {

        motorH.move(-STEPS_PER_SECTOR);
        while (motorH.distanceToGo() != 0) motorH.run();

        for (int i = 0; i < 2; i++) {
            motorV.move(-STEPS_PER_SECTOR);
            while (motorV.distanceToGo() != 0) motorV.run();
        }
    }

    motorH.setCurrentPosition(0);
    motorV.setCurrentPosition(0);
}

