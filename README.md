# Interlagos Data Dashboard

Dashboard em tempo real para visualização de dados de telemetria de corridas no Autódromo de Interlagos.

## 📋 Descrição do Projeto

Sistema distribuído que coleta, armazena e visualiza dados de telemetria de 24 pilotos durante corridas de Fórmula 1 no circuito de Interlagos. O projeto implementa uma arquitetura cliente-servidor com comunicação RPC (Remote Procedure Call) e streaming de dados em tempo real via Server-Sent Events (SSE).

### Componentes Principais

- **CAR (Cliente de Aquisição de Dados)**: Sistema embarcado nos carros que coleta dados de telemetria (temperatura e pressão dos pneus, RPM, tempos de volta e curva) e envia via MQTT
- **ISCCP (Interface de Serviços de Consulta de Corridas de Pilotos)**: Broker MQTT que recebe dados dos carros e encaminha via RPC para o SSACP
- **SSACP (Servidor de Serviços de Armazenamento de Corridas de Pilotos)**: Servidor RPC que recebe dados do ISCCP e armazena no banco de dados distribuído
- **MongoDB Distribuído**: Banco de dados NoSQL distribuído para armazenamento de telemetria
- **Dashboard Web**: Interface Next.js com React que consulta o MongoDB e visualiza os dados em tempo real

## 🏗️ Arquitetura

```
┌─────────────┐
│   CAR (x24) │──────┐
└─────────────┘      │
                     │ MQTT
┌─────────────┐      │
│   CAR (x24) │──────┼──────► ┌────────────┐
└─────────────┘      │        │   ISCCP    │
                     │        │ (Broker)   │
┌─────────────┐      │        └────────────┘
│   CAR (x24) │──────┘               │
└─────────────┘                      │ RPC (rpyc)
                                     ▼
                              ┌────────────┐      ┌──────────────────┐
                              │   SSACP    │◄────►│    MongoDB       │
                              │  (Python)  │      │  (Distribuído)   │
                              └────────────┘      └──────────────────┘
                                                           │
                                                           │ Consultas
                                                           ▼
                                                    ┌────────────┐
                                                    │ Dashboard  │
                                                    │   React    │
                                                    └────────────┘
```

## 🚀 Tecnologias Utilizadas

### Backend

- **Python 3.x**: Linguagem para os serviços CAR e SSACP
- **MQTT**: Protocolo de mensageria para comunicação entre CAR e ISCCP
- **rpyc**: Framework para comunicação RPC entre ISCCP e SSACP
- **MongoDB Distribuído**: Banco de dados NoSQL distribuído para armazenamento de telemetria
- **pymongo**: Driver Python para MongoDB

### Frontend

- **Next.js 14**: Framework React com App Router
- **TypeScript**: Tipagem estática para maior segurança
- **Tailwind CSS**: Estilização utilitária
- **Server-Sent Events (SSE)**: Streaming de dados em tempo real

### DevOps

- **Docker & Docker Compose**: Containerização e orquestração dos serviços

## 📁 Estrutura do Projeto

```
interlagos-data-dashboard/
├── docker-compose.yml           # Orquestração dos containers
├── next-dashboard/              # Frontend Next.js
│   ├── app/
│   │   ├── api/                # API Routes (ISCCP)
│   │   │   └── corridas/
│   │   │       ├── route.ts    # Endpoint REST
│   │   │       └── realtime/
│   │   │           └── route.ts # Endpoint SSE
│   │   ├── components/
│   │   │   ├── Header.tsx
│   │   │   ├── PilotosListClient.tsx    # Visualização individual
│   │   │   └── TodosPilotosClient.tsx   # Grid com todos pilotos
│   │   ├── pilotos/
│   │   │   └── page.tsx        # Rota /pilotos
│   │   └── page.tsx            # Rota / (home)
│   └── libs/
│       └── api.ts              # Cliente SSE e fetch
└── python-backend/
    ├── car/                    # Sistema embarcado dos carros
    │   ├── car.py             # Cliente RPC que envia telemetria
    │   └── data/
    │       └── curvascalculadas.csv
    └── ssacp/
        └── ssacp.py           # Servidor RPC + MongoDB
```

