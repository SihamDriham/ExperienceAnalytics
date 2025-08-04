from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
import logging

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2025, 6, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=10),
    'catchup': False,
}

# DAG principal mensuel
dag = DAG(
    'monthly_data_pipeline',
    default_args=default_args,
    description='Pipeline mensuel : Kafka producers + Spark processing + Cassandra storage',
    schedule_interval='0 2 1 * *',  # Le 1er de chaque mois à 2h du matin
    max_active_runs=1,
    tags=['monthly', 'kafka', 'spark', 'cassandra'],
)

def log_pipeline_start():
    """Log du début du pipeline"""
    logging.info("=== DÉBUT DU PIPELINE MENSUEL ===")
    logging.info(f"Date d'exécution: {datetime.now()}")
    logging.info("Étapes: Kafka Producers → Spark Processing → Cassandra Storage")
    return "PIPELINE_STARTED"

def log_pipeline_end():
    """Log de fin du pipeline"""
    logging.info("=== FIN DU PIPELINE MENSUEL ===")
    logging.info(f"Pipeline terminé avec succès à: {datetime.now()}")
    return "PIPELINE_COMPLETED"

# =============================================================================
# DÉFINITION DES TÂCHES
# =============================================================================

# Début du pipeline
start_task = DummyOperator(
    task_id='start_monthly_pipeline',
    dag=dag,
)

log_start_task = PythonOperator(
    task_id='log_pipeline_start',
    python_callable=log_pipeline_start,
    dag=dag,
)

# =============================================================================
# PHASE 1: KAFKA PRODUCERS - Lecture des fichiers CSV et envoi vers Kafka
# =============================================================================

produce_users_task = BashOperator(
    task_id='kafka_produce_users',
    bash_command='cd /opt/airflow && python scripts/kafka/producer_users.py',
    dag=dag,
)

produce_devices_task = BashOperator(
    task_id='kafka_produce_devices',
    bash_command='cd /opt/airflow && python scripts/kafka/producer_devices.py',
    dag=dag,
)

produce_applications_task = BashOperator(
    task_id='kafka_produce_applications',
    bash_command='cd /opt/airflow && python scripts/kafka/producer_applications.py',
    dag=dag,
)

produce_sentiments_task = BashOperator(
    task_id='kafka_produce_sentiments',
    bash_command='cd /opt/airflow && python scripts/kafka/producer_sentiments.py',
    dag=dag,
)

# Point de synchronisation après les producers
producers_complete = DummyOperator(
    task_id='kafka_producers_complete',
    dag=dag,
)

# =============================================================================
# PHASE 2: SPARK PROCESSING - Traitement des données depuis Kafka
# =============================================================================

# Attendre un peu pour que tous les messages soient dans Kafka
wait_for_kafka = BashOperator(
    task_id='wait_for_kafka_messages',
    bash_command='echo "Attente de 30 secondes pour que tous les messages soient dans Kafka..." && sleep 30',
    dag=dag,
)

# Traitements Spark individuels
spark_users_task = BashOperator(
    task_id='spark_process_users',
    bash_command='cd /opt/airflow && spark-submit spark/stream_users.py',
    dag=dag,
)

spark_devices_task = BashOperator(
    task_id='spark_process_devices',
    bash_command='cd /opt/airflow && spark-submit spark/stream_devices.py',
    dag=dag,
)

spark_applications_task = BashOperator(
    task_id='spark_process_applications',
    bash_command='cd /opt/airflow && spark-submit spark/stream_applications.py',
    dag=dag,
)

spark_alls_task = BashOperator(
    task_id='spark_process_alls',
    bash_command='cd /opt/airflow && spark-submit spark/stream_alls.py',
    dag=dag,
)

# Point de synchronisation après les traitements individuels
individual_processing_complete = DummyOperator(
    task_id='individual_processing_complete',
    dag=dag,
)

# # Traitement global final
# spark_all_task = BashOperator(
#     task_id='spark_process_all',
#     bash_command='cd /opt/airflow && spark-submit spark/stream_alls.py',
#     dag=dag,
# )

# =============================================================================
# PHASE 3: FINALISATION
# =============================================================================

log_end_task = PythonOperator(
    task_id='log_pipeline_end',
    python_callable=log_pipeline_end,
    dag=dag,
)

end_task = DummyOperator(
    task_id='end_monthly_pipeline',
    dag=dag,
)

# =============================================================================
# DÉFINITION DES DÉPENDANCES
# =============================================================================

# Phase 1: Démarrage et Kafka Producers
start_task >> log_start_task

# Les 4 producers Kafka s'exécutent en parallèle
log_start_task >> [
    produce_users_task,
    produce_devices_task,
    produce_applications_task,
    produce_sentiments_task
]

# Synchronisation après les producers
[
    produce_users_task,
    produce_devices_task,
    produce_applications_task,
    produce_sentiments_task
] >> producers_complete

# Phase 2: Attente puis traitements Spark
producers_complete >> wait_for_kafka

# Les 4 traitements Spark s'exécutent en parallèle
wait_for_kafka >> [
    spark_users_task,
    spark_devices_task,
    spark_applications_task,
    spark_alls_task
]

# Synchronisation après les traitements individuels
[
    spark_users_task,
    spark_devices_task,
    spark_applications_task,
    spark_alls_task
] >> individual_processing_complete

# Traitement global final
# individual_processing_complete >> spark_all_task

# Phase 3: Finalisation
# spark_all_task >> log_end_task >> end_task
individual_processing_complete >> log_end_task >> end_task