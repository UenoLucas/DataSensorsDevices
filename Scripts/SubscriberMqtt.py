import json
import os,sys
current_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(current_dir)
from Models.mqttModel import MqttModel
from Controllers.sqliteController import ControllerSqlite
from kafka import KafkaProducer

class Subscriber():
    def __init__(self,):
        # open json file with some configurations
        with open("Scripts/config.json", "r") as file:
            json_file = json.load(file)
        try:
            object_mqtt = json_file["mqtt"]
            adress_broker = object_mqtt["address"]
            port = object_mqtt["port"]
            topic = object_mqtt["topic"]
            object_db = json_file["db"]
            self.table_name = object_db["table_name"]
            self.fp_database = object_db["filepath_db"]
            object_kafka = json_file["kafka"]
            self.host_kafka = object_kafka["host_kafka"]
            self.topic_kafka = object_kafka["topic"]
        except Exception as e:
            print(f"problem to read json: {e}")
            
        # objeto e conexão com banco sqlite
        try:            
            fp_database = os.path.join(current_dir,"DataBase","LocalData.db")
            self.obj_sqlite = ControllerSqlite(fp_database,self.table_name)
        except Exception as ex:
            print(f"Error with Sqlite object:{ex}")

        # Configuração do Kafka
        try:    
            self.kafka_producer = KafkaProducer(bootstrap_servers=self.host_kafka)
        except Exception as ex:
            print(f"Error configuring Kafka producer: {ex}")
            
        # conexão mqtt
        try:
            self.mqtt_model = MqttModel(broker= adress_broker,port = port, topic = topic)
            self.mqtt_model.connect()
            self.mqtt_model.client.subscribe(topic)
            self.mqtt_model.client.on_message = self.handle_message
            self.start_received_messages()
        except Exception as ex:
            print(f"Error with Mqtt object:{e}")
        
    # method to start to receive messages
    def start_received_messages(self):
        try:
            self.mqtt_model.client.loop_forever()
        except:
            self.mqtt_model.disconnect()
            
    #method to insert in localdata the messages from mqtt broker
    def insert_in_db(self, data):
        query = f"INSERT INTO {self.table_name} (Date, A, V, Temperature) VALUES (?,?,?,?)"
        parameters = (data["Date"],data["A"], data["V"], data["Temperature"])
        try:
            self.obj_sqlite.insert_values(query, parameters)
        except Exception as ex:
            print(f"Error to insert data: {ex}")

    # Método para enviar mensagem para o Kafka
    def send_to_kafka(self, message):
        try:
            self.kafka_producer.send(self.topic_kafka, value=message.encode())
            self.kafka_producer.flush()
            print(f"Sent message to Kafka: {message}")
        except Exception as ex:
            print(f"Error sending message to Kafka: {ex}")
            
    def handle_message(self, client, userdata, msg):
        message = msg.payload.decode()
        data = json.loads(message)
        self.send_to_kafka(message)
        # self.insert_in_db(data)
        # print(message)

        
if __name__ == "__main__":
    obj_sub = Subscriber()
        
