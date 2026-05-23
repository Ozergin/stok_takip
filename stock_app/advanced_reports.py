from db import Database
from datetime import datetime, timedelta

db = Database()

def stok_degeri():
    c = db.execute("SELECT stock, price FROM products")
    total = 0
    for s,p in c.fetchall():
        total += s * p
    return total

def kar_raporu():
    c = db.execute("SELECT price, buy_price, amount FROM sales JOIN products ON sales.seri_no=products.seri_no")
    total = 0
    for sale_price,buy_price,amount in c.fetchall():
        total += (sale_price - buy_price) * amount
    return total

def en_cok_satan():
    c = db.execute("""
    SELECT seri_no, SUM(amount) as total
    FROM sales
    GROUP BY seri_no
    ORDER BY total DESC
    LIMIT 5
    """)
    return c.fetchall()

def olu_stok():
    limit = datetime.now() - timedelta(days=30)
    c = db.execute("""
    SELECT seri_no FROM products
    WHERE seri_no NOT IN (
        SELECT DISTINCT seri_no FROM sales WHERE date > ?
    )
    """,(limit.isoformat(),))
    return c.fetchall()
