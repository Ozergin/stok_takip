from db import Database

db = Database()

# Kritik stokları döndürür
def check_low_stock():
    c = db.execute("SELECT seri_no, name, stock, min_stock FROM products WHERE stock <= min_stock AND stock > 0")
    return c.fetchall()

# Stok biten ürünleri döndürür
def get_out_of_stock():
    c = db.execute("SELECT seri_no, name FROM products WHERE stock <= 0")
    return c.fetchall()
