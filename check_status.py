import sqlite3

print("\n--- ESTADO DE ORDERS ---")
conn = sqlite3.connect("orders.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM orders")
for row in cursor.fetchall():
    print(row)
conn.close()

print("\n--- ESTADO DE INVENTORY ---")
conn = sqlite3.connect("inventory.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM inventory")
for row in cursor.fetchall():
    print(row)
conn.close()

print("\n--- ESTADO DE PAYMENTS ---")
conn = sqlite3.connect("payments.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM payments")
for row in cursor.fetchall():
    print(row)
conn.close()