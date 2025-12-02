import json
import os
import time
import random

import paho.mqtt.client as mqtt
from data.dadosCurvas import pista
import sys

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
    
    def connect_with_retry(self, max_retries=10, delay=2):
        """Conecta ao MQTT broker com retry"""
        for attempt in range(1, max_retries + 1):
            try:
                print(f"[Car {self.driver}] Tentando conectar ao MQTT (tentativa {attempt}/{max_retries})...")
                self.client.connect("mqtt-broker", 1883, 60)
                return
            except Exception as e:
                if attempt == max_retries:
                    print(f"[Car {self.driver}] ERRO: Falha ao conectar após {max_retries} tentativas: {e}")
                    sys.exit(1)
                print(f"[Car {self.driver}] Conexão recusada, aguardando {delay}s... ({attempt}/{max_retries})")
                time.sleep(delay)
    
    def tyres(self):
        tyres = {}
        tyres["temperaturas(°C)"] = {}
        tyres["pressao(psi)"] = {}
        tyres["rpm"] = int(((self.maxSpeed*3.6*1000)/2.1)*4.5/60)
        for t in tyresArray:
            temperatura = random.randint(80, 100)
            tyres["temperaturas(°C)"][t] = temperatura
            pressao = random.randint(17, 21)
            tyres["pressao(psi)"][t] = pressao
        return tyres
            

    def on_connect(self, client, userdata, connect_flags, rc, properties=None):
        if rc == 0:
            print(f"[Car {self.driver}] Conectado ao broker MQTT!")
        else:
            print(f"[Car {self.driver}] Falha na conexão. Código: {rc}")


    def race(self):
        """Executa a corrida do carro"""
        print(f"[Car {self.driver}] Iniciando corrida - Equipe: {self.team}, Durabilidade: {self.durability}")
        for volta in range(1, 11):
            for c in pista:
                curva = {}
                tempo = c["distancia"] / (self.maxSpeed * c["deltaVelocidade"])
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


# Lê variáveis de ambiente do docker-compose.yml
driver = os.getenv("DRIVER", "Unknown Driver")
team = os.getenv("TEAM", "Unknown Team")
durability = os.getenv("DURABILITY", "0.1")

# Cria e inicia a corrida do carro
car = Car(driver, team, durability)
car.race()