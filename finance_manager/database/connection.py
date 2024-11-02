# finance_manager/database/connection.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        # Create the appdata directory if it doesn't exist
        appdata_path = os.path.join(os.getenv("APPDATA"), "finance_manager")
        if not os.path.exists(appdata_path):
            os.makedirs(appdata_path)

        self.db_path = os.path.join(appdata_path, "finance_manager.db")
        self.engine = create_engine(f"sqlite:///{self.db_path}", echo=False)

        # Create session factory
        session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(session_factory)

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def get_session(self):
        return self.Session()

    def close_session(self):
        self.Session.remove()
