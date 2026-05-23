import tkinter as tk
from tkinter import messagebox
from db import Database
from auth import login
from qr import scan_qr
from stock_ai import check_low_stock, get_out_of_stock
from datetime import datetime

db = Database()

# ===== TABLOLAR =====
db.execute("""
CREATE TABLE IF NOT EXISTS debts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    seri_no TEXT,
    customer_name TEXT,
    customer_surname TEXT,
    phone TEXT,
    plate TEXT,
    amount INTEGER,
    total REAL,
    date TEXT
)
""")

# ================== GİRİŞ ==================
class LoginApp:
    def __init__(self, root):
        self.root = root
        root.title("Giriş")
        root.geometry("300x200")

        tk.Label(root, text="Kullanıcı Adı").pack(pady=5)
        self.u = tk.Entry(root); self.u.pack()

        tk.Label(root, text="Şifre").pack(pady=5)
        self.p = tk.Entry(root, show="*"); self.p.pack()

        tk.Button(root, text="Giriş Yap", command=self.do_login).pack(pady=15)

    def do_login(self):
        username = self.u.get()
        password = self.p.get()

        if (username == "ozergin" and password == "1234.") or login(username, password):
            self.root.destroy()
            main(admin_mode=(username == "admin"))
        else:
            messagebox.showerror("Hata", "Giriş başarısız")

