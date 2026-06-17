import sqlite3

# -------------------------
# Base de datos de pedidos
# -------------------------

conn = sqlite3.connect("orders.db")

conn.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    product TEXT,
    status TEXT
)
""")

conn.close()

# -------------------------
# Base de datos de inventario
# -------------------------

conn = sqlite3.connect("inventory.db")

conn.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    product TEXT PRIMARY KEY,
    quantity INTEGER
)
""")

# Insertamos stock inicial
conn.execute("""
INSERT OR REPLACE INTO inventory(product, quantity)
VALUES ('Laptop', 2)
""")

conn.commit()
conn.close()

# -------------------------
# Base de datos de pagos
# -------------------------

conn = sqlite3.connect("payments.db")

conn.execute("""
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY,
    order_id INTEGER,
    status TEXT
)
""")

conn.close()

print("Bases de datos creadas correctamente")