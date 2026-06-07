import sqlite3
import pika
import json

# Cambiar esto:
# True  = fuerza fallo de pago
# False = pago aprobado
FAIL_PAYMENT = True


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


def process_payment(order_id, product):
    conn = sqlite3.connect("payments.db")

    if FAIL_PAYMENT:
        status = "FAILED"
        event = "payment_failed"
        print("[PAYMENT] Pago fallido intencionalmente")
    else:
        status = "APPROVED"
        event = "payment_approved"
        print("[PAYMENT] Pago aprobado")

    conn.execute(
        "INSERT OR REPLACE INTO payments(id, order_id, status) VALUES (?, ?, ?)",
        (order_id, order_id, status)
    )

    conn.commit()
    conn.close()

    publish_event(event, {
        "order_id": order_id,
        "product": product
    })

    print(f"[PAYMENT] Evento enviado: {event}")


def listen_stock_reserved():
    connection, channel = get_channel()

    channel.queue_declare(queue="stock_reserved", durable=True)

    def stock_reserved_callback(ch, method, properties, body):
        data = json.loads(body)
        print("[PAYMENT] Evento recibido: stock_reserved")
        process_payment(data["order_id"], data["product"])

    channel.basic_consume(
        queue="stock_reserved",
        on_message_callback=stock_reserved_callback,
        auto_ack=True
    )

    print("[PAYMENT] Esperando evento stock_reserved...")
    channel.start_consuming()


if __name__ == "__main__":
    listen_stock_reserved()