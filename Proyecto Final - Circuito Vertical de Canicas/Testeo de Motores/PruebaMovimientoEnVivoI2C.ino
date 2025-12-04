#include <Wire.h>
#include <AccelStepper.h>
#include <Servo.h>

// Codigo version funcional

// =======================================================
// I2C
// =======================================================
#define I2C_ADDRESS 0x27
#define DESTINO 99

volatile int8_t comando_recibido = 0;
volatile bool nuevo_comando = false;
uint8_t respuestaI2C = 4;

// =======================================================
// SERVOS NO BLOQUEANTES
// =======================================================
Servo servoMotor1;
Servo servoMotor2;
Servo servoMotor3;

#define SERVO1_PIN PB1
#define SERVO2_PIN PB8
#define SERVO3_PIN PB9

const int ANGULO_ACTIVO  = 90;
const int ANGULO_REPOSO  = 180;

bool servoPendiente = false;
int servoObjetivo = 0;

unsigned long servoTimer = 0;
bool servoEtapa1 = false;
bool servoEtapa2 = false;

void iniciarServo(int s)
{
    servoObjetivo = s;
    servoPendiente = true;

    servoEtapa1 = true;
    servoEtapa2 = false;

    servoTimer = millis();
}

void actualizarServo()
{
    if (!servoPendiente) return;

    // Etapa 1: activar
    if (servoEtapa1 && millis() - servoTimer >= 5)
    {
        if (servoObjetivo == 1) servoMotor1.write(ANGULO_ACTIVO);
        if (servoObjetivo == 2) servoMotor2.write(ANGULO_ACTIVO);
        if (servoObjetivo == 3) servoMotor3.write(ANGULO_ACTIVO);

        servoEtapa1 = false;
        servoEtapa2 = true;
        servoTimer = millis();
        return;
    }

    // Etapa 2: reposo
    if (servoEtapa2 && millis() - servoTimer >= 300)
    {
        if (servoObjetivo == 1) servoMotor1.write(ANGULO_REPOSO);
        if (servoObjetivo == 2) servoMotor2.write(ANGULO_REPOSO);
        if (servoObjetivo == 3) servoMotor3.write(ANGULO_REPOSO);

        servoEtapa2 = false;
        servoPendiente = false;
    }
}

// =======================================================
// MOTORES
// =======================================================
#define STEP_H PA0
#define DIR_H  PA1
#define STEP_V PA2
#define DIR_V  PA3
#define LED_READY PB10

AccelStepper motorH(AccelStepper::DRIVER, STEP_H, DIR_H);
AccelStepper motorV(AccelStepper::DRIVER, STEP_V, DIR_V);

// =======================================================
// MECÁNICA
// =======================================================
const int STEPS_PER_REV = 200;
const float LEAD_SCREW_PITCH = 8;
const float SECTOR_DISTANCE = 100;
const float DROP_DISTANCE = 150;

const int STEPS_PER_MM = STEPS_PER_REV / LEAD_SCREW_PITCH;
const int STEPS_PER_SECTOR = SECTOR_DISTANCE * STEPS_PER_MM;
const int STEPS_DROP_S = DROP_DISTANCE * STEPS_PER_MM;

// =======================================================
// ESTADOS
// =======================================================
int estado_pasado = 2;
int estado_actual = 2;

bool esperandoConfirmacion = false;
int objetivoConfirmacion = 0;

// =======================================================
// ISR — maestro ENVÍA
// =======================================================
void receiveEvent(int howMany)
{
    if (howMany <= 0) return;

    comando_recibido = (int8_t)Wire.read();
    nuevo_comando = true;
}

// =======================================================
// ISR — maestro SOLICITA
// =======================================================
void requestEvent()
{
    Wire.write(respuestaI2C);
}

// =======================================================
// MOVIMIENTO SIMPLE
// =======================================================
void moverSegunCambio(int pasado, int actual)
{
    if (actual == pasado + 1)
        motorH.move(STEPS_PER_SECTOR);
    else if (actual == pasado - 1)
        motorH.move(-STEPS_PER_SECTOR);
    else if (actual == pasado + 3)
        motorV.move(STEPS_PER_SECTOR);
    else
        return;

    while (motorH.distanceToGo() || motorV.distanceToGo())
    {
        motorH.run();
        motorV.run();
    }
}

