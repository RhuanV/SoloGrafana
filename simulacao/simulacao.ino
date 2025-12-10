/*
 * Emulador de Telemetria CubeSat para SoloV1.py
 * * Este código simula o envio de pacotes de dados no formato EXATO
 * esperado pelo script Python da estação de solo.
 * * Configuração:
 * - Placa: Arduino Nano (ou Uno/Mega)
 * - Baud Rate: 115200 (Deve bater com o Python)
 */

struct TelemetryFrame {
  int id;
  unsigned long millisTime;
  float lat;
  float lon;
  float alt;
  int hour; int min; int sec;
  float bat;     // Bateria %
  float temp;    // Temperatura C
  long pres;     // Pressão Pa
  int hum;       // Humidade %
  float ax; float ay; float az; // Acelerômetro
  int checksum;
};

// --- DADOS FALSOS ---
// Criamos 3 cenários para variar os gráficos no Dashboard
TelemetryFrame frames[] = {
  // Cenario 1: Estável
  {1, 1000, -23.2125, -45.8667, 600.0, 12, 0, 0, 98.5, 25.0, 101325, 45, 0.01, 0.02, 9.81, 1},
  
  // Cenario 2: Subindo e aquecendo (Simulação de lançamento)
  {2, 2000, -23.2130, -45.8670, 850.5, 12, 0, 1, 97.0, 35.5, 98000, 40, 0.50, 0.10, 12.5, 1},
  
  // Cenario 3: Descendo e bateria caindo
  {3, 3000, -23.2135, -45.8675, 400.0, 12, 0, 2, 85.0, 28.2, 102000, 50, -0.1, -0.1, 9.70, 1}
};

int totalFrames = 3;
int currentFrame = 0;

void setup() {
  // Importante: O baudrate deve ser igual ao do Python (115200)
  Serial.begin(115200);
}

void loop() {
  sendTelemetry(currentFrame);
  
  // Avança para o próximo frame
  currentFrame++;
  if (currentFrame >= totalFrames) {
    currentFrame = 0; // Volta ao início (Loop)
  }
  
  // Espera 1 segundo entre pacotes (Simula frequência de 1Hz)
  delay(1000);
}

void sendTelemetry(int index) {
  TelemetryFrame f = frames[index];
  
  // A ordem abaixo deve ser RIGOROSAMENTE a mesma que o SoloV1.py lê
  // Verifique as linhas de SerialObj.readline() no seu código Python
  
  // 1. Header (Msg:RSSI,Length)
  Serial.print("Msg:");
  Serial.print("-90"); // RSSI simulado
  Serial.print(",");
  Serial.println("50"); // Tamanho fictício
  
  // 2. ID (Id:valor)
  Serial.print("Id:");
  Serial.println(f.id);
  
  // 3. Millis (Millis:valor)
  Serial.print("Millis:");
  Serial.println(f.millisTime);
  
  // 4. GPS (GPS:Lat,Lon,Alt) - O python espera: values[1].split(',')
  Serial.print("GPS:");
  Serial.print(f.lat, 4);
  Serial.print(",");
  Serial.print(f.lon, 4);
  Serial.print(",");
  Serial.println(f.alt, 1);
  
  // 5. Time (Time:H-M-S) - O python espera: values[1].split('-')
  Serial.print("Time:");
  Serial.print(f.hour);
  Serial.print("-");
  Serial.print(f.min);
  Serial.print("-");
  Serial.println(f.sec);
  
  // 6. Battery (Bat:valor)
  Serial.print("Bat:");
  Serial.println(f.bat, 1);
  
  // 7. Temperature (Temp:valor)
  Serial.print("Temp:");
  Serial.println(f.temp, 1);
  
  // 8. Pressure (Pres:valor)
  Serial.print("Pres:");
  Serial.println(f.pres);
  
  // 9. Humidity (Hum:valor)
  Serial.print("Hum:");
  Serial.println(f.hum);
  
  // 10. Acelerometer X (Ax:valor)
  Serial.print("Ax:");
  Serial.println(f.ax, 2);
  
  // 11. Acelerometer Y (Ay:valor)
  Serial.print("Ay:");
  Serial.println(f.ay, 2);
  
  // 12. Acelerometer Z (Az:valor)
  Serial.print("Az:");
  Serial.println(f.az, 2);
  
  // 13. Checksum (Checksum:1)
  Serial.print("Checksum:");
  Serial.println(f.checksum);
}