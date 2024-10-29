import sqlite3
import os
from pathlib import Path


class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        appdata_path = os.path.join(os.getenv("APPDATA"), "finance_manager")
        if not os.path.exists(appdata_path):
            os.makedirs(appdata_path)

        self.db_path = os.path.join(appdata_path, "finance_manager.db")

        if not os.path.exists(self.db_path):
            from .models import init_database

            init_database(self.db_path)

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def execute_query(self, query, parameters=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor

    def execute_many(self, query, parameters):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, parameters)
            conn.commit()
            return cursor

    def fetch_one(self, query, parameters=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)
            return cursor.fetchone()

    def fetch_all(self, query, parameters=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)
            return cursor.fetchall()
