import sqlite3
import pika
import json
import sys

ORDER_ID = 1
PRODUCT = "Laptop"


def get_channel():
    # Conecta Python con RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    return connection, channel


def publish_event(event_name, data):
    # Publica un evento en RabbitMQ
    connection, channel = get_channel()

    channel.queue_declare(queue=event_name, durable=True)

    channel.basic_publish(
        exchange="",
        routing_key=event_name,
        body=json.dumps(data),
        properties=pika.BasicProperties(delivery_mode=2)
    )

    connection.close()


def create_order():
    # Guarda el pedido en la base local del servicio Order
    conn = sqlite3.connect("orders.db")

    conn.execute(
        "INSERT OR REPLACE INTO orders(id, product, status) VALUES (?, ?, ?)",
        (ORDER_ID, PRODUCT, "PENDING")
    )

    conn.commit()
    conn.close()

    print("[ORDER] Pedido creado con estado PENDING")

    # Publica evento para que Inventory Service lo procese
    publish_event("order_created", {
        "order_id": ORDER_ID,
        "product": PRODUCT
    })

    print("[ORDER] Evento enviado: order_created")


def listen_payment_events():
    # Escucha eventos del Payment Service
    connection, channel = get_channel()

    channel.queue_declare(queue="payment_approved", durable=True)
    channel.queue_declare(queue="payment_failed", durable=True)

    def payment_approved_callback(ch, method, properties, body):
        data = json.loads(body)

        conn = sqlite3.connect("orders.db")
        conn.execute(
            "UPDATE orders SET status = ? WHERE id = ?",
            ("CONFIRMED", data["order_id"])
        )
        conn.commit()
        conn.close()

        print("[ORDER] Pago aprobado. Pedido CONFIRMED")

    def payment_failed_callback(ch, method, properties, body):
        data = json.loads(body)

        conn = sqlite3.connect("orders.db")
        conn.execute(
            "UPDATE orders SET status = ? WHERE id = ?",
            ("CANCELLED", data["order_id"])
        )
        conn.commit()
        conn.close()

        print("[ORDER] Pago fallido. Pedido CANCELLED")

        # Compensación: avisa que el pedido fue cancelado
        publish_event("order_cancelled", {
            "order_id": data["order_id"],
            "product": data["product"]
        })

        print("[ORDER] Evento enviado: order_cancelled")

    channel.basic_consume(
        queue="payment_approved",
        on_message_callback=payment_approved_callback,
        auto_ack=True
    )

    channel.basic_consume(
        queue="payment_failed",
        on_message_callback=payment_failed_callback,
        auto_ack=True
    )

    print("[ORDER] Esperando eventos de pago...")
    channel.start_consuming()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "create":
        create_order()
    else:
        listen_payment_events()
