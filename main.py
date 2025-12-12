import json
import time
import sys
from src import database, serial_handler, parser, file_manager, Atitude

# Carregar Config
try:
    with open('config/config.json') as f:
        CONFIG = json.load(f)
except:
    print("❌ Config.json não encontrado!"); sys.exit()

def main():
    print("=== ESTAÇÃO DE SOLO V3 (Modular) ===")
    
    # 1. Setup
    missao = CONFIG['mission']['name']
    porta = CONFIG['serial']['port']
    baud = CONFIG['serial']['baudrate']
    
    # 2. Conexões
    arduino = serial_handler.conectar(porta, baud)
    if not arduino: return

    db = database.DatabaseHandler(CONFIG)
    csv_file = file_manager.criar_arquivo_csv("data/launches", missao)
    
    # 3. WebSocket 3D
    Atitude.iniciar()

    print(f"🚀 Monitorando missão: {missao}")
    
    while True:
        try:
            # A. Ler Serial (Bloco Bruto)
            raw_data = serial_handler.ler_bloco_telemetria(arduino)
            
            if raw_data:
                # B. Processar (Limpar, Converter, Renomear)
                pacote = parser.processar_telemetria(raw_data)
                
                # C. Usar os dados
                # 1. Enviar para Banco
                db.enviar_pacote(missao, pacote)
                
                # 2. Atualizar 3D (Usa os atalhos 'raw_nums' que criamos no parser)
                nums = pacote['raw_nums']
                Atitude.atualizar(nums['ax'], nums['ay'], nums['az'])
                
                # 3. Salvar CSV (Salva os campos finais formatados)
                # Dica: flatten junta tags e fields num só dict pro CSV
                dados_csv = {**pacote['tags'], **pacote['fields'], "millis": nums['millis']}
                file_manager.salvar_dados(csv_file, dados_csv)
                
                print(f"📡 RX: Id={pacote['fields']['pacote_id']} | Bat={pacote['fields']['bateria_pct']}% | Checksum={pacote['tags']['checksum_status']}")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Erro no loop: {e}")

if __name__ == "__main__":
    main()