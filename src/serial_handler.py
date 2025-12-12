import serial
import serial.tools.list_ports
import time

def listar_portas():
    return [p.device for p in serial.tools.list_ports.comports()]

def conectar(porta, baudrate):
    try:
        ser = serial.Serial(porta, baudrate, timeout=1)
        time.sleep(2)
        print(f"✅ Serial conectada: {porta}")
        return ser
    except Exception as e:
        print(f"❌ Erro Serial: {e}")
        return None

def ler_bloco_telemetria(ser):
    """
    Lê o bloco de várias linhas do protocolo SoloV2.
    Retorna um dicionário bruto (strings) com chaves curtas.
    """
    if not ser or not ser.in_waiting:
        return None

    try:
        # 1. Busca o cabeçalho "Msg:"
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if not line.startswith("Msg"):
            return None # Ignora logs de RX/TX/ERRO por enquanto

        raw = {}
        
        # Linha 1: Msg:RSSI,Length
        parts = line.split(':')
        if len(parts) > 1:
            vals = parts[1].split(',')
            raw['rssi'] = vals[0] if len(vals) > 0 else "0"

        # Função auxiliar para ler próxima linha chave:valor
        def read_next():
            l = ser.readline().decode('utf-8', errors='ignore').strip()
            return l.split(':', 1)

        # Leitura Sequencial (Ordem fixa do Arduino)
        # Id, Millis, GPS, Time, Bat, Temp, Pres, Hum, Ax, Ay, Az, Checksum
        
        # Id
        p = read_next()
        raw['id'] = p[1] if len(p) > 1 else "0"
        
        # Millis
        p = read_next()
        raw['millis'] = p[1] if len(p) > 1 else "0"
        
        # GPS:Lat,Lon,Alt
        p = read_next()
        if len(p) > 1:
            gps = p[1].split(',')
            raw['lat'] = gps[0] if len(gps) > 0 else "0"
            raw['lon'] = gps[1] if len(gps) > 1 else "0"
            raw['alt'] = gps[2] if len(gps) > 2 else "0"
            
        # Time (Hora) - Lê e guarda, mas não usamos no DB geralmente
        read_next() 

        # Bat
        p = read_next()
        raw['bat'] = p[1] if len(p) > 1 else "0"

        # Temp
        p = read_next()
        raw['temp'] = p[1] if len(p) > 1 else "0"

        # Pres
        p = read_next()
        raw['pres'] = p[1] if len(p) > 1 else "0"

        # Hum
        p = read_next()
        raw['hum'] = p[1] if len(p) > 1 else "0"

        # Ax, Ay, Az
        p = read_next(); raw['ax'] = p[1] if len(p) > 1 else "0"
        p = read_next(); raw['ay'] = p[1] if len(p) > 1 else "0"
        p = read_next(); raw['az'] = p[1] if len(p) > 1 else "0"

        # Checksum
        p = read_next()
        raw['checksum'] = p[1] if len(p) > 1 else "0"

        return raw

    except Exception as e:
        print(f"⚠️ Erro ao ler bloco: {e}")
        return None