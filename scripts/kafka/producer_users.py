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

# Lire le fichier CSV en mémoire
# rows = []
# with open('data/users.csv', 'r', encoding='utf-8') as file:
#     reader = csv.DictReader(file)
#     for row in reader:
#         # convertir year et month en int pour comparer
#         row['year'] = int(row['year'])
#         row['month'] = int(row['month'])
#         rows.append(row)

# # Trouver la dernière année et mois présents dans le fichier
# last_year = max(r['year'] for r in rows)
# last_month = max(r['month'] for r in rows if r['year'] == last_year)

# #print(f"📌 Envoi uniquement des données de {last_month}/{last_year}")

# # Envoyer seulement les lignes du dernier mois
# for row in rows:
#     if row['year'] == last_year and row['month'] == last_month:
#         producer.send(topic, row)
#         print(f"Message envoyé : {json.dumps(row, ensure_ascii=False)}")
#         time.sleep(1)

producer.flush()
producer.close()
