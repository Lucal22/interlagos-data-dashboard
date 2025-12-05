import json, os
import rpyc
import time
import threading
from rpyc.utils.server import ThreadedServer
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure

# Tenta conectar ao Replica Set com retry
def connect_to_mongodb(retries=10):
    for attempt in range(retries):
        try:
            client = MongoClient(
                "mongodb://mongo1:27017,mongo2:27017,mongo3:27017/",
                replicaSet="rs0",
                w="majority",
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000
            )
            client.admin.command('ping')
            print(f"[SSACP] Conectado ao MongoDB Replica Set")
            return client
        except (ServerSelectionTimeoutError, ConnectionFailure) as e:
            print(f"[SSACP] Tentativa {attempt+1}/{retries} falhou: {e}")
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

def next_race_id():
    doc = counters.find_one_and_update(
        {"_id": "corrida_id"},
        {"$inc": {"seq": 1}},
        return_document=True,
        upsert=True
    )
    return doc["seq"]

def get_or_create_active_race():
    
    # Busca a corrida mais recente
    ultima_corrida = corridas.find_one(sort=[("id_corrida", -1)])
    
    if ultima_corrida:
        print(f"[SSACP] Usando corrida existente {ultima_corrida['id_corrida']}")
        return ultima_corrida
    
    # Se não houver, cria uma nova
    novo_id = next_race_id()
    corrida = corridas.find_one_and_update(
        {"id_corrida": novo_id},
        {
            "$setOnInsert": {
                "id_corrida": novo_id,
                "inicio": time.time(),
                "pilotos": []
            }
        },
        upsert=True,
        return_document=True
    )

    print(f"[SSACP] Corrida {corrida['id_corrida']} criada")
    return corrida

active_race = get_or_create_active_race()
print(f"[SSACP] Corrida ativa garantida antes do servidor iniciar.")

class SSACP(rpyc.Service):
    def exposed_enviar_dados(self, dados_volta_json):
        try:
            info = json.loads(dados_volta_json)

            piloto_nome = info.get("piloto", "Unknown")
            equipe = info.get("equipe")
            num_volta = str(info.get("volta"))
            curva = int(info.get("curva", 0))
            tempo = float(info.get("tempo", 0))
            pneus = info.get("pneus", {})

            corrida = get_or_create_active_race()
            id_corrida = corrida["id_corrida"]

            corrida = corridas.find_one({"id_corrida": id_corrida})
            pilotos = corrida.get("pilotos", [])

            idx = next((i for i, p in enumerate(pilotos) if p["piloto"] == piloto_nome), None)

            if idx is None:
                novo = {
                    "piloto": piloto_nome,
                    "voltas": {
                        num_volta: [{
                            "curva": curva,
                            "tempo": tempo,
                            "pneus": pneus
                        }]
                    }
                }
                if equipe:
                    novo["equipe"] = equipe

                corridas.update_one(
                    {"id_corrida": id_corrida},
                    {"$push": {"pilotos": novo}}
                )

                print(f"[SSACP] NOVO piloto {piloto_nome} - Volta {num_volta} Curva {curva}")
                return True

            piloto_doc = pilotos[idx]

            # Verifica se a volta existe, senão inicializa
            if "voltas" not in piloto_doc or num_volta not in piloto_doc.get("voltas", {}):
                corridas.update_one(
                    {"id_corrida": id_corrida, "pilotos.piloto": piloto_nome},
                    {"$set": {f"pilotos.$.voltas.{num_volta}": []}}
                )
            
            corridas.update_one(
                {"id_corrida": id_corrida, "pilotos.piloto": piloto_nome},
                {"$push": {f"pilotos.$.voltas.{num_volta}": {
                    "curva": curva,
                    "tempo": tempo,
                    "pneus": pneus
                }}}
            )
            
            if equipe:
                corridas.update_one(
                    {"id_corrida": id_corrida, "pilotos.piloto": piloto_nome},
                    {"$set": {"pilotos.$.equipe": equipe}}
                )

            return True

        except Exception as e:
            print(f"[SSACP] ERRO armazenamento: {e}")
            return False

ssacp_port = int(os.getenv("PORT", "18861"))

try:
    server = ThreadedServer(SSACP, port=ssacp_port)
    print(f"[SSACP] Servidor rodando na porta {ssacp_port}")
    threading.Thread(target=server.start, daemon=True).start()
except Exception as e:
    print(f"[SSACP] ERRO ao iniciar servidor: {e}")
    exit(1)

while True:
    time.sleep(1)
