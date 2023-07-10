import sqlite3 
import sys,os
current_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(current_dir)
from Models.sqliteModel import SQLiteModel

class ControllerSqlite():
    def __init__(self,db,table):
        self.table_name = table
        self.sqlite_model = SQLiteModel(db_name=db)
        self.sqlite_model.connect()
        self.verify_if_table_exists()
        
    def disconnect(self,):
        self.sqlite_model.disconnect()

    def verify_if_table_exists(self):
        query = self.sqlite_model.execute_query(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.table_name}';")
        if(len(query)==0):
            self.create_table()
            
    def create_table(self):
        self.sqlite_model.execute_query(f"CREATE TABLE IF NOT EXISTS {self.table_name} (ID INTEGER PRIMARY KEY AUTOINCREMENT,MACHINE_NAME text, DATE TEXT, A REAL, V REAL, TEMPERATURE REAL)")
        print(f"Table {self.table_name} created")
        
    def insert_values(self,command,parameter):
        self.sqlite_model.execute_query(query=command,parameters=parameter)

# if __name__=="__main__":
#     obj = ControllerSqlite("DataBase/LocalData.db","DataSensors")
#     command = f"INSERT INTO DataSensors (MACHINE_NAME, DATE, A, V, TEMPERATURE) VALUES (?, ?, ?, ?, ?)"
#     parameters = ('machine2', '2023/07/06 15:48:56', '2.5', '6.0', '47')
#     print(f"parameters:{parameters}")
#     # Executar a inserção no banco de dados
#     obj.insert_values(command, parameters)