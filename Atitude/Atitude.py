import asyncio
import websockets
import threading
import json

# --- ESTADO COMPARTILHADO ---
# Este dicionário guarda a última leitura. 
# O SoloV2 escreve aqui, o WebSocket lê daqui.
_dados_tempo_real = {
    "ax": 0, 
    "ay": 0, 
    "az": 9.8
}

# --- LÓGICA DO SERVIDOR WEBSOCKET ---
async def _enviar_telemetria(websocket):
    """
    Função assíncrona que roda para cada cliente conectado (Grafana).
    Envia o JSON a 30Hz (0.03s).
    """
    print("🟢 [Atitude] Cliente 3D Conectado ao WebSocket!")
    try:
        while True:
            # Serializa o dicionário para JSON e envia
            await websocket.send(json.dumps(_dados_tempo_real))
            # Controla o FPS do stream (0.03s = ~30 FPS)
            await asyncio.sleep(0.03) 
    except websockets.ConnectionClosed:
        print("🔴 [Atitude] Cliente 3D Desconectado")
    except Exception as e:
        print(f"⚠️ [Atitude] Erro no socket: {e}")

async def _iniciar_socket(host="0.0.0.0", port=8765):
    """Sobe o servidor na porta especificada."""
    print(f"🚀 [Atitude] Streaming 3D iniciado em ws://localhost:{port}")
    async with websockets.serve(_enviar_telemetria, host, port):
        await asyncio.Future()  # Mantém rodando indefinidamente

def _thread_wrapper():
    """
    O Asyncio precisa de um Event Loop próprio quando rodado
    dentro de uma Thread secundária.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_iniciar_socket())

# --- FUNÇÕES PÚBLICAS (API) ---

def iniciar():
    """
    Inicia o servidor WebSocket numa Thread separada (Daemon).
    Não bloqueia o código principal.
    """
    t = threading.Thread(target=_thread_wrapper, daemon=True)
    t.start()

def atualizar(ax, ay, az):
    """
    Atualiza os valores que serão enviados para o dashboard.
    Deve ser chamado pelo SoloV2 sempre que chegar dado novo.
    """
    _dados_tempo_real["ax"] = float(ax)
    _dados_tempo_real["ay"] = float(ay)
    _dados_tempo_real["az"] = float(az)