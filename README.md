# 🛰️ CubeSat Ground Station Dashboard (SoloGrafana)

Este projeto implementa uma **Estação de Solo (Ground Station)** moderna e escalável para monitorização de telemetria de CubeSats. Utiliza uma arquitetura baseada em microsserviços para capturar, armazenar e visualizar dados críticos de missão em tempo real.

![Dashboard Preview](https://via.placeholder.com/800x400?text=Dashboard+Grafana+Preview)
*(Substitua este link por um print real do seu dashboard)*

## 📋 Funcionalidades

* **Ingestão de Dados em Tempo Real:** Captura pacotes de telemetria via Serial (Rádio/USB).
* **Armazenamento de Séries Temporais:** Uso do **InfluxDB** para alta performance na gravação de dados históricos.
* **Visualização Profissional:** Dashboard no **Grafana** com taxa de atualização de até 10Hz (100ms).
* **Multi-Missão:** Suporte para filtrar e comparar dados de diferentes lançamentos/testes.
* **Simulação de Hardware:** Inclui código Arduino para emular o satélite e sensores (MPU6050).
* **Backup Local:** Gravação simultânea de ficheiros `.csv` brutos para redundância.

## 🛠️ Arquitetura do Sistema

O fluxo de dados segue o padrão da indústria aeroespacial "New Space":

1. **CubeSat/Arduino:** Envia pacotes de telemetria (String formatada) via Rádio ou Serial.
2. **Python Gateway (`SoloV1.py` e `SoloV2.py`):**
   * Lê a porta Serial.
   * Decodifica o protocolo (Parse).
   * Salva em CSV local (`/launches`).
   * Envia para o banco de dados via API.
3. **InfluxDB (Docker):** Armazena os dados com tags (Missão, Satélite).
4. **Grafana (Docker):** Consulta o banco e renderiza os gráficos para o operador.

## 🚀 Pré-requisitos

* **Python 3.8+**
* **Docker** e **Docker Compose**
* **Arduino IDE** (para carregar o código no hardware)

## 📦 Instalação e Configuração

### 1. Preparar o Ambiente (Docker)
Na raiz do projeto, onde está o ficheiro `docker-compose.yml`, suba os serviços:

```bash
docker-compose up -d
```

* **Grafana:** Acessível em http://localhost:3000
* **InfluxDB:** Acessível em http://localhost:8086

### 2. Configurar o Banco de Dados
1. Aceda a http://localhost:8086.
2. Crie uma organização (ex: `cubesat_team`) e um bucket (ex: `telemetria`).
3. Gere um API Token (com permissão de leitura/escrita).
4. Copie este Token.

### 3. Configurar o Python
Crie um ambiente virtual para isolar as dependências:

```bash
# Criar e ativar venv
python -m venv venv

# Windows:
.\venv\Scripts\Activate
# Linux/Mac:
source venv/bin/activate

# Instalar bibliotecas
pip install -r requirements.txt
```

### 4. Configurar o Script da Estação
Edite o ficheiro `influxDBtoken.txt` e adicione o seu token do InfluxDB.

Configure as variáveis no script Python (`SoloV1.py` ou `SoloV2.py`):

```python
INFLUX_TOKEN = "SEU_TOKEN_AQUI"  # ou lido do arquivo influxDBtoken.txt
INFLUX_ORG = "cubesat_team"
INFLUX_BUCKET = "telemetria"
NOME_MISSAO = "Teste_Bancada_01"  # Mude a cada novo teste
```

## 🎮 Como Usar

### Passo A: O Hardware (Satélite/Emulador)
1. Conecte o Arduino (Nano/Uno) ao computador.
2. Se estiver a usar o MPU6050, faça as conexões I2C (SDA->A4, SCL->A5).
3. Carregue o código `simulacao.ino` ou `simulacao2.ino` (disponível nas pastas `/simulacao`).
4. Verifique qual porta COM foi atribuída (ex: COM3 ou /dev/ttyUSB0).

### Passo B: A Estação de Solo
Execute o script Python:

```bash
python SoloV1.py
# ou
python SoloV2.py
```

Se tudo estiver correto, verá logs como: `✅ Conectado ao Dashboard` e `Dados enviados: Bat=98%`.

### Passo C: O Dashboard (Grafana)
1. Aceda a http://localhost:3000 (Login: admin / admin).
2. Configure a Data Source selecionando InfluxDB (Linguagem: Flux).
3. Importe ou crie os painéis conforme documentado na Wiki do projeto.

## 📊 Estrutura do Dashboard

O painel de controlo foi desenhado com 3 níveis de informação:

| Nível | Descrição | Visualizações Chave |
|-------|-----------|-------------------|
| **1. Sinais Vitais** | Status imediato da saúde do satélite. | • Heartbeat (Último Contacto)<br>• GPS Lock Status<br>• Bateria (Gauge)<br>• RSSI (Sinal) |
| **2. Missão** | Consciência situacional e navegação. | • Mapa Mundi (Rastreio 3D)<br>• Perfil de Voo (Altitude vs Pressão) |
| **3. Engenharia** | Diagnóstico profundo dos subsistemas. | • Estabilidade (Vibração/G-Force)<br>• Acelerometria (3 Eixos)<br>• Eficiência do Link (Pacotes/min) |

## 📂 Estrutura de Ficheiros

```
/
├── docker-compose.yml      # Orquestração dos contentores (Banco + Grafana)
├── SoloV1.py              # Script principal da Estação de Solo (Versão 1)
├── SoloV2.py              # Script principal da Estação de Solo (Versão 2)
├── requirements.txt        # Dependências Python
├── influxDBtoken.txt      # Token de acesso ao InfluxDB
├── README.md              # Documentação
├── .gitignore             # Arquivos ignorados pelo Git
├── /data                  # Dados de telemetria em formato JSONL
│   ├── telemetry.jsonl
│   └── telemetrycopy.jsonl
├── /simulacao             # Código Arduino para simulação
│   └── simulacao.ino
├── /simulacao2            # Código Arduino alternativo
│   └── simulacao2.ino
├── /launches              # (Gerado automaticamente) Logs CSV brutos
│   ├── Bat1.csv ... Bat32.csv  # Dados de bateria
│   └── Tel1.csv ... Tel32.csv  # Dados de telemetria
└── /videoTeste            # Pasta para testes de vídeo (ignorada pelo Git)
```

## 🔧 Versões do Software

### SoloV1.py vs SoloV2.py
- **SoloV1.py:** Versão inicial do sistema de telemetria
- **SoloV2.py:** Versão aprimorada com melhorias de performance e funcionalidades adicionais

### Códigos de Simulação
- **simulacao.ino:** Emulador básico do CubeSat
- **simulacao2.ino:** Versão melhorada do emulador com mais sensores

## 🔍 Dados Suportados

O sistema captura e processa os seguintes tipos de telemetria:

* **Bateria (Bat):** Tensão e percentual de carga
* **Telemetria (Tel):** Dados gerais dos sensores
* **GPS:** Coordenadas e altitude
* **IMU:** Acelerômetro, giroscópio e magnetômetro
* **Ambientais:** Temperatura, pressão e humidade

## 🤝 Contribuição

Para adicionar novas funcionalidades:

1. Crie uma branch para a sua modificação (`git checkout -b feature/novo-sensor`).
2. No InfluxDB, adicione o novo campo `.field("novo_sensor", valor)` no script Python.
3. Atualize o ficheiro `docker-compose.yml` se adicionar novos serviços.
4. Teste thoroughly antes de submeter um pull request.

## 📝 Licença

Este projeto é open source e está disponível sob a licença MIT.

---

**Desenvolvido para Missões CubeSat Open Source. 🚀**

*Para mais informações, consulte a documentação técnica ou abra uma issue no repositório.*