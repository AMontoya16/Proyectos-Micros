#include <Wire.h> 
#include <AccelStepper.h>
#include <Servo.h>

// Código versión funcional v10000 EDITADO

// =======================================================
// CONFIGURACIÓN I2C
// =======================================================
#define I2C_ADDRESS 0x27     // Dirección I2C del STM32 como esclavo
#define DESTINO 99           // Código especial para operación DESTINO

volatile int8_t comando_recibido = 0;  // Último comando recibido del maestro
volatile bool nuevo_comando = false;   // Indica si hay comando nuevo
int8_t respuestaI2C = 4;               // Valor que se envía al maestro

// =======================================================
// PARADA DE EMERGENCIA
// =======================================================
volatile bool paradaEmergencia = false;  // Bandera de emergencia activada

// ISR que se ejecuta cuando se presiona el botón de emergencia
void emergencyStopISR()
{
    paradaEmergencia = true;  // Marca estado de emergencia
}

// =======================================================
// SERVOS NO BLOQUEANTES
// =======================================================
Servo servoMotor1;
Servo servoMotor2;
Servo servoMotor3;

#define SERVO1_PIN PB1
#define SERVO2_PIN PB8
#define SERVO3_PIN PB9

const int ANGULO_ACTIVO  = 90;   // Ángulo que ejecuta acción
const int ANGULO_REPOSO  = 180;  // Ángulo de reposo del servo

bool servoPendiente = false;     // Indica si hay una secuencia de servo en proceso
int servoObjetivo = 0;           // Cuál servo debe accionarse

unsigned long servoTimer = 0;    // Control de tiempos sin bloqueo
bool servoEtapa1 = false;        // Etapa de activación
bool servoEtapa2 = false;        // Etapa de regreso a reposo

// Inicia la secuencia no bloqueante de activación de servo
void iniciarServo(int s)
{
    servoObjetivo = s;
    servoPendiente = true;

    servoEtapa1 = true;
    servoEtapa2 = false;

    servoTimer = millis();  // Marca de tiempo inicial
}

// Actualiza el estado de los servos de forma no bloqueante
void actualizarServo()
{
    if (!servoPendiente) return;

    // Etapa 1: activar servo después de 5 ms
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

    // Etapa 2: regresar servo al reposo después de 300 ms
    if (servoEtapa2 && millis() - servoTimer >= 300)
    {
        if (servoObjetivo == 1) servoMotor1.write(ANGULO_REPOSO);
        if (servoObjetivo == 2) servoMotor2.write(ANGULO_REPOSO);
        if (servoObjetivo == 3) servoMotor3.write(ANGULO_REPOSO);

        servoEtapa2 = false;
        servoPendiente = false;  // Secuencia completada
    }
}

// =======================================================
// CONFIGURACIÓN DE MOTORES
// =======================================================
#define STEP_H PA0
#define DIR_H  PA1
#define STEP_V PA2
#define DIR_V  PA3
#define FLAG_READY PB10       // Línea hacia Raspberry Pi indicando "dato listo"

AccelStepper motorH(AccelStepper::DRIVER, STEP_H, DIR_H);  // Motor horizontal
AccelStepper motorV(AccelStepper::DRIVER, STEP_V, DIR_V);  // Motor vertical

// =======================================================
// PARÁMETROS MECÁNICOS
// =======================================================
const int STEPS_PER_REV = 200;          // Pasos por revolución del motor
const float LEAD_SCREW_PITCH = 8;       // Paso del tornillo (mm por vuelta)
const float SECTOR_DISTANCE = 100;      // Distancia entre sectores horizontales
const float DROP_DISTANCE = 150;        // Distancia de caída vertical

const int STEPS_PER_MM = STEPS_PER_REV / LEAD_SCREW_PITCH;          // Pasos por mm
const int STEPS_PER_SECTOR = SECTOR_DISTANCE * STEPS_PER_MM;        // Pasos entre sectores
const int STEPS_DROP_S = DROP_DISTANCE * STEPS_PER_MM;              // Pasos para caída

// =======================================================
// ESTADOS DEL SISTEMA
// =======================================================
int estado_pasado = 2;     // Estado anterior de posición
int estado_actual = 2;     // Estado actual

bool esperandoConfirmacion = false;  // Indica si se espera un valor de confirmación
int objetivoConfirmacion = 0;        // Valor que debe recibirse para confirmar

// =======================================================
// ISR - Evento cuando el maestro escribe
// =======================================================
void receiveEvent(int howMany)
{
    if (howMany <= 0) return;

    comando_recibido = (int8_t)Wire.read();  // Lee comando entrante
    nuevo_comando = true;                    // Marca comando disponible
}

// =======================================================
// ISR - Evento cuando el maestro solicita lectura
// =======================================================
void requestEvent()
{
    Wire.write((int8_t)respuestaI2C);  // Envía un byte al maestro
}

// =======================================================
// FUNCIONES DE MOVIMIENTO
// =======================================================

// Movimiento entre posiciones según variación del estado
void moverSegunCambio(int pasado, int actual)
{
    if (actual == pasado + 1)
        motorH.move(STEPS_PER_SECTOR);        // Movimiento a la derecha
    else if (actual == pasado - 1)
        motorH.move(-STEPS_PER_SECTOR);       // Movimiento a la izquierda
    else if (actual == pasado + 3)
        motorV.move(STEPS_PER_SECTOR);        // Movimiento hacia abajo
    else
        return;

    // Ejecuta movimiento hasta completar pasos
    while (motorH.distanceToGo() || motorV.distanceToGo())
    {
        motorH.run();
        motorV.run();
    }
}

