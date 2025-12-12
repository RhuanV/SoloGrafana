def safe_float(value):
    try:
        return float(value)
    except:
        return 0.0

def processar_telemetria(raw):
    """
    Recebe o dict bruto (chaves curtas, strings)
    Retorna dict formatado para o InfluxDB (chaves longas, floats, tags separadas).
    """
    if not raw:
        return None

    # 1. Conversão de Tipos
    # Transforma tudo em número
    rssi = safe_float(raw.get('rssi'))
    pid = safe_float(raw.get('id'))
    bat = safe_float(raw.get('bat'))
    temp = safe_float(raw.get('temp'))
    pres = safe_float(raw.get('pres'))
    hum = safe_float(raw.get('hum'))
    ax = safe_float(raw.get('ax'))
    ay = safe_float(raw.get('ay'))
    az = safe_float(raw.get('az'))
    lat = safe_float(raw.get('lat'))
    lon = safe_float(raw.get('lon'))
    alt = safe_float(raw.get('alt'))
    
    # 2. Lógica do Checksum (Tag)
    cks_val = raw.get('checksum', '0')
    cks_status = "ok" if cks_val == "1" else "fail"

    # 3. Montagem do Pacote Final (Mapping SoloV2)
    # Estrutura separada para facilitar o envio ao Influx
    return {
        "tags": {
            "checksum_status": cks_status,
            "satelite": "Cubesat-1"
        },
        "fields": {
            "rssi": rssi,
            "pacote_id": pid,         # SoloV2 chamava de 'pacote_id'
            "bateria_pct": bat,       # SoloV2 chamava de 'bateria_pct'
            "temperatura": temp,
            "pressao": pres,
            "humidade": hum,
            "aceleracao_x": ax,
            "aceleracao_y": ay,
            "aceleracao_z": az,
            "latitude": lat,
            "longitude": lon,
            "altitude": alt
        },
        # Dados auxiliares para o loop principal (ex: websocket)
        "raw_nums": {
            "ax": ax, "ay": ay, "az": az,
            "millis": raw.get('millis', '0')
        }
    }