#include <Wire.h>

/*
 * Emulador de Satélite com MPU6050 REAL
 * Lê Acelerômetro e Giroscópio reais, mas simula GPS/Bateria
 * para manter a compatibilidade com o dashboard.
 */

const int MPU_ADDR = 0x68; // Endereço I2C padrão do MPU6050

// Variáveis para guardar os dados reais
int16_t AcX, AcY, AcZ, Tmp, GyX, GyY, GyZ;
float realAx, realAy, realAz, realTemp;

// Variáveis de simulação (GPS, Bateria, etc.)
int packetId = 1;
float simLat = -23.2125;
float simLon = -45.8667;
float simAlt = 600.0;
float simBat = 100.0;

void setup() {
  Serial.begin(115200);
  
  // Inicializa o MPU6050
  Wire.begin();
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x6B);  // Registrador de Power Management
  Wire.write(0);     // Manda 0 para "acordar" o MPU
  Wire.endTransmission(true);
  
  Serial.println("MPU6050 Inicializado!");
  delay(100);
}

void loop() {
  // 1. LER DADOS DO SENSOR (REAL)
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B);  // Começa a ler do registrador ACCEL_XOUT_H
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_ADDR, 14, true); // Pede 14 bytes seguidos

  AcX = Wire.read() << 8 | Wire.read();
  AcY = Wire.read() << 8 | Wire.read();
  AcZ = Wire.read() << 8 | Wire.read();
  Tmp = Wire.read() << 8 | Wire.read();
  GyX = Wire.read() << 8 | Wire.read();
  GyY = Wire.read() << 8 | Wire.read();
  GyZ = Wire.read() << 8 | Wire.read();

  // Conversão para unidades humanas
  // Aceleração: Escala padrão +/- 2g (16384 LSB/g). Convertendo para m/s²
  realAx = (AcX / 16384.0) * 9.81;
  realAy = (AcY / 16384.0) * 9.81;
  realAz = (AcZ / 16384.0) * 9.81;

  // Temperatura: Fórmula do datasheet (Temp em graus Celsius)
  realTemp = (Tmp / 340.00) + 36.53;

  // 2. ATUALIZAR DADOS SIMULADOS (Para o gráfico não ficar parado)
  simBat -= 0.05; // Bateria descarregando
  if(simBat < 0) simBat = 100;
  
  simAlt += 0.5; // Subindo devagar
  
  // 3. ENVIAR NO FORMATO DO PROTOCOLO (SoloV1.py)
  // A ordem deve ser rigorosamente esta:
  
  // Header
  Serial.print("Msg:"); Serial.print("-85"); Serial.print(","); Serial.println("64");
  
  // ID
  Serial.print("Id:"); Serial.println(packetId);
  
  // Millis (Tempo de missão)
  Serial.print("Millis:"); Serial.println(millis());
  
  // GPS (Simulado)
  Serial.print("GPS:"); 
  Serial.print(simLat, 4); Serial.print(","); 
  Serial.print(simLon, 4); Serial.print(","); 
  Serial.println(simAlt, 1);
  
  // Hora (Simulada fixa ou pode usar millis para calcular)
  Serial.print("Time:"); Serial.println("12-00-00");
  
  // Bateria (Simulada)
  Serial.print("Bat:"); Serial.println(simBat, 1);
  
  // Temperatura (REAL do MPU)
  Serial.print("Temp:"); Serial.println(realTemp, 2);
  
  // Pressão (Simulada)
  Serial.print("Pres:"); Serial.println("101325");
  
  // Humidade (Simulada)
  Serial.print("Hum:"); Serial.println("45");
  
  // Acelerômetro (REAL do MPU)
  Serial.print("Ax:"); Serial.println(realAx, 2);
  Serial.print("Ay:"); Serial.println(realAy, 2);
  Serial.print("Az:"); Serial.println(realAz, 2);
  
  // Checksum
  Serial.print("Checksum:"); Serial.println("1");

  // Incrementa contador
  packetId++;
  
  // Delay para controlar a taxa de atualização (10Hz = 100ms)
  delay(100); 
}