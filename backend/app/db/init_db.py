#fortuna/backend/app/db/init_db.py
def init_database():
    from .session import DatabaseConnection

    db = DatabaseConnection()
    db.create_tables()
