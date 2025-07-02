# Analyse de l’Expérience Numérique Utilisateur

## Objectif

Ce projet vise à mettre en place une solution analytique Big Data complète pour :

- Collecter des données issues de l’environnement numérique de travail (fichiers CSV)
- Les intégrer et les traiter en streaming et en batch
- Identifier les irritants et les anomalies dans l’usage des postes et applications
- Visualiser les KPI via des tableaux de bord dynamiques

---
## Architecture du Projet
![Image](https://github.com/user-attachments/assets/b498620c-19ee-492b-9ac5-1f0753f6b0a5)

Le pipeline repose sur les composants suivants :

- **Kafka** : ingestion de données en streaming
- **Spark (Streaming & Batch)** : traitement des données en temps réel et en différé
- **HDFS** : stockage des données brutes
- **Cassandra** : stockage des données 
- **Grafana** : visualisation et reporting
- **Airflow** : orchestration des traitements batch

---
## Structure des données

### 1. `users.csv` – Informations sur les employés
- `id`, `user_name`, `full_name`, `department`, `job_title`, `first_seen`, `last_seen`, `total_active_days`, `number_of_days_since_last_seen`, `seen_on_windows`, `seen_on_mac_os`, `user_uid` .
- **But** : analyser la présence, les comportements et les contextes métiers.

### 2. `devices.csv` – Équipements utilisés
- `device_id`, `hostname`, `os`, `model`, `cpu_usage`, `ram_usage`, `disk_usage`, `last_boot`, `is_encrypted`, `user_id`.
- **But** : détecter les problèmes techniques ou matériels.

### 3. `applications.csv` – Utilisation des applications
- `id`, `name`, `compagny`, `description`, `platform`, `storage_policy`, `first_seen`, `last_seen`, `total_active_days`, `database_usage`, `crash_rate`, `cpu_consumption`, `ram_consumption`, `user_id`.
- **But** : analyser les performances applicatives.

### 4. `sentiments.csv` – Feedback utilisateur
- `sentiment_id`, `user_id`, `campaign_name`, `question`, `response`, `score_sentiment`, `date_response`, `comment`.
- **But** : mesurer la satisfaction perçue.

---
## Nettoyage des données

### 1. `users.csv`
- Supprimer utilisateurs sans id et user_uid

- Vérifier que first_seen < last_seen

- Uniformiser les dates au format yyyy-MM-dd HH:mm:ss

### 2. `devices.csv`

- Supprimer devices sans device_id et user_id

- Uniformiser les dates au format yyyy-MM-dd HH:mm:ss
  
### 3. `applications.csv`

- Supprimer applications sans id et user_id

- Vérifier que first_seen < last_seen

- Uniformiser les dates au format yyyy-MM-dd HH:mm:ss

### 4. `sentiments.csv`

- Supprimer sentiments sans id et user_id

---
## Étapes de Mise en Place

### 1. Lancer l’environnement Docker

```bash
docker-compose up -d
```
### 2. Créer les topics Kafka

```bash
docker exec -it kafka kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic users-topic
docker exec -it kafka kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic devices-topic
docker exec -it kafka kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic applications-topic
docker exec -it kafka kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic sentiments-topic
```

### 3. Lancer le Producer Python pour envoyer des données sur Kafka

```bash
python scripts/producer_users.py
python scripts/producer_devices.py
python scripts/producer_applications.py
python scripts/producer_sentiments.py
```

### 4. Lancer le job Spark Streaming pour consommer les données Kafka

Exécutez-le depuis PowerShell en mode administrateur avec la commande suivante:

```bash
.\run_spark_users.bat
.\run_spark_devices.bat
.\run_spark_applications.bat
.\run_spark_sentiments.bat
```
