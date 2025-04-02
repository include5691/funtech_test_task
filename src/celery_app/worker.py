import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

import time
from celery import Celery
from src.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['src.celery_app.worker']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery_app.task(name="process_order")
def process_order_task(order_id: str, **kwargs):
    "Background task to process an order"
    try:
        logging.info(f"Processing order {order_id}")
        time.sleep(2)
        print(f"Order {order_id} processed")
        return f"Order {order_id} processed successfully"
    except Exception as e:
        logging.error(f"Error during processing order {order_id}: {e}", exc_info=True)
        raise