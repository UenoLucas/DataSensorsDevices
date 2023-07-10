import sqlite3

class SQLiteModel:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()
            print("Connected with the database")
        except:
            print("Error to connect with db")
            
    def disconnect(self):
        self.cursor.close()
        self.connection.close()

    def execute_query(self, query, parameters=None):
        if parameters:
            self.cursor.execute(query, parameters)
        else:
            self.cursor.execute(query)
        self.connection.commit()
        if query.lower().startswith("select"):
            return self.cursor.fetchall()

    def fetch_all_rows(self):
        return self.cursor.fetchall()

    def fetch_one_row(self):
        return self.cursor.fetchone()
