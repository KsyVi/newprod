import os

from dotenv import load_dotenv

load_dotenv()  

DATABASE_URL = os.getenv("DATABASE_URL")
USE_SEARCH_SERVICE = os.getenv("USE_SEARCH_SERVICE", "true").lower() == "true"


KAFKA_BROKERS = "адрес_твоего_кафка:9092"
KAFKA_TOPIC = "имя_топика_куда_отправлять"
KAFKA_USERNAME = "твой_юзер_если_нужен"
KAFKA_PASSWORD = "твой_пароль_если_нужен"
cert_path = "/путь/к/сертификату/ca.pem"
KAFKA_SSL_CHECK_HOSTNAME = False  # или True, если нужно


