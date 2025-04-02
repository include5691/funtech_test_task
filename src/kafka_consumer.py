from dotenv import load_dotenv
load_dotenv()

import logging
from confluent_kafka import Consumer
from src.core.config import settings
from src.celery_app.worker import process_order_task

logging.basicConfig(level=logging.INFO)

config = {
    'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
    'group.id': 'order_processing_group',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(config)

def start_consume():
    try:
        consumer.subscribe([settings.KAFKA_NEW_ORDERS_TOPIC])
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                logging.error(f"Consumer error: {msg.error()}")
                continue
            message_value = msg.value().decode()
            message_key = msg.key().decode()
            logging.info(f"Received message: {message_key} with value: {message_value}")
            task_result = process_order_task.delay(order_id=message_key, order_body=message_value)
            logging.info(f"Task result: {task_result}")
    except Exception as e:
        logging.error(f"An unexpected error occurred in the consumer: {e}", exc_info=True)
    finally:
        if consumer is not None:
            logging.info("Closing Kafka consumer...")
            consumer.close() 
            logging.info("Kafka consumer closed.")

if __name__ == "__main__":
    start_consume()