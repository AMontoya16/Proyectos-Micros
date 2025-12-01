#include <Wire.h>

#define I2C_ADDRESS 0x27
#define DESTINO 99

volatile uint8_t respuestaI2C = 4;

int estado_pasado = 2;
int estado_actual = 2;

volatile bool delay_en_progreso = false;
volatile unsigned long tiempo_inicio = 0;
const unsigned long DELAY_RESPUESTA = 10000;  // 10 segundos

volatile bool respuesta_lista = false;

// ========================================================
//  Evento: Maestro ENVÍA dato
// ========================================================
void receiveEvent(int howMany) {

    if (howMany > 0) {

        estado_actual = Wire.read();

        // --------------------- LÓGICA ---------------------
        if (estado_actual == DESTINO) {
            respuestaI2C = 3;
        }
        else if (estado_actual == estado_pasado + 1) {
            respuestaI2C = 0;   // derecha
        }
        else if (estado_actual == estado_pasado - 1) {
            respuestaI2C = 1;   // izquierda
        }
        else if (estado_actual == estado_pasado + 3) {
            respuestaI2C = 2;   // abajo
        }
        else {
            respuestaI2C = 4;   // valor inválido
        }

        estado_pasado = estado_actual;

        // -------------------------------------------------
        // INICIAR EL DELAY DE 10 s ANTES DE PERMITIR LECTURA
        // -------------------------------------------------

        respuesta_lista = false;
        delay_en_progreso = true;
        tiempo_inicio = millis();

        // Avisar que NO hay dato listo: PB10 = LOW
        digitalWrite(PB10, LOW);
    }
}

// ========================================================
//  Evento: Maestro SOLICITA dato
// ========================================================
void requestEvent() {

    // SOLO enviamos el valor correcto
    Wire.write(respuestaI2C);

    // Si enviamos un dato válido, bajamos PB10
    respuesta_lista = false;
    digitalWrite(PB10, LOW);
}

// ========================================================
//  Setup
// ========================================================
void setup() {

    Wire.setSDA(PB7);
    Wire.setSCL(PB6);
    Wire.begin(I2C_ADDRESS);

    Wire.onReceive(receiveEvent);
    Wire.onRequest(requestEvent);

    pinMode(PB10, OUTPUT);
    digitalWrite(PB10, LOW);
}

// ========================================================
//  Loop principal
// ========================================================
void loop() {

    if (delay_en_progreso) {

        unsigned long ahora = millis();

        if (ahora - tiempo_inicio >= DELAY_RESPUESTA) {

            delay_en_progreso = false;
            respuesta_lista = true;

            // Ahora sí avisar al maestro:
            digitalWrite(PB10, HIGH);
        }
    }
}