// Movimiento de caída vertical
void moverDrop()
{
    motorV.move(STEPS_DROP_S);
    while (motorV.distanceToGo()) motorV.run();
}

// Regreso a nivel fijo después de caída o movimientos especiales
void regreso(int pos_actual)
{
    motorV.move(-STEPS_DROP_S);
    while (motorV.distanceToGo()) motorV.run();

    if (pos_actual == 7)
    {
        motorH.move(STEPS_PER_SECTOR);
        while (motorH.distanceToGo()) motorH.run();

        for (int i=0; i<2; i++){
            motorV.move(-STEPS_PER_SECTOR);
            while (motorV.distanceToGo()) motorV.run();
        }
    }
    else if (pos_actual == 8)
    {
        for (int i=0; i<2; i++){
            motorV.move(-STEPS_PER_SECTOR);
            while (motorV.distanceToGo()) motorV.run();
        }
    }
    else if (pos_actual == 9)
    {
        motorH.move(-STEPS_PER_SECTOR);
        while (motorH.distanceToGo()) motorH.run();

        for (int i=0; i<2; i++){
            motorV.move(-STEPS_PER_SECTOR);
            while (motorV.distanceToGo()) motorV.run();
        }
    }

    // Reinicia coordenadas internas
    motorH.setCurrentPosition(0);
    motorV.setCurrentPosition(0);
}

// =======================================================
// SETUP DEL SISTEMA
// =======================================================
void setup()
{
    pinMode(FLAG_READY, OUTPUT);      // Señal a Raspberry
    digitalWrite(FLAG_READY, HIGH);   // Indica listo inicialmente

    // Configurar servos
    servoMotor1.attach(SERVO1_PIN);
    servoMotor2.attach(SERVO2_PIN);
    servoMotor3.attach(SERVO3_PIN);

    servoMotor1.write(ANGULO_REPOSO);
    servoMotor2.write(ANGULO_REPOSO);
    servoMotor3.write(ANGULO_REPOSO);

    // Configurar motores
    motorH.setMaxSpeed(700);
    motorH.setAcceleration(1100);

    motorV.setMaxSpeed(700);
    motorV.setAcceleration(1100);

    // Configura interrupción de emergencia en PB0
    pinMode(PB0, INPUT);   // Botón con resistencia externa a 3.3 V
    attachInterrupt(digitalPinToInterrupt(PB0), emergencyStopISR, RISING);

    // Inicialización I2C
    Wire.setSDA(PB7);
    Wire.setSCL(PB6);
    Wire.begin(I2C_ADDRESS);

    Wire.onReceive(receiveEvent);
    Wire.onRequest(requestEvent);

    motorH.setCurrentPosition(0);
    motorV.setCurrentPosition(0);
}

// =======================================================
// LOOP PRINCIPAL
// =======================================================
void loop()
{
    // Si hay emergencia, detener todo inmediatamente
    if (paradaEmergencia)
    {
        motorH.stop();
        motorV.stop();

        motorH.move(0);
        motorV.move(0);

        digitalWrite(FLAG_READY, HIGH);  // Reporta listo pero no operacional

        return;  // No se sigue ejecutando lógica normal
    }

    actualizarServo();  // Servos no bloqueantes

    if (!nuevo_comando) return;  // No hacer nada si no hay comando nuevo

    int8_t cmd = comando_recibido;
    nuevo_comando = false;       // Se limpia bandera

    digitalWrite(FLAG_READY, LOW);  // Señala que aún no hay dato listo

    // Manejo de confirmaciones
    if (esperandoConfirmacion)
    {
        if (cmd == objetivoConfirmacion)
        {
            respuestaI2C = objetivoConfirmacion;
            digitalWrite(FLAG_READY, HIGH);  // Avisa al maestro
            iniciarServo(objetivoConfirmacion);
            esperandoConfirmacion = false;
        }
        return;
    }

    // Comandos negativos representan movimientos preconfirmados
    if (cmd == -1 || cmd == -2 || cmd == -3)
    {
        int objetivo = -cmd;

        respuestaI2C = cmd;  // Se devuelve el mismo número negativo

        estado_actual = objetivo;
        moverSegunCambio(estado_pasado, estado_actual);
        estado_pasado = estado_actual;

        esperandoConfirmacion = true;
        objetivoConfirmacion = objetivo;

        digitalWrite(FLAG_READY, HIGH);
        return;
    }

    // Comando especial DESTINO
    if (cmd == DESTINO)
    {
        respuestaI2C = DESTINO;

        moverDrop();               // Caída vertical
        digitalWrite(FLAG_READY, HIGH);

        regreso(estado_pasado);    // Regreso mecánico final

        estado_pasado = 2;         // Vuelve a estado base
        estado_actual = 2;

        return;
    }

    // Comando 0 significa "no moverse"
    if (cmd == 0)
    {
        respuestaI2C = 0;
        digitalWrite(FLAG_READY, HIGH);
        return;
    }

    // Movimiento normal entre posiciones
    estado_actual = cmd;
    respuestaI2C = estado_actual;

    moverSegunCambio(estado_pasado, estado_actual);
    estado_pasado = estado_actual;

    digitalWrite(FLAG_READY, HIGH);  // Indica listo para lectura
}


