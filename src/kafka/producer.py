import json
import logging
from confluent_kafka import Producer
from src.core.config import settings
from src.schemas.order import OrderRead

config = {
    'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
    'acks': 'all'
}

def delivery_report(err, msg):
    "Called once for each message produced to indicate delivery result"
    if err is not None:
        logging.error(f"Message delivery failed: {err}")
    else:
        logging.info(f"Message delivered to {msg.topic()} at offset {msg.offset()}")

def shutdown_kafka():
    "Shutdown the Kafka producer"
    logging.info("Shutting down Kafka producer...")
    producer.flush()
    logging.info("Kafka producer shut down successfully.")

producer = Producer(config)

async def send_new_order_message(order: OrderRead):
    "Produce a new order message to Kafka to the new_orders topic"
    try:
        producer.produce(
            topic=settings.KAFKA_NEW_ORDERS_TOPIC,
            key=str(order.id),
            value=json.dumps(order.dump_for_kafka()),
            callback=delivery_report
        )
        producer.poll(0)
        logging.info(f"Produced new order message: {order.id}")
    except Exception as e:
        logging.error(f"Failed to produce new order message: {e}")