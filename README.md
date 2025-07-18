# Analyse de l’Expérience Numérique Utilisateur

## Objectif

Ce projet vise à mettre en place une solution analytique Big Data complète pour :

- Collecter des données issues de l’environnement numérique de travail (fichiers CSV)
- Les intégrer et les traiter en streaming et en batch
- Identifier les irritants et les anomalies dans l’usage des postes et applications
- Visualiser les KPI via des tableaux de bord dynamiques

---
## Architecture du Projet
<img width="882" height="666" alt="Image" src="https://github.com/user-attachments/assets/24d60689-b781-448e-a0f4-03fe9dfc6d6b" />

Le pipeline repose sur les composants suivants :

- **Kafka** : ingestion de données en streaming
- **Spark (Streaming & Batch)** : traitement des données en temps réel et en différé
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
## Traitement des données

- Utilisateurs actifs par département
- Moyenne des jours actifs par département
- Moyenne d'utilisation CPU/RAM par modèle d'équipement
- Nombre total de crashs par application
- Taux d’utilisation Windows vs Mac
- Pour chaque feedback négatif (score ≤ 2), détecter si un modèle d’équipement ou une application utilisée à cette même date est lié à une mauvaise expérience.
- analyser l’utilisation des applications (Somme de total_active_days par application, Moyenne de crash_rate par application, Top 5 des apps les plus lourdes)
- Taux de satisfaction numérique (Moyenne des score_sentiment par département (department), Évolution du score dans le temps (record_date), Score moyen par device model ou job_title)

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

### 4. Préparation de la base Cassandra

Avant de lancer les scripts Spark, il faut créer le keyspace et les tables nécessaires dans Cassandra.

1. Ouvrez `cqlsh` :
```bash
docker exec -it cassandra cqlsh
```

2. Créez le keyspace experience_analytics :
```bash
CREATE KEYSPACE experience_analytics
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
```

3. Sélectionnez le keyspace :
```bash
USE experience_analytics;
```

4. Créez les tables :
```bash
CREATE TABLE user_activity_by_department (
    department TEXT,
    date DATE,
    total_active_users INT,
    avg_active_days FLOAT,
    PRIMARY KEY ((department), date)
);
```
```bash
CREATE TABLE user_os_usage_stats (
   date DATE,
   windows_count INT,
   mac_count INT,
   windows_usage_rate FLOAT,
   mac_usage_rate FLOAT,
   total_users INT,
   PRIMARY KEY (date)
);
```

```bash
CREATE TABLE avg_usage_by_model (
    model text,
    date date,
    avg_cpu_usage float,
    avg_ram_usage float,
    avg_disk_usage float,
    PRIMARY KEY (model, date)
);
```

```bash
CREATE TABLE sum_crash_rate (
    id text,
    date date,
    sum_crash_rate float,
    PRIMARY KEY (id, date)
);
```

```bash
CREATE TABLE sentiment_tech_correlation (
    user_id TEXT,
    date DATE,
    model TEXT,
    os TEXT,
    total_active_days INT,
    cpu_usage FLOAT,
    ram_usage FLOAT,
    PRIMARY KEY ((user_id), date)
);
```

```bash
CREATE TABLE app_usage_stats (
    name text,
    record_date date,
    total_days_used int,
    PRIMARY KEY (name, record_date)
);
```

```bash
CREATE TABLE app_crash_stats (
    name text,
    record_date date,
    avg_crash_rate double,
    PRIMARY KEY (name, record_date)
);
```

```bash
CREATE TABLE heavy_apps (
    name text,
    record_date date,
    total_consumption double,
    PRIMARY KEY (record_date, total_consumption, name)
);
```

### 5. Lancer le job Spark 

Exécutez-le depuis PowerShell en mode administrateur avec la commande suivante:

```bash
docker exec -it spark-master bash
```
```bash
cd /opt/bitnami/spark/scripts
```
```bash
spark-submit spark/stream_users.py
spark-submit spark/stream_devices.py
spark-submit spark/stream_applications.py
spark-submit spark/stream_sentiments.py
spark-submit spark/stream_alls.py
```
**Note :** Exécutez ces commandes une par une, attendez que chaque job se lance correctement avant d’en lancer un autre.  
Pour arrêter un job Spark en cours, utilisez `CTRL + C`.

### 6. Visualisation avec Grafana

1. Connecte-toi sur http://localhost:3000 avec admin/admin
2. Va dans Ajouter une sources de données
3. Cherche Cassandra
4. Renseigne :
   - Contact points : cassandra 
   - Port : 9042
   - Keyspace : experience_analytics
5. Teste la connexion, elle doit réussir.
6. Créer un Dashboard avec une requête Cassandra
