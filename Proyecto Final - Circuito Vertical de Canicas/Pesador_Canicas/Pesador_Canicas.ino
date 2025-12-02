//PRUEBA SIN LA LIBRERIA 
#define DT 3 //dara
#define SCK 2 //seial clock

// #define BTN_TARA 4   // <<< botón para tarar (comentado)

float factor_calibracion = 212.0;
const float peso_por_canica = 5.5;
const float hist = 1;
const int muestras = 10;

long offset = 0;
int canicas = 0;
float peso_referencia = 0;

long leerHX711() {
  while (digitalRead(DT));

  long valor = 0;
  for (int i = 0; i < 24; i++) {
    digitalWrite(SCK, HIGH);
    delayMicroseconds(2);
    valor <<= 1;
    digitalWrite(SCK, LOW);
    delayMicroseconds(2);
    if (digitalRead(DT)) valor++;
  }

  digitalWrite(SCK, HIGH);
  delayMicroseconds(2);
  digitalWrite(SCK, LOW);

  if (valor & 0x800000) valor |= ~0xFFFFFF;
  return valor;
}

long leerPromedio() {
  long suma = 0;
  for (int i = 0; i < muestras; i++) {
    suma += leerHX711();
  }
  return suma / muestras;
}

void setup() {
  Serial.begin(9600);
  pinMode(DT, INPUT);
  pinMode(SCK, OUTPUT);
  digitalWrite(SCK, LOW);

  // pinMode(BTN_TARA, INPUT_PULLUP);  // BOTÓN DE RESET

  Serial.println("Tarar (quite todo)");
  delay(3000);

  offset = leerPromedio();
  peso_referencia = 0;
}

void loop() {

  /* BOTON DE RESET

  if (digitalRead(BTN_TARA) == LOW) {
    delay(200);
    offset = leerPromedio();
    peso_referencia = 0;
    canicas = 0;
  }

  */

  float peso_actual = (leerPromedio() - offset) / factor_calibracion;
  float diferencia = peso_actual - peso_referencia;

  if (diferencia > peso_por_canica - hist) {
    int nuevas = round(diferencia / peso_por_canica);
    canicas += nuevas;
    peso_referencia += nuevas * peso_por_canica;
  }

  if (diferencia < -(peso_por_canica - hist)) {
    int retiradas = round(abs(diferencia) / peso_por_canica);
    canicas -= retiradas;
    if (canicas < 0) canicas = 0;
    peso_referencia -= retiradas * peso_por_canica;
  }

  Serial.print("Peso: ");
  Serial.print(peso_actual, 2);
  Serial.print(" g  |  Canicas: ");
  Serial.println(canicas);

  delay(200);
}