import datetime
#import psutil
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

class DatabaseHandler:
    def __init__(self, config):
        self.bucket = config['influxdb']['bucket']
        self.org = config['influxdb']['org']
        self.client = InfluxDBClient(
            url=config['influxdb']['url'],
            token=config['influxdb']['token'],
            org=self.org
        )
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    def enviar_pacote(self, missao, pacote_processado):
        """
        Envia o pacote formatado pelo parser.py
        """
        try:
            tags = pacote_processado['tags']
            fields = pacote_processado['fields']

            p = Point("telemetria_sat") \
                .tag("missao", missao) \
                .time(datetime.datetime.utcnow())
            
            # Adiciona Tags Extras (ex: checksum)
            for k, v in tags.items():
                p.tag(k, v)

            # Adiciona Campos de Telemetria (ex: ax, bat)
            for k, v in fields.items():
                p.field(k, v)

            # Adiciona Telemetria do PC (Bônus)
            #p.field("cpu_pc", psutil.cpu_percent())
            #p.field("ram_pc", psutil.virtual_memory().percent)

            self.write_api.write(bucket=self.bucket, org=self.org, record=p)
        except Exception as e:
            print(f"❌ Erro InfluxDB: {e}")