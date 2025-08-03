import json
import ssl

from typing import Optional

from aiokafka import AIOKafkaProducer

from config import (
    KAFKA_BROKERS, 
    KAFKA_TOPIC,
    KAFKA_USERNAME,
    KAFKA_PASSWORD,
    cert_path,
    KAFKA_SSL_CHECK_HOSTNAME
)

class KafkaProducer:
    def __init__(self):
        self.producer: Optional[AIOKafkaProducer] = None

    async def init(self):
        # SSL/TLS настройки
        ssl_context = ssl.create_default_context(cafile=cert_path)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE if not KAFKA_SSL_CHECK_HOSTNAME else ssl.CERT_REQUIRED

        # Конфигурация для подключения к Kafka
        conf = {
            'bootstrap_servers': KAFKA_BROKERS,
            'security_protocol': 'SASL_SSL',
            'sasl_mechanism': 'PLAIN',
            'sasl_plain_username': KAFKA_USERNAME,
            'sasl_plain_password': KAFKA_PASSWORD,
            'ssl_context': ssl_context,
        }
        self.producer = AIOKafkaProducer(**conf)
        try:
            await self.producer.start()
        except Exception as e:
            await self.close()  # Ensure the producer is stopped if initialization fails
            raise RuntimeError(f"Failed to start Kafka producer: {e}")

    async def close(self):
        if self.producer:
            try:
                await self.producer.stop()
            except Exception as e:
                raise RuntimeError(f"Failed to stop Kafka producer: {e}")

    async def send_search_task(self, search_query):
        message = json.dumps(search_query).encode('utf-8')
        try:
            await self.producer.send_and_wait(KAFKA_TOPIC, message)
            print(f"Sent message: {message}")
        except Exception as e:
            raise RuntimeError(f"Error sending message to Kafka: {e}")

    async def check_health(self):
        # Check if the producer is initialized and started
        if not self.producer or not self.producer._closed:
            return True  
        return False 

kafka_producer = KafkaProducer()
