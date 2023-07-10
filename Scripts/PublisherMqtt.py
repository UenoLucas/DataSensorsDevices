import sys
import os
current_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir,"Scripts"))
sys.path.append(os.path.join(current_dir,"Controllers"))
sys.path.append(os.path.join(current_dir,"Models"))
import argparse
from Controllers.mqttPublisherController import MqttPublisherController
import json
import datetime
import time
import math
import random

class PowerMachineSimulation:
    def __init__(self):
        self.amplitude_current = 10.0
        self.frequency_current = 1.0

        self.amplitude_voltage = 100.0
        self.frequency_voltage = 2.0

    def current_function(self, i):
        # Simulação de corrente senoidal com ruído
        amplitude_noise = 1.0
        noise = amplitude_noise * (2 * random.random() - 1)  # Ruído aleatório entre -amplitude_noise e amplitude_noise

        current = self.amplitude_current * math.sin(2 * math.pi * self.frequency_current * i) + noise
        return round(current, 4)

    def voltage_function(self, i):
        # Simulação de tensão triangular com ruído
        amplitude_noise = 10.0
        noise = amplitude_noise * (2 * random.random() - 1)  # Ruído aleatório entre -amplitude_noise e amplitude_noise

        period = 1 / self.frequency_voltage
        t = i % period  # Tempo dentro do período
        if t < period / 2:
            voltage = 2 * self.amplitude_voltage * (t / (period / 2)) - self.amplitude_voltage + noise
        else:
            voltage = -2 * self.amplitude_voltage * ((t - period / 2) / (period / 2)) + self.amplitude_voltage + noise
        return round(voltage, 3)

    def temperature_function(self,):
        return  random.randint(60,90)
    
class Publish_Data():
    def __init__(self, machine_name= ""):
        with open("Scripts/config.json", "r") as file:
            json_file = json.load(file)
        try:
            object_mqtt = json_file["mqtt"]
            self.adress_broker = object_mqtt["address"]
            self.port = object_mqtt["port"]
            self.topic = object_mqtt["topic"]        
            self.machine_name = machine_name
        except Exception as e:
            print("problem to read json:"+e.args)
        self.mqtt_object = MqttPublisherController(self.adress_broker,self.port,self.topic)
        self.power_data = PowerMachineSimulation()
        pass

    
    def send_data(self,):
        self.mqtt_object.connect()
        i = 1
        char = "/"
        original_char=char
        while(True):
            current = self.power_data.current_function(i)
            tension = self.power_data.voltage_function(i)
            temperature = self.power_data.temperature_function()
            datetime_now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            obj = {"Machine":self.machine_name,"A":current,"V":tension,"Temperature":temperature,"Date":datetime_now}
            self.mqtt_object.publish_message(json.dumps(obj))
            sys.stdout.write(f"\rData rows sent: {i} {char}")
            sys.stdout.flush()
            i += 1
            if i%2==0:
                char="\\"
            else:
                char="/"
            time.sleep(3)
            
if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Publish data script")
    parser.add_argument("--machine", type=str, help="Machine name")
    args = parser.parse_args()
    obj = Publish_Data(machine_name=args.machine)
    try:
        obj.send_data()
    except Exception as ex:
        print(f"Error: {ex}")
    pass
