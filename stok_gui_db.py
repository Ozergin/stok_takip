ox
import sqlite3

DB_FILE = "stok.db"
KRITIK_STOK_LIMIT = 2


# =========================
# DATABASE LAYER
class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seri_no TEXT UNIQUE,
            urun_adi TEXT,
            gelen_adet INTEGER,
            satilan_adet INTEGER,
            kalan_adet INTEGER
        )
        """)
        self.conn.commit()

    def execute(self, query, params=()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor


# =========================
# BUSINESS LOGIC
# =========================

class StockService:
    def __init__(self):
        self.db = Database()

    def add_product(self, seri_no, urun_adi, adet):
        self.db.execute("""
            INSERT INTO products (seri_no, urun_adi, gelen_adet, satilan_adet, kalan_adet)
            VALUES (?, ?, ?, 0, ?)
        """, (seri_no, urun_adi, adet, adet))

    def update_stock(self, seri_no, new_stock):
        self.db.execute("""
            UPDATE products
            SET gelen_adet = gelen_adet + ?,
                kalan_adet = kalan_adet + ?
            WHERE seri_no = ?
        """, (new_stock, new_stock, seri_no))

    def sell(self, seri_no):
        cursor = self.db.execute("""
            SELECT kalan_adet, satilan_adet FROM products WHERE seri_no = ?
        """, (seri_no,))
        row = cursor.fetchone()

        if not row:
            raise Exception("Ürün bulunamadı.")

        kalan, satilan = row
        if kalan <= 0:
            raise Exception("Stok bitti.")

        kalan -= 1
        satilan += 1

        self.db.execute("""
            UPDATE products
            SET kalan_adet = ?, satilan_adet = ?
            WHERE seri_no = ?
        """, (kalan, satilan, seri_no))

        return kalan

    def get_all(self):
        cursor = self.db.execute("SELECT seri_no, urun_adi, gelen_adet, satilan_adet, kalan_adet FROM products")
        return cursor.fetchall()

    def search_by_seri(self, seri):
        cursor = self.db.execute("""
            SELECT seri_no, urun_adi, gelen_adet, satilan_adet, kalan_adet
            FROM products
            WHERE seri_no LIKE ?
        """, (f"%{seri}%",))
        return cursor.fetchall()

    def search_by_name(self, name):
        cursor = self.db.execute("""
            SELECT seri_no, urun_adi, gelen_adet, satilan_adet, kalan_adet
            FROM products
            WHERE urun_adi LIKE ?
        """, (f"%{name}%",))
        return cursor.fetchall()


# =========================
# GUI
# =========================

class StockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Profesyonel Stok Sistemi")
        self.root.geometry("900x620")

        self.service = StockService()
        self.build_ui()
        self.refresh_list()

    def build_ui(self):
        # Ürün ekle
        tk.Label(self.root, text="Ürün Ekle", font=("Arial", 13, "bold")).pack()
        f1 = tk.Frame(self.root)
        f1.pack(pady=5)

        self.seri_e = tk.Entry(f1)
        self.ad_e = tk.Entry(f1)
        self.adet_e = tk.Entry(f1)

        tk.Label(f1, text="Seri").grid(row=0, column=0)
        tk.Label(f1, text="Ad").grid(row=1, column=0)
        tk.Label(f1, text="Adet").grid(row=2, column=0)

        self.seri_e.grid(row=0, column=1)
        self.ad_e.grid(row=1, column=1)
        self.adet_e.grid(row=2, column=1)

        tk.Button(f1, text="Ekle", command=self.add_product).grid(row=3, columnspan=2, pady=5)

        # Stok artır
        tk.Label(self.root, text="Stok Artır", font=("Arial", 13, "bold")).pack()
        f2 = tk.Frame(self.root)
        f2.pack()

        self.update_seri = tk.Entry(f2)
        self.update_adet = tk.Entry(f2)

        tk.Label(f2, text="Seri").grid(row=0, column=0)
        tk.Label(f2, text="Eklenecek Adet").grid(row=1, column=0)

        self.update_seri.grid(row=0, column=1)
        self.update_adet.grid(row=1, column=1)

        tk.Button(f2, text="Stok Güncelle", command=self.update_stock).grid(row=2, columnspan=2, pady=5)

        # Satış
        tk.Label(self.root, text="Satış", font=("Arial", 13, "bold")).pack()
        f3 = tk.Frame(self.root)
        f3.pack()

        self.sale_seri = tk.Entry(f3)
        tk.Label(f3, text="Seri").grid(row=0, column=0)
        self.sale_seri.grid(row=0, column=1)

        tk.Button(f3, text="Satış Yap", command=self.sell).grid(row=1, columnspan=2, pady=5)

        # Arama
        tk.Label(self.root, text="Ürün Arama", font=("Arial", 13, "bold")).pack(pady=5)
        f4 = tk.Frame(self.root)
        f4.pack()

        self.search_seri = tk.Entry(f4)
        self.search_name = tk.Entry(f4)

        tk.Label(f4, text="Seri No").grid(row=0, column=0)
        tk.Label(f4, text="Ürün Adı").grid(row=0, column=2)

        self.search_seri.grid(row=0, column=1)
        self.search_name.grid(row=0, column=3)

        tk.Button(f4, text="Seri Ara", command=self.search_by_seri).grid(row=1, column=0, columnspan=2, pady=5)
        tk.Button(f4, text="İsim Ara", command=self.search_by_name).grid(row=1, column=2, columnspan=2, pady=5)
        tk.Button(f4, text="Tüm Liste", command=self.refresh_list).grid(row=2, columnspan=4, pady=5)

        # Liste
        self.listbox = tk.Listbox(self.root, width=130, height=12)
        self.listbox.pack(pady=10)

    # ===== actions =====

    def add_product(self):
        try:
            self.service.add_product(
                self.seri_e.get(),
                self.ad_e.get(),
                int(self.adet_e.get())
            )
            self.refresh_list()
        except Exception as e:
            messagebox.showerror("Hata", str(e))

    def update_stock(self):
        try:
            self.service.update_stock(
                self.update_seri.get(),
                int(self.update_adet.get())
            )
            self.refresh_list()
        except Exception as e:
            messagebox.showerror("Hata", str(e))

    def sell(self):
        try:
            kalan = self.service.sell(self.sale_seri.get())
            if kalan < KRITIK_STOK_LIMIT:
                messagebox.showwarning("Kritik", f"Kritik stok! Kalan: {kalan}")
            self.refresh_list()
        except Exception as e:
            messagebox.showerror("Hata", str(e))

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        for p in self.service.get_all():
            self.listbox.insert(tk.END, f"{p[0]} | {p[1]} | Gelen:{p[2]} | Satılan:{p[3]} | Kalan:{p[4]}")

    def search_by_seri(self):
        self.listbox.delete(0, tk.END)
        results = self.service.search_by_seri(self.search_seri.get())
        for p in results:
            self.listbox.insert(tk.END, f"{p[0]} | {p[1]} | Gelen:{p[2]} | Satılan:{p[3]} | Kalan:{p[4]}")

    def search_by_name(self):
        self.listbox.delete(0, tk.END)
        results = self.service.search_by_name(self.search_name.get())
        for p in results:
            self.listbox.insert(tk.END, f"{p[0]} | {p[1]} | Gelen:{p[2]} | Satılan:{p[3]} | Kalan:{p[4]}")


# =========================
# START
# =========================

if __name__ == "__main__":
    root = tk.Tk()
    app = StockApp(root)
    root.mainloop()
