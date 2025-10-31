#include <Wire.h>

#define I2C_ADDRESS 0x27
#define LED_PIN PA9

volatile bool dataReceived = false;
volatile uint8_t receivedByte = 0;
volatile bool sendOK = false;

// Cuando el maestro envía datos
void receiveEvent(int numBytes) {
  if (numBytes > 0) {
    receivedByte = Wire.read();
    dataReceived = true;
  }
}

// Cuando el maestro solicita datos
void requestEvent() {
  if (sendOK) {
    Wire.write(2);          // Enviar byte de confirmación
    delayMicroseconds(10);  // 🔹 Pequeña pausa por seguridad
    sendOK = false;
  } else {
    Wire.write(0);  // Enviar 0 si no hay datos
    delayMicroseconds(10);
  }
}

void setup() {
  Serial.begin(115200);
  while (!Serial)
    ;
  Serial.println("STM32 I2C esclavo listo");

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);

  Wire.setSDA(PB7);
  Wire.setSCL(PB6);

  Wire.begin(I2C_ADDRESS);
  Wire.onReceive(receiveEvent);
  Wire.onRequest(requestEvent);

  Serial.print("Dirección esclavo: 0x");
  Serial.println(I2C_ADDRESS, HEX);
}

void loop() {
  if (dataReceived) {
    dataReceived = false;

    Serial.print("Dato recibido: ");
    Serial.println(receivedByte);

    if (receivedByte == 1) {
      digitalWrite(LED_PIN, LOW);
      Serial.println("LED encendido");
    } else if (receivedByte == 0) {
      digitalWrite(LED_PIN, HIGH);
      Serial.println("LED apagado");
    }

    sendOK = true;
  }
}
