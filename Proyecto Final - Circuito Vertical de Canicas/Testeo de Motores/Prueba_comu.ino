#include <Wire.h>

#define I2C_ADDRESS 0x27  // Dirección I2C del STM32 esclavo

volatile bool dataReceived = false;
volatile byte receivedByte = 0;

// Callback que se ejecuta cuando el maestro envía datos
void onReceive(int numBytes) {
  if (numBytes > 0) {
    receivedByte = Wire.read();  // Leer un byte
    dataReceived = true;
  }
}

void setup() {
  Serial.begin(115200);
  Serial.println("STM32 listo como esclavo I2C de prueba");

  // Iniciar como esclavo I2C
  Wire.begin(I2C_ADDRESS);
  Wire.onReceive(onReceive);

  Serial.print("Dirección I2C esclavo: 0x");
  Serial.println(I2C_ADDRESS, HEX);
}

void loop() {
  if (dataReceived) {
    dataReceived = false;
    Serial.print("Dato recibido: ");
    Serial.println(receivedByte);
  }
}
