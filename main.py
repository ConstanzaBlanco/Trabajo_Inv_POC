from threading import Thread
from order_service import create_order
import time

def pedido_1_exitoso():
    create_order(order_id=1, producto="Laptop", payment_success=True)

def pedido_2_pago_fallido():
    create_order(order_id=2, producto="Laptop", payment_success=False)

def pedido_3_exitoso_agota_stock():
    create_order(order_id=3, producto="Laptop", payment_success=True)

def pedido_4_stock_fallido():
    create_order(order_id=4, producto="Laptop", payment_success=True)

t1 = Thread(target=pedido_1_exitoso)
t2 = Thread(target=pedido_2_pago_fallido)
t3 = Thread(target=pedido_3_exitoso_agota_stock)
t4 = Thread(target=pedido_4_stock_fallido)

t1.start()
time.sleep(10)
t2.start()
time.sleep(10)
t3.start()
time.sleep(10)
t4.start()

t1.join()
t2.join()
t3.join()
t4.join()

print("Pedidos enviados")
