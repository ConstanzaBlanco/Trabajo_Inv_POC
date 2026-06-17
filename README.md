# Saga Pattern con RabbitMQ

Prueba de concepto desarrollada para demostrar el funcionamiento del patrón **Saga** utilizando una arquitectura basada en eventos y un enfoque de **coreografía**.

## Tecnologías utilizadas

- Python
- RabbitMQ
- SQLite
- Docker
- Pika

## Levantar RabbitMQ

Ejecutar:

```bash
docker run -d --hostname rabbitmq-demo --name rabbitmq-demo -p 5672:5672 -p 15672:15672 rabbitmq:4-management
```

RabbitMQ quedará disponible en:

```text
http://localhost:15672
```

Credenciales:

```text
Usuario: guest
Contraseña: guest
```

Puerto utilizado por los microservicios:

```text
5672
```

## Instalar dependencias

```bash
py -m pip install pika
```

## Crear las bases de datos

```bash
py setup_databases.py
```

Se generarán:

- orders.db
- inventory.db
- payments.db

## Ejecutar los servicios

Abrir una terminal para cada servicio:

```bash
py order_service.py
```

```bash
py inventory_service.py
```

```bash
py payment_service.py
```

## Ejecutar la prueba

En una nueva terminal:

```bash
py main.py
```

## ¿Qué demuestra el POC?

La solución implementa tres microservicios:

- Order Service
- Inventory Service
- Payment Service

Cada uno posee su propia base de datos SQLite y se comunica exclusivamente mediante eventos publicados en RabbitMQ.

La prueba ejecuta cuatro escenarios:

1. Pedido exitoso.
2. Pago fallido con compensación.
3. Pedido exitoso consumiendo el último stock disponible.
4. Pedido rechazado por falta de stock.

Esto permite observar el comportamiento de una Saga basada en coreografía y el uso de transacciones compensatorias para mantener la consistencia del sistema ante fallos.

## RabbitMQ

Desde la interfaz web pueden visualizarse:

- Conexiones activas.
- Colas creadas.
- Eventos publicados.
- Mensajes consumidos.
- Actividad de cada escenario ejecutado.
