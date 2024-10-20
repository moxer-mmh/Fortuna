import unittest
import os
import sqlite3
import tempfile
import shutil
from finance_manager.database.models import init_database
from finance_manager.database import DatabaseConnection


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")

        os.environ["APPDATA"] = self.temp_dir

        DatabaseConnection._instance = None

    def tearDown(self):
        try:
            if hasattr(self, "db") and self.db:
                self.db.get_connection().close()

            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception as e:
            print(f"Error during cleanup: {e}")

    def test_init_database(self):
        init_database(self.db_path)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = {table[0] for table in cursor.fetchall()}

        expected_tables = {"accounts", "categories", "transactions"}
        self.assertEqual(expected_tables, tables & expected_tables)

        conn.close()

    def test_database_connection_singleton(self):
        conn1 = DatabaseConnection()
        conn2 = DatabaseConnection()
        self.assertIs(conn1, conn2)

    def test_execute_query(self):
        db = DatabaseConnection()

        db.execute_query(
            "INSERT INTO accounts (id, name, balance) VALUES (?, ?, ?)",
            ("1", "Test Account", 1000.0),
        )

        result = db.fetch_one("SELECT name, balance FROM accounts WHERE id = ?", ("1",))
        self.assertEqual(result, ("Test Account", 1000.0))

    def test_execute_many(self):
        db = DatabaseConnection()

        test_data = [
            ("1", "Account 1", 1000.0),
            ("2", "Account 2", 2000.0),
            ("3", "Account 3", 3000.0),
        ]

        db.execute_many(
            "INSERT INTO accounts (id, name, balance) VALUES (?, ?, ?)", test_data
        )

        results = db.fetch_all("SELECT name, balance FROM accounts ORDER BY id")
        expected = [("Account 1", 1000.0), ("Account 2", 2000.0), ("Account 3", 3000.0)]
        self.assertEqual(results, expected)

    def test_fetch_all(self):
        db = DatabaseConnection()

        test_categories = [
            ("1", "Food", 500.0, "expense"),
            ("2", "Salary", 5000.0, "income"),
        ]

        db.execute_many(
            "INSERT INTO categories (id, name, budget, type) VALUES (?, ?, ?, ?)",
            test_categories,
        )

        expense_categories = db.fetch_all(
            "SELECT name, budget FROM categories WHERE type = ?", ("expense",)
        )
        self.assertEqual(expense_categories, [("Food", 500.0)])

    def test_fetch_one(self):
        db = DatabaseConnection()

        db.execute_query(
            "INSERT INTO categories (id, name, budget, type) VALUES (?, ?, ?, ?)",
            ("1", "Test Category", 1000.0, "expense"),
        )

        result = db.fetch_one(
            "SELECT name, budget FROM categories WHERE id = ?", ("1",)
        )
        self.assertEqual(result, ("Test Category", 1000.0))


if __name__ == "__main__":
    unittest.main()
