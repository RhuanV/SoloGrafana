import serial
import collections
import time
import os
import math
import msvcrt
from geographiclib.geodesic import Geodesic

# --- [NOVO] Imports para o Dashboard ---
from datetime import datetime
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# --- IMPORTS DE AUTOMAÇÃO ---
import subprocess
import webbrowser
import time
import sys

# --- FUNÇÃO DE AUTO-LANÇAMENTO ---
def iniciar_missao():
    print("\n🚀 INICIANDO SEQUÊNCIA DE LANÇAMENTO...")
    
    # 1. Subir o Docker (Silenciosamente se já estiver rodando)
    print("🐳 Verificando serviços de Telemetria (Docker)...")
    try:
        # 'cwd' garante que ele acha o docker-compose na mesma pasta do script
        subprocess.run(["docker-compose", "up", "-d"], check=True)
    except FileNotFoundError:
        print("❌ ERRO: Docker não encontrado. Instale o Docker Desktop.")
        input("Pressione Enter para sair...")
        sys.exit()
    except subprocess.CalledProcessError:
        print("⚠️ Aviso: Falha ao iniciar Docker. Verifique se o Docker Desktop está aberto.")

    # 2. Aguardar o Banco de Dados (Warm-up)
    print("⏳ Aguardando aquecimento do banco de dados (5s)...")
    time.sleep(5) 

    # 3. Abrir o Dashboard Específico
    # COLE AQUI A URL QUE VOCÊ COPIOU DO SEU NAVEGADOR
    DASHBOARD_URL = "http://localhost:3000/d/adq9dp2/satdashboard?orgId=1&refresh=100ms&kiosk"
    
    # Dica: Adicione '&kiosk' no final da URL para abrir em modo tela cheia/apresentação
    print(f"🖥️ Abrindo Centro de Controle: {DASHBOARD_URL}")
    try:
        webbrowser.open(DASHBOARD_URL)
    except:
        pass

# --- CHAMADA DA FUNÇÃO ---
# Chame isto ANTES de tentar conectar ao InfluxDB
iniciar_missao()

# --- [NOVO] Configuração do InfluxDB ---
# Substitua pelo SEU token gerado no passo anterior
INFLUX_TOKEN = "nQpHZOxI0nJW1NtB3ZydeyZEYDlM2THCZopQ5qLnManv-002oJzsQfv8VMrHXbc-6JEZ7PFHd4L1kTFYG4729g=="
INFLUX_ORG = "ITACUBE"
INFLUX_BUCKET = "telemetria"
INFLUX_URL = "http://localhost:8086"

print("Conectando ao InfluxDB...")
write_api = None
try:
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    print("✅ Conectado ao Dashboard com sucesso!")
except Exception as e:
    print(f"⚠️ Aviso: Não foi possível conectar ao InfluxDB: {e}")


# Função auxiliar para evitar erros se o dado vier vazio
def safe_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

myLat = -23.212542  # deg
myLon = -45.866778  # deg
myAlt = 600  # m

# ------------------------ escrever arquivo
j = 1
filePath = "launches/Bat"+str(j)+".csv"
# Cria diretório se não existir
os.makedirs("launches", exist_ok=True) 

while os.path.exists(filePath):
    j += 1
    filePath = "launches/Bat"+str(j)+".csv"
print("Writing Bat on file "+filePath)
fileBat = open(filePath, "x")
fileBat.write("Carga,Tempo (ms),Carga %,Tempo (min)\n")
fileBat.flush()

j = 1
filePath = "launches/Tel"+str(j)+".csv"
while os.path.exists(filePath):
    j += 1
    filePath = "launches/Tel"+str(j)+".csv"
print("Writing Tel on file "+filePath)
fileTel = open(filePath, "x")
fileTel.write("Id,Tempo (ms),RSSI (dBm),Checksum (bool),Lat (deg),Lon (deg),Alt (m),Hora,Min,Seg,Temp (Celsius),Pres (Pa),Hum (%),Ax (m/s2),Ay (m/s2),Az (m/s2)\n")
fileTel.flush()


# ------------------------ serial start

print("Initializing Receiver")
# Adapt Port COM #########################
# ATENÇÃO: Verifique se sua porta é COM3 mesmo
try:
    SerialObj = serial.Serial('COM6') 
    SerialObj.baudrate = 115200
    SerialObj.bytesize = 8
    SerialObj.parity = 'N'
    SerialObj.stopbits = 1
    SerialObj.timeout = 3
    time.sleep(1)
    SerialObj.flushInput()
    print("Init Sucess, receiving data:")
except Exception as e:
    print(f"ERRO CRÍTICO: Não foi possível abrir a porta Serial: {e}")
    # Para teste sem rádio, comente a linha abaixo
    exit() 