# ================== ANA ==================
class MainApp:
    def __init__(self, root, admin_mode=False):
        self.root = root
        self.admin_mode = admin_mode
        root.title("Kurumsal Stok Sistemi")
        root.geometry("1300x900")

        # ÜST PANEL
        top_frame = tk.Frame(root)
        top_frame.pack(fill="x", pady=5)

        # ÜRÜN YÖNETİMİ
        um_frame = tk.LabelFrame(top_frame, text="Ürün Yönetimi", padx=10, pady=10)
        um_frame.pack(side="left", padx=10)

        labels = ["Seri No","Ürün Adı","Stok","Fiyat","Min Stok"]
        self.entries = {}

        for i,l in enumerate(labels):
            tk.Label(um_frame,text=l).grid(row=i,column=0,sticky="w")
            e = tk.Entry(um_frame,width=20)
            e.grid(row=i,column=1,pady=2)
            self.entries[l] = e

        tk.Button(um_frame, text="Ürün Ekle", command=self.add_product, width=20)\
            .grid(row=5,columnspan=2,pady=8)

        # SATIŞ PANELİ
        sp_frame = tk.LabelFrame(top_frame, text="Satış Paneli", padx=10, pady=10)
        sp_frame.pack(side="left", padx=10)

        tk.Label(sp_frame,text="Seri No").grid(row=0,column=0)
        tk.Label(sp_frame,text="Adet").grid(row=1,column=0)

        self.sale_seri = tk.Entry(sp_frame,width=18); self.sale_seri.grid(row=0,column=1)
        self.adet = tk.Entry(sp_frame,width=18); self.adet.grid(row=1,column=1)

        tk.Button(sp_frame,text="Manuel Satış",command=self.manual_sale,width=18)\
            .grid(row=2,columnspan=2,pady=5)

        tk.Button(sp_frame,text="Borçlu Satış",command=self.debt_sale,width=18, bg="#fff3cd")\
            .grid(row=3,columnspan=2,pady=5)

        tk.Button(sp_frame,text="QR ile Satış",command=self.qr_sale,width=18)\
            .grid(row=4,columnspan=2,pady=5)

        # ÜRÜN LİSTESİ
        list_frame = tk.LabelFrame(root, text="Ürün Listesi", padx=10, pady=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.listbox = tk.Listbox(list_frame,font=("Consolas",11))
        self.listbox.pack(fill="both", expand=True)

        # ALT PANEL
        bottom_panel = tk.Frame(root, bd=2, relief="groove")
        bottom_panel.pack(fill="x", side="bottom", padx=10, pady=10)

        tk.Button(bottom_panel,text="Listeyi Yenile",command=self.refresh,width=16).pack(side="left", padx=5)
        tk.Button(bottom_panel,text="Ürün Detayı",command=self.show_product_detail,width=16).pack(side="left", padx=5)
        tk.Button(bottom_panel,text="Seçili Ürünü Sil",command=self.delete_selected_product,width=16).pack(side="left", padx=5)
        tk.Button(bottom_panel,text="Borç Listesi",command=self.show_debt_list,width=16, bg="#d1ecf1").pack(side="left", padx=5)
        tk.Button(bottom_panel,text="Stoğu Bitenler",command=self.show_out_of_stock,width=16,bg="#f8d7da").pack(side="left", padx=5)
        tk.Button(bottom_panel,text="Kritik Stoklar",command=self.show_critical_stock,width=16,bg="#fff3cd").pack(side="left", padx=5)


        tk.Button(bottom_panel,text="Günlük Ciro",command=lambda:self.show_ciro("daily"),width=14).pack(side="left", padx=3)
        tk.Button(bottom_panel,text="Haftalık Ciro",command=lambda:self.show_ciro("weekly"),width=14).pack(side="left", padx=3)
        tk.Button(bottom_panel,text="Aylık Ciro",command=lambda:self.show_ciro("monthly"),width=14).pack(side="left", padx=3)
        tk.Button(bottom_panel,text="Yıllık Ciro",command=lambda:self.show_ciro("yearly"),width=14).pack(side="left", padx=3)

        tk.Button(bottom_panel,text="Ciro Sıfırla",command=self.reset_ciro_btn,width=14,bg="#f8d7da").pack(side="left", padx=5)
        tk.Button(bottom_panel,text="Çıkış Yap",command=self.logout,width=14).pack(side="right", padx=10)

        self.refresh()

            # ================== FİLTRELEME ==================
    def show_out_of_stock(self):
        self.listbox.delete(0, tk.END)
        for p in db.execute("SELECT seri_no,name,stock,price,min_stock FROM products WHERE stock<=0").fetchall():
            self.listbox.insert(
                tk.END,
                f"{p[0]} | {p[1]} | Stok:{p[2]} | Fiyat:{p[3]} | Min:{p[4]} | STOK BİTTİ"
            )

    def show_critical_stock(self):
        self.listbox.delete(0, tk.END)
        for p in db.execute("SELECT seri_no,name,stock,price,min_stock FROM products WHERE stock>0 AND stock<=min_stock").fetchall():
            self.listbox.insert(
                tk.END,
                f"{p[0]} | {p[1]} | Stok:{p[2]} | Fiyat:{p[3]} | Min:{p[4]} | KRİTİK"
            )


    # ================== BORÇLU SATIŞ ==================
    def debt_sale(self):
        seri = self.sale_seri.get()
        adet = int(self.adet.get()) if self.adet.get() else 1

        r = db.execute("SELECT stock,price FROM products WHERE seri_no=?", (seri,)).fetchone()
        if not r:
            messagebox.showerror("Hata","Ürün yok"); return

        stock, price = r
        if stock < adet:
            messagebox.showerror("Hata","Yetersiz stok"); return

        win = tk.Toplevel(self.root)
        win.title("Borçlu Satış")
        win.geometry("350x400")

        fields = ["Ad","Soyad","Telefon","Plaka"]
        entries = {}

        for f in fields:
            tk.Label(win,text=f).pack()
            e = tk.Entry(win,width=30)
            e.pack()
            entries[f]=e

        def save_debt():
            name = entries["Ad"].get()
            surname = entries["Soyad"].get()
            phone = entries["Telefon"].get()
            plate = entries["Plaka"].get()

            total = price * adet

            db.execute("UPDATE products SET stock=stock-? WHERE seri_no=?", (adet,seri))
            db.execute("INSERT INTO sales(seri_no,amount,price,total,date) VALUES(?,?,?,?,?)",
                       (seri,adet,price,total,datetime.now().isoformat()))

            db.execute("""INSERT INTO debts
            (seri_no,customer_name,customer_surname,phone,plate,amount,total,date)
            VALUES(?,?,?,?,?,?,?,?)""",
            (seri,name,surname,phone,plate,adet,total,datetime.now().isoformat()))

            messagebox.showinfo("Bilgi","Borç kaydedildi")
            win.destroy()
            self.refresh()

        tk.Button(win,text="Borcu Kaydet",command=save_debt,width=20,bg="#ffeeba").pack(pady=20)

    # ================== BORÇ LİSTESİ ==================
    def show_debt_list(self):
        # Sayfa zaten açıksa yeni açma, üzerine getir
        if hasattr(self, "debt_win") and getattr(self, "debt_win", None) and self.debt_win.winfo_exists():
            self.debt_win.lift()
            return

        self.debt_win = tk.Toplevel(self.root)
        win = self.debt_win
        win.title("Borç Listesi")
        win.geometry("1100x600")

        # Çoklu seçim için extended
        self.debt_listbox = tk.Listbox(win,font=("Consolas",11), selectmode=tk.EXTENDED)
        self.debt_listbox.pack(fill="both", expand=True)

        def refresh_debt_list():
            self.debt_listbox.delete(0, tk.END)
            rows = db.execute("SELECT id,seri_no,customer_name,customer_surname,phone,plate,amount,total,date FROM debts ORDER BY date DESC").fetchall()
            for r in rows:
                self.debt_listbox.insert(tk.END,
                    f"{r[2]} {r[3]} | Tel:{r[4]} | Plaka:{r[5]} | Ürün:{r[1]} | Adet:{r[6]} | Tutar:{r[7]} | Tarih:{r[8][:19]} | ID:{r[0]}")

        refresh_debt_list()

        def delete_selected_debt():
            sel = self.debt_listbox.curselection()
            if not sel:
                messagebox.showerror("Hata","Borç seç"); return
            if messagebox.askyesno("Onay","Seçili borçlar silinsin mi?"):
                for i in reversed(sel):
                    line = self.debt_listbox.get(i)
                    debt_id = int(line.split("| ID:")[1])
                    db.execute("DELETE FROM debts WHERE id=?", (debt_id,))
                refresh_debt_list()
                messagebox.showinfo("Bilgi","Seçili borçlar silindi")

        tk.Button(win,text="Seçili Borçları Sil",command=delete_selected_debt,bg="#f5c6cb").pack(pady=5)

    # ================== CİRO ==================
    def show_ciro(self, mode):
        win = tk.Toplevel(self.root)
        win.title("Ciro Raporu")
        win.geometry("900x600")

        lb = tk.Listbox(win,font=("Consolas",11))
        lb.pack(fill="both", expand=True)

        now = datetime.now()

        if mode == "daily":
            f = now.strftime("%Y-%m-%d")
            q = "SELECT seri_no,amount,total,date FROM sales WHERE date LIKE ?"
            p = (f"{f}%",); title="GÜNLÜK CİRO"
        elif mode == "weekly":
            w = now.strftime("%Y-%W")
            q = "SELECT seri_no,amount,total,date FROM sales WHERE strftime('%Y-%W',date)=?"
            p = (w,); title="HAFTALIK CİRO"
        elif mode == "monthly":
            m = now.strftime("%Y-%m")
            q = "SELECT seri_no,amount,total,date FROM sales WHERE date LIKE ?"
            p = (f"{m}%",); title="AYLIK CİRO"
        else:
            y = now.strftime("%Y")
            q = "SELECT seri_no,amount,total,date FROM sales WHERE date LIKE ?"
            p = (f"{y}%",); title="YILLIK CİRO"

        rows = db.execute(q,p).fetchall()
        lb.insert(tk.END,f"===== {title} =====")

        total = 0
        for r in rows:
            lb.insert(tk.END,f"{r[0]} | Adet:{r[1]} | Tutar:{r[2]} | Tarih:{r[3][:19]}")
            total += r[2]

        lb.insert(tk.END,"")
        lb.insert(tk.END,f"TOPLAM CİRO: {total} TL")

    def reset_ciro_btn(self):
        if messagebox.askyesno("Onay","TÜM CİROYU SIFIRLAMAK istiyor musun?"):
            db.execute("DELETE FROM sales")
            messagebox.showinfo("Bilgi","Ciro sıfırlandı")

    # ================== ÜRÜN DETAY + DÜZENLE ==================
    def show_product_detail(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showerror("Hata","Ürün seç"); return

        seri = self.listbox.get(sel[0]).split(" | ")[0]
        prod = db.execute("SELECT * FROM products WHERE seri_no=?", (seri,)).fetchone()

        win = tk.Toplevel(self.root)
        win.title("Ürün Detayı")
        win.geometry("1000x650")

        info = tk.Frame(win)
        info.pack(fill="x")

        tk.Label(info,text=f"Seri: {prod[1]} | Ad: {prod[2]} | Stok: {prod[3]} | Fiyat: {prod[4]} | Min: {prod[5]}",
                 font=("Arial",12,"bold")).pack(pady=5)

        edit = tk.LabelFrame(win,text="Ürünü Düzenle")
        edit.pack(fill="x", pady=5)

        e_name=tk.Entry(edit); e_name.insert(0,prod[2])
        e_price=tk.Entry(edit); e_price.insert(0,str(prod[4]))
        e_min=tk.Entry(edit); e_min.insert(0,str(prod[5]))
        e_stock=tk.Entry(edit); e_stock.insert(0,str(prod[3]))

        for lbl,e in [("Ad",e_name),("Fiyat",e_price),("Min Stok",e_min),("Stok",e_stock)]:
            tk.Label(edit,text=lbl).pack()
            e.pack()

        def save_edit():
            name_val = e_name.get().strip()
            stock_val = e_stock.get().strip()
            price_val = e_price.get().strip()
            min_val = e_min.get().strip()

            # 🔒 Veri doğrulama
            if not name_val:
                messagebox.showerror("Hata","Ürün adı boş olamaz")
                return
            if not stock_val.isdigit():
                messagebox.showerror("Hata","Stok sayı olmalı")
                return
            if not min_val.isdigit():
                messagebox.showerror("Hata","Min stok sayı olmalı")
                return

            try:
                price_val = float(price_val)
            except:
                messagebox.showerror("Hata","Fiyat sayı olmalı")
                return

            db.execute("""
                UPDATE products 
                SET name=?, stock=?, price=?, min_stock=? 
                WHERE seri_no=?
            """, (
                name_val,
                int(stock_val),
                float(price_val),
                int(min_val),
                seri
            ))

            messagebox.showinfo("Bilgi","Ürün güncellendi")
            win.destroy()
            self.refresh()

        tk.Button(edit,text="Kaydet",command=save_edit,bg="#d4edda").pack(pady=5)

    # ================== TEMEL ==================
    def add_product(self):
        db.execute("INSERT INTO products(seri_no,name,stock,price,min_stock) VALUES(?,?,?,?,?)",
                   (self.entries["Seri No"].get(),self.entries["Ürün Adı"].get(),
                    int(self.entries["Stok"].get()),float(self.entries["Fiyat"].get()),
                    int(self.entries["Min Stok"].get())))

        self.refresh()

    def refresh(self):
        self.listbox.delete(0, tk.END)
        for p in db.execute("SELECT seri_no,name,stock,price,min_stock FROM products").fetchall():
            durum=""
            if p[2]<=0: durum=" | STOK BİTTİ"
            elif p[2]<=p[4]: durum=" | KRİTİK"
            self.listbox.insert(tk.END,f"{p[0]} | {p[1]} | Stok:{p[2]} | Fiyat:{p[3]} | Min:{p[4]}{durum}")

    def manual_sale(self):
        seri=self.sale_seri.get()
        adet=int(self.adet.get()) if self.adet.get() else 1
        r=db.execute("SELECT stock,price FROM products WHERE seri_no=?",(seri,)).fetchone()
        if not r: return
        stock,price=r
        if stock<adet: return
        total=price*adet
        db.execute("UPDATE products SET stock=stock-? WHERE seri_no=?",(adet,seri))
        db.execute("INSERT INTO sales(seri_no,amount,price,total,date) VALUES(?,?,?,?,?)",
                   (seri,adet,price,total,datetime.now().isoformat()))
        messagebox.showinfo("Bilgi","Satış yapıldı")
        self.refresh()

    def qr_sale(self):
        seri=scan_qr()
        if not seri:return
        self.sale_seri.delete(0,tk.END)
        self.sale_seri.insert(0,seri)
        self.manual_sale()

    def delete_selected_product(self):
        sel=self.listbox.curselection()
        if not sel:return
        seri=self.listbox.get(sel[0]).split(" | ")[0]
        if messagebox.askyesno("Onay","Silinsin mi?"):
            db.execute("DELETE FROM products WHERE seri_no=?",(seri,))
            self.refresh()

    def logout(self):
        self.root.destroy()
        r=tk.Tk()
        LoginApp(r)
        r.mainloop()

# ================== BAŞLAT ==================
def main(admin_mode=False):
    root=tk.Tk()
    MainApp(root,admin_mode)
    root.mainloop()

if __name__=="__main__":
    r=tk.Tk()
    LoginApp(r)
    r.mainloop()
