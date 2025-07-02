import csv
import json
from kafka import KafkaProducer
import time

# Initialisation du producteur Kafka avec un encodeur JSON
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Sérialise automatiquement en JSON
)

topic = 'devices-topic'

with open('data/devices.csv', 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        producer.send(topic, row)
        print(f"Message envoyé : {json.dumps(row, ensure_ascii=False)}")  # Affiche le message en JSON
        time.sleep(1)

producer.flush()
producer.close()
