import sqlite3
import pika
import json


def get_channel():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    return connection, channel


def publish_event(event_name, data):
    connection, channel = get_channel()

    channel.queue_declare(queue=event_name, durable=True)

    channel.basic_publish(
        exchange="",
        routing_key=event_name,
        body=json.dumps(data),
        properties=pika.BasicProperties(delivery_mode=2)
    )

    connection.close()


def reserve_stock(order_id, product):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("SELECT quantity FROM inventory WHERE product = ?", (product,))
    row = cursor.fetchone()

    if row is None or row[0] <= 0:
        conn.close()
        print("[INVENTORY] No hay stock disponible")

        publish_event("stock_failed", {
            "order_id": order_id,
            "product": product
        })
        return

    new_quantity = row[0] - 1

    cursor.execute(
        "UPDATE inventory SET quantity = ? WHERE product = ?",
        (new_quantity, product)
    )

    conn.commit()
    conn.close()

    print(f"[INVENTORY] Stock reservado. Stock actual: {new_quantity}")

    publish_event("stock_reserved", {
        "order_id": order_id,
        "product": product
    })

    print("[INVENTORY] Evento enviado: stock_reserved")

#Reroll
def restore_stock(order_id, product):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE inventory SET quantity = quantity + 1 WHERE product = ?",
        (product,)
    )

    conn.commit()

    cursor.execute("SELECT quantity FROM inventory WHERE product = ?", (product,))
    quantity = cursor.fetchone()[0]

    conn.close()

    print(f"[INVENTORY] Compensación ejecutada. Stock restaurado: {quantity}")


def listen_events():
    connection, channel = get_channel()

    channel.queue_declare(queue="order_created", durable=True)
    channel.queue_declare(queue="order_cancelled", durable=True)

    def order_created_callback(ch, method, properties, body):
        data = json.loads(body)
        print("[INVENTORY] Evento recibido: order_created")
        reserve_stock(data["order_id"], data["product"])

    def order_cancelled_callback(ch, method, properties, body):
        data = json.loads(body)
        print("[INVENTORY] Evento recibido: order_cancelled")
        restore_stock(data["order_id"], data["product"])

    channel.basic_consume(
        queue="order_created",
        on_message_callback=order_created_callback,
        auto_ack=True
    )

    channel.basic_consume(
        queue="order_cancelled",
        on_message_callback=order_cancelled_callback,
        auto_ack=True
    )

    print("[INVENTORY] Esperando eventos...")
    channel.start_consuming()


if __name__ == "__main__":
    listen_events()