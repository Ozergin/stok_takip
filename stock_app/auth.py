from db import Database

db = Database()

def register(username, password):
    db.execute("INSERT INTO users(username,password) VALUES(?,?)",(username,password))

def login(username, password):
    c = db.execute("SELECT * FROM users WHERE username=? AND password=?", (username,password))
    return c.fetchone()