## 🏁 Funcionalidades

### Visualização Individual

- Seleção de piloto via dropdown
- Exibição de todas as voltas (1-5) e curvas (1-15)
- Cards com informações detalhadas de cada curva:
  - Tempo de curva
  - Temperatura e pressão dos 4 pneus (DD, DE, TD, TE)
  - RPM do motor
- Atualização em tempo real via SSE (100ms)

### Visualização de Todos os Pilotos

- Grid com 24 cards (um por piloto)
- Informação da última curva completada
- Dados da volta atual
- Pré-renderização dos cards para melhor UX
- Acumulação incremental de dados

### Backend

- Armazenamento atômico no MongoDB (operações thread-safe)
- Reuso de corridas ativas (evita duplicação)
- Estrutura de dados otimizada:
  - 1 documento de corrida por sessão
  - 24 pilotos por corrida
  - 5 voltas × 15 curvas por piloto

## 🎯 Dados de Telemetria

Cada curva captura:

- **Tempo**: Duração para completar a curva (segundos)
- **Pneus**:
  - Temperatura (°C) para cada pneu
  - Pressão (PSI) para cada pneu
- **RPM**: Rotações por minuto do motor
- **Metadata**: Número da volta, número da curva, piloto, equipe

## 🔄 Fluxo de Dados

1. **CAR** lê dados do arquivo CSV com telemetria calculada
2. **CAR** publica dados via **MQTT** para o **ISCCP**
3. **ISCCP** recebe mensagens MQTT e encaminha via **RPC** para o **SSACP** (porta 18861)
4. **SSACP** armazena no **MongoDB Distribuído** usando operações atômicas
5. **Dashboard** consulta o **MongoDB** via SSE
6. **ISCCP** busca dados do **MongoDB** a cada 100ms
7. **Dashboard** atualiza a UI em tempo real

## 🐳 Execução com Docker

```bash
# Subir todos os serviços
docker-compose up -d

# Verificar logs
docker logs -f <container-name>

# Parar serviços
docker-compose down
```

### Portas

- **3000**: Dashboard Next.js
- **27017**: MongoDB
- **18861**: SSACP (RPC)

## 🛠️ Desenvolvimento Local

### Frontend

```bash
cd next-dashboard
npm install
npm run dev
```

### Backend Python

```bash
cd python-backend/ssacp
pip install -r requirements.txt
python ssacp.py
```

### CAR (Simulação)

```bash
cd python-backend/car
pip install -r requirements.txt
python car.py
```

## 📊 Modelo de Dados

### Estrutura MongoDB

```javascript
{
  id_corrida: 1,
  pilotos: [
    {
      piloto: "Oscar Piastri",
      equipe: "McLaren",
      voltas: {
        "1": [
          {
            curva: 1,
            tempo: 12.5,
            pneus: {
              "temperaturas(°C)": {
                "Dianteira direita": 85,
                "Dianteira esquerda": 83,
                "Traseira direita": 90,
                "Traseira esquerda": 88
              },
              "pressao(psi)": {
                "Dianteira direita": 24,
                "Dianteira esquerda": 24,
                "Traseira direita": 22,
                "Traseira esquerda": 22
              },
              "rpm": 15000
            }
          },
          // ... curvas 2-15
        ],
        // ... voltas 2-5
      }
    },
    // ... 23 pilotos restantes
  ]
}
```

## 🎨 Interface

- **Design**: Clean e moderno com Tailwind CSS
- **Responsividade**: Grid adaptativo
- **Interatividade**: Hover para detalhes completos
- **Navegação**: Header fixo com botões para alternar entre visões
- **Performance**: Pre-renderização e atualização incremental

## 📝 Notas Técnicas

- MongoDB opera com operações atômicas (`$push`, `$setOnInsert`)
- Next.js com App Router e componentes Server/Client estratégicos
- Sistema previne criação de múltiplas corridas usando `find_one(sort=[("id_corrida", -1)])`

## 👥 Autores

Projeto desenvolvido por Luís Carlos como prática de Sistemas Distribuídos - IFMG
