import json, os
import rpyc
import time
import threading
from rpyc.utils.server import ThreadedServer
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure

# Tenta conectar ao Replica Set com retry
def connect_to_mongodb(retries=10):
    """Conecta ao MongoDB com retry"""
    for attempt in range(retries):
        try:
            client = MongoClient(
                "mongodb://mongo1:27017,mongo2:27017,mongo3:27017/",
                replicaSet="rs0",
                w="majority",
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000
            )
            # Força uma tentativa de conexão
            client.admin.command('ping')
            print(f"[SSACP] Conectado ao MongoDB Replica Set")
            return client
        except (ServerSelectionTimeoutError, ConnectionFailure) as e:
            print(f"[SSACP] Tentativa {attempt+1}/{retries} de conexão ao MongoDB falhou: {e}")
            if attempt < retries - 1:
                time.sleep(2)
    
    print(f"[SSACP] ERRO: Não conseguiu conectar ao MongoDB após {retries} tentativas")
    return None

client = connect_to_mongodb()
if client is None:
    print("[SSACP] CRÍTICO: Não há conexão com MongoDB. Encerrando...")
    exit(1)

db = client["f1"]
corridas = db["corridas"]
counters = db["counters"]

lock = threading.Lock()

# gera ID da corrida 
def next_race_id():
    doc = counters.find_one_and_update(
        {"_id": "corrida_id"},
        {"$inc": {"seq": 1}},
        return_document=True,
        upsert=True
    )
    return doc["seq"]

# obtém corrida ativa ou cria nova
def get_or_create_active_race():
    corrida = corridas.find_one({"finalizada": False})

    if corrida:
        return corrida

    # Não existe corrida ativa → cria uma nova
    novo_id = next_race_id()

    corrida = {
        "id_corrida": novo_id,
        "finalizada": False,
        "inicio": time.time(),
        "pilotos": []
    }

    corridas.insert_one(corrida)
    print(f"[SSACP] Criada corrida {novo_id}")

    return corrida

#  SSACP
class SSACP(rpyc.Service):

    def exposed_enviar_dados(self, dados_volta_json):
        """Recebe dados da volta e armazena no MongoDB"""
        try:
            info = json.loads(dados_volta_json)

            piloto = info.get("piloto", "Unknown")
            num_volta = int(info.get("volta", 0))
            curva = int(info.get("curva", 0))
            tempo = float(info.get("tempo", 0))
            pneus = info.get("pneus", {})

            with lock:
                # Pega corrida ativa (ou cria automaticamente)
                corrida = get_or_create_active_race()
                id_corrida = corrida["id_corrida"]

                # Estrutura: corridas[id].pilotos[piloto].voltas[volta] = [curvas...]
                # Tenta atualizar ou inserir dados do piloto/volta/curva
                resultado = corridas.update_one(
                    {
                        "id_corrida": id_corrida,
                        "pilotos.piloto": piloto,
                        "pilotos.voltas": {"$exists": True}
                    },
                    {
                        "$push": {
                            "pilotos.$[pilot].voltas.$[volt]": {
                                "curva": curva,
                                "tempo": tempo,
                                "pneus": pneus
                            }
                        }
                    },
                    array_filters=[
                        {"pilot.piloto": piloto},
                        {"volt": num_volta}
                    ]
                )

                # Se nenhum piloto encontrado, cria novo com primeira volta
                if resultado.matched_count == 0:
                    corridas.update_one(
                        {"id_corrida": id_corrida},
                        {
                            "$push": {
                                "pilotos": {
                                    "piloto": piloto,
                                    "voltas": {
                                        num_volta: [{
                                            "curva": curva,
                                            "tempo": tempo,
                                            "pneus": pneus
                                        }]
                                    }
                                }
                            }
                        }
                    )
                    print(f"[SSACP] Novo piloto {piloto} adicionado na corrida {id_corrida}")
                else:
                    print(f"[SSACP] Dados recebidos - Piloto: {piloto}, Volta: {num_volta}, Curva: {curva}")
            
            return True
        except json.JSONDecodeError as e:
            print(f"[SSACP] ERRO ao decodificar JSON: {e}")
            return False
        except Exception as e:
            print(f"[SSACP] ERRO ao armazenar dados: {e}")
            return False


# SERVERS
ports = [18861, 18862, 18863]

ssacp_port = int(os.getenv("PORT", "18861"))

try:
    server = ThreadedServer(SSACP, port=ssacp_port)
    print(f"[SSACP] Servidor SSACP rodando na porta {ssacp_port}")
    threading.Thread(target=server.start, daemon=True).start()
except Exception as e:
    print(f"[SSACP] ERRO ao iniciar servidor: {e}")
    exit(1)

while True:
    time.sleep(1)
