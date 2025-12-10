import serial
import collections
import time
import os
import math
import msvcrt
from geographiclib.geodesic import Geodesic

myLat = -23.212542  # deg
myLon = -45.866778  # deg
myAlt = 600  # m

# ------------------------ escrever arquivo
j = 1
filePath = "launches/Bat"+str(j)+".csv"
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
print("Writing Bat on file "+filePath)
fileTel = open(filePath, "x")
fileTel.write("Id,Tempo (ms),RSSI (dBm),Checksum (bool),Lat (deg),Lon (deg),Alt (m),Hora,Min,Seg,Temp (Celsius),Pres (Pa),Hum (%),Ax (m/s2),Ay (m/s2),Az (m/s2)\n")
fileTel.flush()


# ------------------------ serial start

print("Initializing Receiver")
# Adapt Port COM #########################
SerialObj = serial.Serial('COM3')
SerialObj.baudrate = 115200
SerialObj.bytesize = 8
SerialObj.parity = 'N'
SerialObj.stopbits = 1
SerialObj.timeout = 3
time.sleep(1)
SerialObj.flushInput()

print("Init Sucess, receiving data:")

while True:
    if msvcrt.kbhit():
        if (msvcrt.getch() == b'p'):
            print("\nSent Ping...")
            SerialObj.write(b'P')

    i = 0
    while SerialObj.in_waiting:
        packet = SerialObj.readline()
        reading = packet.decode('utf').rstrip('\r\n')
        values = reading.split(':')

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
                fields = values[1].split(',')
                Rssi = fields[0]
                Length = fields[1]

                packet = SerialObj.readline()
                reading = packet.decode('utf').rstrip('\r\n')
                values = reading.split(':')
                Id = values[1]

                packet = SerialObj.readline()
                reading = packet.decode('utf').rstrip('\r\n')
                values = reading.split(':')
                Millis = values[1]

                packet = SerialObj.readline()
                reading = packet.decode('utf').rstrip('\r\n')
                values = reading.split(':')
                fields = values[1].split(',')
                Lat = fields[0]
                Lon = fields[1]
                Alt = fields[2]

                packet = SerialObj.readline()
                reading = packet.decode('utf').rstrip('\r\n')
                values = reading.split(':')
                fields = values[1].split('-')
                Hour = fields[0]
                Min = fields[1]
                Sec = fields[2]

                packet = SerialObj.readline()
                reading = packet.decode('utf').rstrip('\r\n')
                values = reading.split(':')
                Bat = values[1]

                packet = SerialObj.readline()
                reading = packet.decode('utf').rstrip('\r\n')
                values = reading.split(':')
                Temp = values[1]

                packet = SerialObj.readline()
                reading = packet.decode('utf').rstrip('\r\n')
                values = reading.split(':')
                Pres = values[1]

                # depois de:
                # values = reading.split(':')
                # Pres = values[1]

                # --- ler Hum, Ax, Ay, Az ---
                packet = SerialObj.readline()
                reading = packet.decode('utf').rstrip('\r\n')
                values = reading.split(':', 1)
                Hum = values[1] if values[0] == "Hum" else ""

                packet = SerialObj.readline()
                reading = packet.decode('utf').rstrip('\r\n')
                values = reading.split(':', 1)
                Ax = values[1] if values[0] == "Ax" else ""

                packet = SerialObj.readline()
                reading = packet.decode('utf').rstrip('\r\n')
                values = reading.split(':', 1)
                Ay = values[1] if values[0] == "Ay" else ""

                packet = SerialObj.readline()
                reading = packet.decode('utf').rstrip('\r\n')
                values = reading.split(':', 1)
                Az = values[1] if values[0] == "Az" else ""

                # --- por fim, Checksum ---
                packet = SerialObj.readline()
                reading = packet.decode('utf').rstrip('\r\n')
                values = reading.split(':', 1)
                Checksum = values[1] if values[0] == "Checksum" else ""
                if (Checksum != "1"):
                    print("Warning: Checksum failed in this packet")

                BatMin = int(Millis) / 60000.0

                print("Id: " + Id + ",RSSI: " + Rssi +
                      " dBm, Millis: " + Millis + " ms, Bat: " + Bat + " %")
                print("GPS:{Pos: " + Lat + " deg, " + Lon + " deg, " +
                      Alt + " m" + "}")
                print("Temp: " + Temp + " Celsius, Pres: " +
                      Pres + " Pa, Hum: " + Hum + " %")
                print("Acc:{Ax: " + Ax + ", Ay: " + Ay + ", Az: " + Az + "}")

                fileBat.write(Bat + "," + Millis + "," +
                              Bat + "%," + str(BatMin) + "\n")

                # ATENÇÃO: o cabeçalho do Tel.csv deve bater com esta ordem!
                fileTel.write(
                    Id + "," + Millis + "," + Rssi + "," + Checksum + "," + Lat + "," +
                    Lon + "," + Alt + "," + Hour + "," + Min + "," + Sec + "," +
                    Temp + "," + Pres + "," + Hum + "," + Ax + "," + Ay + "," + Az + "\n"
                )

                fileBat.flush()
                fileTel.flush()

                if abs(float(Lat)) > 0.1:
                    print("#----------------------------------------#")
                    GeoData = Geodesic.WGS84.Inverse(
                        myLat, myLon, float(Lat), float(Lon))
                    distance = GeoData['s12']/1000.0
                    print("Distance (2d): " + str(distance) + " km")
                    Radius = 6371.0
                    theta = math.radians(GeoData['a12'])
                    h = float(Alt)/1000.0 - myAlt/1000.0
                    distance3d = math.sqrt(
                        Radius**2 + (Radius + h)**2 - 2*Radius*(Radius + h)*math.cos(theta))
                    print("Distance (3d): " + str(distance3d) + " km")
                    gamma = math.acos(
                        (distance3d**2 + Radius**2 - (Radius + h)**2) / (2*distance3d*Radius))
                    print("Heading: " + str(GeoData['azi1']) + " degrees, Altidude: " +
                          str(math.degrees(gamma) - 90.0) + " degrees")
                    print("#----------------------------------------#")
                else:
                    print("Invalid GPS reading, waiting for next msg")
                print("******************************************")
