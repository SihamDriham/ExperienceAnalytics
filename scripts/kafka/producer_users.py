import csv
import json
from kafka import KafkaProducer
import time

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')  
)

topic = 'users-topic'

with open('data/users.csv', 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        producer.send(topic, row)
        print(f"Message envoyé : {json.dumps(row, ensure_ascii=False)}")  
        time.sleep(1)

producer.flush()
producer.close()