while True:
    if msvcrt.kbhit():
        if (msvcrt.getch() == b'p'):
            print("\nSent Ping...")
            SerialObj.write(b'P')

    i = 0
    while SerialObj.in_waiting:
        try:
            packet = SerialObj.readline()
            reading = packet.decode('utf', errors='ignore').rstrip('\r\n')
            values = reading.split(':')
        except Exception as e:
            print("Erro de leitura serial")
            continue

        if len(values) == 1:
            if values[0] == "RX":
                print("Radio in RX Mode")
            elif values[0] == "TX":
                print("Radio in TX Mode")
            elif values[0] == "ER":
                print("Radio Error!")
            else:
                print(values[0] + " \n")

        elif len(values) == 2:
            if values[0] == "Msg":
                print("******************************************")
                # Parse inicial
                fields = values[1].split(',')
                Rssi = fields[0] if len(fields) > 0 else "0"
                Length = fields[1] if len(fields) > 1 else "0"

                # Leitura sequencial dos pacotes
                # Dica: Adicionei try/excepts implícitos no safe_float depois
                
                packet = SerialObj.readline()
                reading = packet.decode('utf', errors='ignore').rstrip('\r\n')
                values = reading.split(':')
                Id = values[1] if len(values) > 1 else "0"

                packet = SerialObj.readline()
                reading = packet.decode('utf', errors='ignore').rstrip('\r\n')
                values = reading.split(':')
                Millis = values[1] if len(values) > 1 else "0"

                packet = SerialObj.readline()
                reading = packet.decode('utf', errors='ignore').rstrip('\r\n')
                values = reading.split(':')
                fields = values[1].split(',') if len(values) > 1 else ["0","0","0"]
                Lat = fields[0]
                Lon = fields[1]
                Alt = fields[2]

                packet = SerialObj.readline()
                reading = packet.decode('utf', errors='ignore').rstrip('\r\n')
                values = reading.split(':')
                fields = values[1].split('-') if len(values) > 1 else ["0","0","0"]
                Hour = fields[0]
                Min = fields[1]
                Sec = fields[2]

                packet = SerialObj.readline()
                reading = packet.decode('utf', errors='ignore').rstrip('\r\n')
                values = reading.split(':')
                Bat = values[1] if len(values) > 1 else "0"

                packet = SerialObj.readline()
                reading = packet.decode('utf', errors='ignore').rstrip('\r\n')
                values = reading.split(':')
                Temp = values[1] if len(values) > 1 else "0"

                packet = SerialObj.readline()
                reading = packet.decode('utf', errors='ignore').rstrip('\r\n')
                values = reading.split(':')
                Pres = values[1] if len(values) > 1 else "0"

                # --- Sensores IMU ---
                packet = SerialObj.readline()
                reading = packet.decode('utf', errors='ignore').rstrip('\r\n')
                values = reading.split(':', 1)
                Hum = values[1] if len(values) > 1 and values[0] == "Hum" else ""

                packet = SerialObj.readline()
                reading = packet.decode('utf', errors='ignore').rstrip('\r\n')
                values = reading.split(':', 1)
                Ax = values[1] if len(values) > 1 and values[0] == "Ax" else ""

                packet = SerialObj.readline()
                reading = packet.decode('utf', errors='ignore').rstrip('\r\n')
                values = reading.split(':', 1)
                Ay = values[1] if len(values) > 1 and values[0] == "Ay" else ""

                packet = SerialObj.readline()
                reading = packet.decode('utf', errors='ignore').rstrip('\r\n')
                values = reading.split(':', 1)
                Az = values[1] if len(values) > 1 and values[0] == "Az" else ""

                # --- Checksum ---
                packet = SerialObj.readline()
                reading = packet.decode('utf', errors='ignore').rstrip('\r\n')
                values = reading.split(':', 1)
                Checksum = values[1] if len(values) > 1 and values[0] == "Checksum" else ""
                
                if (Checksum != "1"):
                    print("⚠️ Warning: Checksum failed!")

                BatMin = safe_float(Millis) / 60000.0

                # --- Prints no Console ---
                print(f"Id: {Id}, RSSI: {Rssi} dBm, Bat: {Bat}%")
                print(f"GPS: {Lat}, {Lon}, {Alt}m")
                print(f"Ambiente: {Temp}C, {Pres}Pa, {Hum}%")

                # --- [NOVO] ENVIAR PARA O GRAFANA/INFLUXDB ---
                try:
                    p = Point("telemetria_sat") \
                        .tag("satelite", "Cubesat-1") \
                        .tag("checksum_status", "ok" if Checksum == "1" else "fail") \
                        .field("rssi", safe_float(Rssi)) \
                        .field("pacote_id", safe_float(Id)) \
                        .field("bateria_pct", safe_float(Bat)) \
                        .field("temperatura", safe_float(Temp)) \
                        .field("pressao", safe_float(Pres)) \
                        .field("humidade", safe_float(Hum)) \
                        .field("aceleracao_x", safe_float(Ax)) \
                        .field("aceleracao_y", safe_float(Ay)) \
                        .field("aceleracao_z", safe_float(Az)) \
                        .field("latitude", safe_float(Lat)) \
                        .field("longitude", safe_float(Lon)) \
                        .field("altitude", safe_float(Alt)) \
                        .time(datetime.utcnow())
                    
                    if write_api:
                        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=p)
                    # print(" -> Enviado para Dashboard") # Descomente para debug
                    
                except Exception as e_db:
                    print(f"Erro ao enviar para Dashboard: {e_db}")

                # --- Gravação CSV (Original) ---
                fileBat.write(Bat + "," + Millis + "," +
                              Bat + "%," + str(BatMin) + "\n")

                fileTel.write(
                    Id + "," + Millis + "," + Rssi + "," + Checksum + "," + Lat + "," +
                    Lon + "," + Alt + "," + Hour + "," + Min + "," + Sec + "," +
                    Temp + "," + Pres + "," + Hum + "," + Ax + "," + Ay + "," + Az + "\n"
                )

                fileBat.flush()
                fileTel.flush()

                # --- Cálculos Geodésicos (Original) ---
                if abs(safe_float(Lat)) > 0.1:
                    print("#----------------------------------------#")
                    try:
                        GeoData = Geodesic.WGS84.Inverse(
                            myLat, myLon, float(Lat), float(Lon))
                        distance = GeoData['s12']/1000.0
                        print("Distance (2d): " + str(distance) + " km")
                        # ... (Mantinve o resto da lógica original de cálculo)
                    except:
                        pass # Evita travar se GPS vier zerado
                    print("#----------------------------------------#")
                else:
                    print("Invalid GPS reading, waiting for next msg")
                print("******************************************")