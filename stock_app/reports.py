import sqlite3
from datetime import datetime, timedelta

DB_FILE = "stock.db"

def ciro(period):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    now = datetime.now()

    if period == "daily":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    elif period == "weekly":
        start = now - timedelta(days=7)

    elif period == "monthly":
        start = now - timedelta(days=30)

    elif period == "yearly":
        start = now - timedelta(days=365)

    else:
        conn.close()
        return 0

    c.execute(
        "SELECT SUM(total) FROM sales WHERE date >= ?",
        (start.isoformat(),)
    )

    result = c.fetchone()[0]
    conn.close()

    return result if result else 0


def reset_ciro():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Satislari sifirlar (ciro = 0)
    c.execute("DELETE FROM sales")

    conn.commit()
    conn.close()
