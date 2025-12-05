import paho.mqtt.client as mqtt
import os
import json
import rpyc
import time
import threading
from queue import Queue

lock = threading.Lock()

class ISCCP:
    def __init__(self, isccp_id, rpyc_host, rpyc_port):
        self.id = isccp_id
        self.proxy = None
        self.rpyc_host = rpyc_host
        self.rpyc_port = rpyc_port
        self.pending_queue = Queue()  # Fila para dados pendentes
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("mqtt-broker", 1883, 60)
        self.client.loop_start()
        
        # Inicia thread de reconexão contínua ao SSACP
        self.reconnect_thread = threading.Thread(target=self.background_reconnect, daemon=True)
        self.reconnect_thread.start()
    
    def background_reconnect(self):
        """Thread contínua que tenta reconectar ao SSACP a cada 5 segundos"""
        while True:
            if self.proxy is None:
                try:
                    self.proxy = rpyc.connect(self.rpyc_host, self.rpyc_port)
                    print(f"[ISCCP {self.id}] Conectado ao SSACP em {self.rpyc_host}:{self.rpyc_port}")
                    # Processa dados pendentes na fila
                    self.flush_pending_queue()
                except Exception as e:
                    print(f"[ISCCP {self.id}] Tentando reconectar ao SSACP: {e}")
                    time.sleep(5)
            else:
                # Se já está conectado, verifica a cada 10s
                time.sleep(10)
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"[ISCCP {self.id}] Conexão efetuada ao broker MQTT")
            client.subscribe(f"isccp/{self.id}")
        else:
            print(f"[ISCCP {self.id}] Falha na conexão, code {rc}")
        

    def on_message(self, client, userdata, msg):
        with lock:
            print(f"recebido em isccp/{self.id}: {msg.payload.decode()}")
            dados = json.loads(msg.payload.decode())
            self.armazenar_dados(dados)

    def armazenar_dados(self, data):

        if self.proxy is None:
            print(f"[ISCCP {self.id}] SSACP offline - adicionando à fila (tamanho: {self.pending_queue.qsize() + 1})")
            self.pending_queue.put(data)
            return
        
        try:
            self.proxy.root.enviar_dados(json.dumps(data))
            print(f"[ISCCP {self.id}] Enviado para SSACP com sucesso!\n")
        except Exception as e:
            print(f"[ISCCP {self.id}] ERRO ao enviar para SSACP: {e} - adicionando à fila\n")
            self.pending_queue.put(data)
            self.proxy = None

    def flush_pending_queue(self):
        queue_size = self.pending_queue.qsize()
        if queue_size == 0:
            return
        
        print(f"[ISCCP {self.id}] Processando {queue_size} dados pendentes...")
        success_count = 0
        
        while not self.pending_queue.empty():
            try:
                data = self.pending_queue.get_nowait()
                self.proxy.root.enviar_dados(json.dumps(data))
                success_count += 1
            except Exception as e:
                print(f"[ISCCP {self.id}] ERRO ao processar fila: {e}")
                # Recoloca o dado na fila
                self.pending_queue.put(data)
                self.proxy = None
                break
        
        print(f"[ISCCP {self.id}] Fila processada: {success_count}/{queue_size} enviados com sucesso\n")


# Lê variáveis de ambiente
isccp_id = int(os.getenv("ID", "1"))
isccp_port = int(os.getenv("PORT", "18861"))
isccp_host = os.getenv("HOST", "ssacp1")

# Inicia ISCCP
isccp = ISCCP(isccp_id=isccp_id, rpyc_host=isccp_host, rpyc_port=isccp_port)

while True:
    time.sleep(1)
