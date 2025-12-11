#include <Wire.h>
#include <TinyGPS++.h>
#include <SoftwareSerial.h>

/*
 * CUBESAT FIRMWARE V2: MPU6050 + GPS REAL
 * - MPU6050: I2C (A4/A5)
 * - GPS: Serial Virtual (Pinos 4/3)
 * - Telemetria: Serial Hardware (USB)
 */

// --- CONFIGURAÇÃO DO GPS ---
static const int RXPin = 4, TXPin = 3; // GPS TX no 4, GPS RX no 3
static const uint32_t GPSBaud = 9600;  // 9600 é o padrão da maioria dos módulos (NEO-6M)

// Objetos
TinyGPSPlus gps;
SoftwareSerial ss(RXPin, TXPin);

// Endereço I2C do MPU6050
const int MPU_ADDR = 0x68;

// Variáveis MPU
int16_t AcX, AcY, AcZ, Tmp, GyX, GyY, GyZ;
float realAx, realAy, realAz, realTemp;

// Variáveis de Simulação (Para o que não temos sensor ainda)
int packetId = 1;
float simBat = 100.0;
unsigned long lastTelemetryTime = 0;
const int TELEMETRY_INTERVAL = 100; // Enviar a cada 100ms (10Hz)

void setup() {
  // 1. Serial USB (Para o Python)
  Serial.begin(115200);

  // 2. Serial GPS
  ss.begin(GPSBaud);

  // 3. Inicializa MPU6050
  Wire.begin();
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x6B);  // Power Management
  Wire.write(0);     // Acordar MPU
  Wire.endTransmission(true);

  Serial.println("Sistema Iniciado: MPU6050 + GPS");
}

void loop() {
  // A. LER DADOS DO GPS CONSTANTEMENTE
  // O GPS manda dados o tempo todo, precisamos ler cada caractere
  while (ss.available() > 0) {
    gps.encode(ss.read());
  }

  // B. ROTINA DE ENVIO DE TELEMETRIA (Non-blocking delay)
  // Usamos millis() em vez de delay() para não perder dados do GPS
  if (millis() - lastTelemetryTime > TELEMETRY_INTERVAL) {
    lastTelemetryTime = millis();
    sendTelemetry();
  }

  delay(1000);
}

void sendTelemetry() {
  // 1. Ler MPU6050
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B);
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_ADDR, 14, true);

  AcX = Wire.read() << 8 | Wire.read();
  AcY = Wire.read() << 8 | Wire.read();
  AcZ = Wire.read() << 8 | Wire.read();
  Tmp = Wire.read() << 8 | Wire.read();
  GyX = Wire.read() << 8 | Wire.read();
  GyY = Wire.read() << 8 | Wire.read();
  GyZ = Wire.read() << 8 | Wire.read();

  realAx = (AcX / 16384.0) * 9.81;
  realAy = (AcY / 16384.0) * 9.81;
  realAz = (AcZ / 16384.0) * 9.81;
  realTemp = (Tmp / 340.00) + 36.53;

  // 2. Simular Bateria
  simBat -= 0.01;
  if (simBat < 0) simBat = 100;

  // 3. ENVIO FORMATADO (Protocolo SoloV1)

  // Header
  Serial.print("Msg:"); Serial.print("-85"); Serial.print(","); Serial.println("64");

  // ID
  Serial.print("Id:"); Serial.println(packetId);

  // Millis
  Serial.print("Millis:"); Serial.println(millis());

// GPS (REAL)
  Serial.print("GPS:");
  if (gps.location.isValid()) {
    Serial.print(gps.location.lat(), 6);
    Serial.print(",");
    Serial.print(gps.location.lng(), 6);
    Serial.print(",");
    Serial.println(gps.altitude.meters(), 1); // Este já estava certo
  } else {
    // CORREÇÃO: Usar println aqui também!
    Serial.println("0.000000,0.000000,0.0"); 
  }

  // Hora (Do GPS ou Fixa)
  Serial.print("Time:");
  if (gps.time.isValid()) {
    Serial.print(gps.time.hour()); Serial.print("-");
    Serial.print(gps.time.minute()); Serial.print("-");
    Serial.println(gps.time.second());
  } else {
    Serial.println("00-00-00");
  }

  // Bateria e Sensores
  Serial.print("Bat:"); Serial.println(simBat, 1);
  Serial.print("Temp:"); Serial.println(realTemp, 2);
  Serial.print("Pres:"); Serial.println("101325"); // Ainda simulado
  Serial.print("Hum:"); Serial.println("45");       // Ainda simulado

  // Acelerômetro
  Serial.print("Ax:"); Serial.println(realAx, 2);
  Serial.print("Ay:"); Serial.println(realAy, 2);
  Serial.print("Az:"); Serial.println(realAz, 2);

  // Checksum
  Serial.print("Checksum:"); Serial.println("1");

  packetId++;
}