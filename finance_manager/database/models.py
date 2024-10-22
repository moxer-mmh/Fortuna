from datetime import datetime
import sqlite3


def init_database(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.executescript(
        """
    CREATE TABLE IF NOT EXISTS accounts (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        balance REAL NOT NULL
    );

    CREATE TABLE IF NOT EXISTS categories (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        budget REAL NOT NULL,
        type TEXT NOT NULL  -- 'expense' or 'income'
    );

    CREATE TABLE IF NOT EXISTS transactions (
        id TEXT PRIMARY KEY,
        date TEXT NOT NULL,
        amount REAL NOT NULL,
        description TEXT,
        account_id TEXT NOT NULL,
        category_id TEXT NOT NULL,
        type TEXT NOT NULL,  -- 'expense', 'income', or 'subscription'
        subscription_id TEXT,  -- NULL if not a subscription transaction
        FOREIGN KEY (account_id) REFERENCES accounts (id),
        FOREIGN KEY (category_id) REFERENCES categories (id),
        FOREIGN KEY (subscription_id) REFERENCES subscriptions (id)
    );

    CREATE TABLE IF NOT EXISTS subscriptions (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        amount REAL NOT NULL,
        frequency TEXT NOT NULL,
        next_payment TEXT NOT NULL,
        category_id TEXT NOT NULL,
        account_id TEXT NOT NULL,
        active BOOLEAN NOT NULL DEFAULT 1,
        FOREIGN KEY (category_id) REFERENCES categories (id),
        FOREIGN KEY (account_id) REFERENCES accounts (id)
    );
    """
    )

    conn.commit()
    conn.close()