void moverDrop()
{
    motorV.move(STEPS_DROP_S);
    while (motorV.distanceToGo()) motorV.run();
}

void regreso(int pos_actual)
{
    motorV.move(-STEPS_DROP_S);
    while (motorV.distanceToGo()) motorV.run();

    if (pos_actual == 7)
    {
        motorH.move(STEPS_PER_SECTOR);
        while (motorH.distanceToGo()) motorH.run();

        for (int i=0;i<2;i++){
            motorV.move(-STEPS_PER_SECTOR);
            while (motorV.distanceToGo()) motorV.run();
        }
    }
    else if (pos_actual == 8)
    {
        for (int i=0;i<2;i++){
            motorV.move(-STEPS_PER_SECTOR);
            while (motorV.distanceToGo()) motorV.run();
        }
    }
    else if (pos_actual == 9)
    {
        motorH.move(-STEPS_PER_SECTOR);
        while (motorH.distanceToGo()) motorH.run();

        for (int i=0;i<2;i++){
            motorV.move(-STEPS_PER_SECTOR);
            while (motorV.distanceToGo()) motorV.run();
        }
    }

    motorH.setCurrentPosition(0);
    motorV.setCurrentPosition(0);
}

// =======================================================
// SETUP
// =======================================================
void setup()
{
    pinMode(LED_READY, OUTPUT);
    digitalWrite(LED_READY, HIGH);

    servoMotor1.attach(SERVO1_PIN);
    servoMotor2.attach(SERVO2_PIN);
    servoMotor3.attach(SERVO3_PIN);

    servoMotor1.write(ANGULO_REPOSO);
    servoMotor2.write(ANGULO_REPOSO);
    servoMotor3.write(ANGULO_REPOSO);

    motorH.setMaxSpeed(700);
    motorH.setAcceleration(1100);

    motorV.setMaxSpeed(700);
    motorV.setAcceleration(1100);

    Wire.setSDA(PB7);
    Wire.setSCL(PB6);
    Wire.begin(I2C_ADDRESS);

    Wire.onReceive(receiveEvent);
    Wire.onRequest(requestEvent);

    motorH.setCurrentPosition(0);
    motorV.setCurrentPosition(0);
}

// =======================================================
// LOOP
// =======================================================
void loop()
{
    actualizarServo();

    if (!nuevo_comando) return;

    int8_t cmd = comando_recibido;
    nuevo_comando = false;

    // bloquear maestro
    digitalWrite(LED_READY, LOW);

    // ===================================================
    // CONFIRMACIÓN
    // ===================================================
    if (esperandoConfirmacion)
    {
        if (cmd == objetivoConfirmacion)
        {
            respuestaI2C = objetivoConfirmacion;

            // permitir lectura INMEDIATA
            digitalWrite(LED_READY, HIGH);

            // mover servo DESPUÉS
            iniciarServo(objetivoConfirmacion);

            esperandoConfirmacion = false;
        }
        return;
    }

    // ===================================================
    // NEGATIVOS
    // ===================================================
    if (cmd == -1 || cmd == -2 || cmd == -3)
    {
        int objetivo = -cmd;

        estado_actual = objetivo;
        moverSegunCambio(estado_pasado, estado_actual);
        estado_pasado = estado_actual;

        // maestro debe confirmar
        esperandoConfirmacion = true;
        objetivoConfirmacion = objetivo;

        // aun no hay dato válido
        respuestaI2C = 4;

        // maestro puede leer YA
        digitalWrite(LED_READY, HIGH);
        return;
    }

    // ===================================================
    // DESTINO
    // ===================================================
    if (cmd == DESTINO)
    {
        respuestaI2C = 3;
        moverDrop();
        regreso(estado_pasado);

        estado_pasado = 2;
        estado_actual = 2;

        digitalWrite(LED_READY, HIGH);
        return;
    }

    // ===================================================
    // MOVIMIENTOS NORMALES
    // ===================================================
    estado_actual = cmd;

    if (estado_actual == estado_pasado + 1) respuestaI2C = 0;
    else if (estado_actual == estado_pasado - 1) respuestaI2C = 1;
    else if (estado_actual == estado_pasado + 3) respuestaI2C = 2;
    else respuestaI2C = 4;

    moverSegunCambio(estado_pasado, estado_actual);
    estado_pasado = estado_actual;

    digitalWrite(LED_READY, HIGH);
}

