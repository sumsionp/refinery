import unittest
import os
import sqlite3
from src.db import init_db, DB_PATH

class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Use a temporary database for testing if possible,
        # but for now we'll just check if the tables exist in the initialized one
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        init_db()

    def test_tables_exist(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        tables = ['cases', 'files', 'snippets', 'settings']
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';")
            self.assertIsNotNone(cursor.fetchone(), f"Table {table} should exist")

        conn.close()

if __name__ == '__main__':
    unittest.main()
