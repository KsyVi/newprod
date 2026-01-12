import json
import asyncio

from fastapi import HTTPException
from typing import Optional

from aiokafka import AIOKafkaProducer

from config import (
    KAFKA_BROKERS, 
    KAFKA_TOPIC,
)

class KafkaProducer:
    def __init__(self):
        self.producer = None
        self.topic = KAFKA_TOPIC
        self.bootstrap_servers = KAFKA_BROKERS

    async def start(self):
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                loop=asyncio.get_running_loop(),
                acks='all'
            )
            await self.producer.start()
            print("Продюсер успешно инициализирован")

        except Exception as e:
            print(f"Непредвиденная ошибка при инициализации Kafka: {e}")
            raise HTTPException(
                status_code=500,
                detail="Внутренняя ошибка сервера при инициализации Kafka"
            )


    async def stop(self):
        try:
            if self.producer:
                await self.producer.stop()
                print("Продюсер успешно остановлен")
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Непредвиденная ошибка при остановке: {e}"
            )


    async def send(self, message) -> bool:
        try:
            if not self.producer:
                raise HTTPException(
                    status_code=503,
                    detail="Продюсер не инициализирован"
                )
            message = json.dumps(message).encode('utf-8')
            try:
                await self.producer.send_and_wait(
                    topic=self.topic,
                    value=message
                )
                print(f"Сообщение успешно отправлено в топик {self.topic}")
                return True

            except Exception as e:
                print(f"Непредвиденная ошибка при отправке: {e}")
                raise HTTPException(
                    status_code=500,
                    detail="Внутренняя ошибка при отправке сообщения"
                )

        except HTTPException as e:
            raise e
        except Exception as e:
            print(f"Критическая ошибка: {e}")
            raise HTTPException(
                status_code=500,
                detail="Произошла неизвестная ошибка"
            )


kafka_producer = KafkaProducer()
