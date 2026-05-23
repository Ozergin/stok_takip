import sqlite3

DB_FILE = "stock.db"

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.create_tables()

    def create_tables(self):
        c = self.conn.cursor()

        # ===== USERS =====
        c.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT DEFAULT 'personel'
        )
        """)

        # ===== PRODUCTS =====
        c.execute("""
        CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seri_no TEXT UNIQUE,
            name TEXT,
            stock INTEGER,
            price REAL,
            buy_price REAL,
            min_stock INTEGER
        )
        """)

        # ===== SALES =====
        c.execute("""
        CREATE TABLE IF NOT EXISTS sales(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seri_no TEXT,
            amount INTEGER,
            price REAL,
            total REAL,
            date TEXT
        )
        """)

        # ===== STOCK LOGS =====
        c.execute("""
        CREATE TABLE IF NOT EXISTS stock_logs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seri_no TEXT,
            type TEXT,        -- giris / cikis / satis / iade
            amount INTEGER,
            date TEXT,
            user TEXT
        )
        """)

        self.conn.commit()

    def execute(self, q, p=()):
        c = self.conn.cursor()
        c.execute(q, p)
        self.conn.commit()
        return c
