import json
import os
import time
import random

import paho.mqtt.client as mqtt
from data.dadosCurvas import pista

timeSim = 1 #Usado para acelerar os testes
tyresArray = ["Dianteira direita","Dianteira esquerda","Traseira direita","Traseira esquerda"]

class Car:
    def __init__(self, driver, team, durability):
        self.driver = driver
        self.team = team
        self.durability = float(durability)
        self.maxSpeed = 85 - (85 * self.durability)
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.connected = False
        self.connect_with_retry()
        self.client.loop_start()

    
    def connect_with_retry(self, delay=2):
     while True:
        try:
            print(f"[Car {self.driver}] Tentando conectar ao MQTT...")
            self.client.connect("mqtt-broker", 1883, 60)
            print(f"[Car {self.driver}] Conectado ao MQTT!")
            return
        except Exception as e:
            print(f"[Car {self.driver}] MQTT indisponível. Tentando novamente em {delay}s...")
            time.sleep(delay)
    
    def tyres(self):
        tyres = {}
        tyres["temperaturas(°C)"] = {}
        tyres["pressao(psi)"] = {}
        tyres["rpm"] = random.randint(int((((self.maxSpeed*3.6*1000)/2.1)*4.5/60)-300),int(((self.maxSpeed*3.6*1000)/2.1)*4.5/60))
        for t in tyresArray:
            temperatura = random.randint(80, 100)
            tyres["temperaturas(°C)"][t] = temperatura
            pressao = random.randint(17, 21)
            tyres["pressao(psi)"][t] = pressao
        return tyres
            

    def on_connect(self, client, userdata, connect_flags, rc, properties=None):
        if rc == 0:
            print(f"[Car {self.driver}] Conectado ao broker MQTT!")
            self.connected = True
        else:
            print(f"[Car {self.driver}] Falha na conexão. Código: {rc}")
            self.connected = False

    def wait_for_connection(self, timeout=10):
        """Aguarda a conexão MQTT estar pronta"""
        start = time.time()
        while not self.connected:
            if time.time() - start > timeout:
                print(f"[Car {self.driver}] AVISO: Timeout aguardando MQTT, continuando mesmo assim...")
                return
            time.sleep(0.1)
        print(f"[Car {self.driver}] MQTT pronto para publicar")

    def race(self):
        """Executa a corrida do carro"""
        # Aguarda MQTT estar conectado antes de iniciar
        self.wait_for_connection()
        
        print(f"[Car {self.driver}] Iniciando corrida - Equipe: {self.team}, Durabilidade: {self.durability}")
        for volta in range(1, 6):
            for c in pista:
                curva = {}
                tempo = (volta*0.1) + ( c["distancia"]) / (self.maxSpeed * c["deltaVelocidade"])
                curva["piloto"] = self.driver
                curva["equipe"] = self.team
                curva["volta"] = volta
                curva["curva"] = c["curva"]
                curva["tempo"] = round(tempo, 3)
                curva["pneus"] = self.tyres()
                data_json = json.dumps(curva, ensure_ascii=False)
                time.sleep(tempo * timeSim)
                try:
                    self.client.publish(f"isccp/{c['curva']}", data_json)
                except Exception as e:
                    print(f"[Car {self.driver}] ERRO ao publicar na curva {c['curva']}: {e}")
        
        print(f"[Car {self.driver}] Corrida finalizada!")
        # Encerra o loop MQTT e desconecta
        self.client.loop_stop()
        self.client.disconnect()


# Lê variáveis de ambiente do docker-compose.yml
driver = os.getenv("DRIVER", "Unknown Driver")
team = os.getenv("TEAM", "Unknown Team")
durability = os.getenv("DURABILITY", "0.1")

# Cria e inicia a corrida do carro
car = Car(driver, team, durability)
car.race()