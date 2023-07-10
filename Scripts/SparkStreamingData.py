import sys,os
current_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(current_dir)
import json
import findspark
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext
from pyspark.sql.types import StructType, StringType
from pyspark.sql.functions import from_json
from Controllers.sqliteController import ControllerSqlite

class KafkaStreaming:
    def __init__(self):
        with open("Scripts/config.json", "r") as file:
            json_file = json.load(file)
        try:
            obj_kafka = json_file["kafka"]
            self.host_kafka = obj_kafka["host_kafka"]
            self.topic = obj_kafka["topic"]
            json_obj_sqlite = json_file["db"]
            self.db = json_obj_sqlite["filepath_db"]
            self.table = json_obj_sqlite["table_name"]
        except Exception as e:
            print("problem to read json: " + str(e))
           
    def start_streaming(self):
        def update_sqlite(df, epoch_id):
            obj_sqlite = ControllerSqlite(db=self.db,table=self.table)
            # Extrair os dados da linha
            rows = df.collect()
            for row in rows:
                machine = row.Machine
                current = row.A
                voltage = row.V
                temperature = row.Temperature
                date = row.Date

                # Construir o comando SQL para inserção
                command = f"INSERT INTO DataSensors (MACHINE_NAME, DATE, A, V, TEMPERATURE) VALUES (?, ?, ?, ?, ?)"
                parameters = (machine, date, current, voltage, temperature)
                print(f"parameters: {parameters}")

                # Executar a inserção no banco de dados
                obj_sqlite.insert_values(command, parameters)
                print("insert values in sqlite")
                
        try:
            spark = SparkSession.builder.appName("KafkaStreaming").getOrCreate()

            # Configurar as propriedades do Kafka        
            schema = StructType()\
                                .add("Machine",StringType())\
                                .add("A", StringType()) \
                                .add("V", StringType()) \
                                .add("Temperature", StringType()) \
                                .add("Date", StringType())

            # Ler o stream do Kafka
            df = spark.readStream.format("kafka") \
                .option("kafka.bootstrap.servers", self.host_kafka) \
                .option("subscribe", self.topic) \
                .load()

            # Converter a coluna "value" para o tipo JSON com base no esquema
            df = df.withColumn("jsonData", from_json(df["value"].cast("string"), schema))

            # Selecionar as colunas relevantes
            df = df.select("jsonData.Machine","jsonData.A", "jsonData.V", "jsonData.Temperature", "jsonData.Date")

            query = df.writeStream.option("truncate", 'false').outputMode("append").trigger(processingTime='3 seconds').foreachBatch(update_sqlite).start()  # Use o método update_interface para atualizar a interface
            
            query.awaitTermination()
        except Exception as e:
            print(f"error: {e}")

if __name__ == "__main__":
    kafka_streaming = KafkaStreaming()
    kafka_streaming.start_streaming()

