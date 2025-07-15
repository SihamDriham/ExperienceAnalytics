from kafka.kafka_users_reader import read_kafka_user_stream
from kafka.kafka_devices_reader import read_kafka_device_stream
from kafka.kafka_applications_reader import read_kafka_application_stream
from kafka.kafka_sentiments_reader import read_kafka_sentiment_stream

from dataCleaners.users_data_cleaner import clean_user_data
from dataCleaners.devices_data_cleaner import clean_device_data
from dataCleaners.applications_data_cleaner import clean_application_data
from dataCleaners.sentiments_data_cleaner import clean_sentiment_data

from processing.processing_alls import analyze_sentiment_tech_correlation, compute_digital_sentiment_score

from cassandra.cassandra_writer import write_to_cassandra
from spark.spark_session import create_spark_session

if __name__ == "__main__":
    spark = create_spark_session()

    # Lecture Kafka
    df_users_raw = read_kafka_user_stream(spark, "users-topic")
    df_apps_raw = read_kafka_application_stream(spark, "applications-topic")
    df_devices_raw = read_kafka_device_stream(spark, "devices-topic")
    df_sentiments_raw = read_kafka_sentiment_stream(spark, "sentiments-topic")

    # Nettoyage
    df_users = clean_user_data(df_users_raw)
    df_apps = clean_application_data(df_apps_raw)
    df_devices = clean_device_data(df_devices_raw)
    df_sentiments = clean_sentiment_data(df_sentiments_raw)

    # 1. Analyse de corrélation technique des sentiments
    df_correlation = analyze_sentiment_tech_correlation(df_users, df_apps, df_devices, df_sentiments)

    query_corr = df_correlation.writeStream \
        .outputMode("append") \
        .foreachBatch(lambda df, epoch_id: write_to_cassandra(df, epoch_id, "sentiment_tech_correlation")) \
        .option("checkpointLocation", "./checkpoints/sentiment_tech_correlation") \
        .trigger(processingTime="30 seconds") \
        .start()

    # 2. Taux de satisfaction numérique
    sentiment_scores = compute_digital_sentiment_score(df_users, df_devices, df_sentiments)

    query_dept = sentiment_scores["by_department"].writeStream \
        .outputMode("append") \
        .foreachBatch(lambda df, epoch_id: write_to_cassandra(df, epoch_id, "sentiment_by_department")) \
        .option("checkpointLocation", "./checkpoints/sentiment_by_department") \
        .trigger(processingTime="30 seconds") \
        .start()

    query_date = sentiment_scores["by_date"].writeStream \
        .outputMode("append") \
        .foreachBatch(lambda df, epoch_id: write_to_cassandra(df, epoch_id, "sentiment_by_date")) \
        .option("checkpointLocation", "./checkpoints/sentiment_by_date") \
        .trigger(processingTime="30 seconds") \
        .start()

    query_model = sentiment_scores["by_device_model"].writeStream \
        .outputMode("append") \
        .foreachBatch(lambda df, epoch_id: write_to_cassandra(df, epoch_id, "sentiment_by_device_model")) \
        .option("checkpointLocation", "./checkpoints/sentiment_by_device_model") \
        .trigger(processingTime="30 seconds") \
        .start()

    query_job = sentiment_scores["by_job_title"].writeStream \
        .outputMode("append") \
        .foreachBatch(lambda df, epoch_id: write_to_cassandra(df, epoch_id, "sentiment_by_job_title")) \
        .option("checkpointLocation", "./checkpoints/sentiment_by_job_title") \
        .trigger(processingTime="30 seconds") \
        .start()

    df_risk = predire_risky_users(df_users, df_devices, df_apps)
    query_risk = df_risk.writeStream \
        .outputMode("append") \
        .foreachBatch(lambda df, epoch_id: write_to_cassandra(df, epoch_id, "predire_risky_users")) \
        .option("checkpointLocation", "./checkpoints/predire_risky_users") \
        .trigger(processingTime="30 seconds") \
        .start()

    try:
        query_corr.awaitTermination()
        query_dept.awaitTermination()
        query_date.awaitTermination()
        query_model.awaitTermination()
        query_job.awaitTermination()
        query_risk.awaitTermination()
    except KeyboardInterrupt:
        print("Arrêt manuel du streaming...")
        query_corr.stop()
        query_dept.stop()
        query_date.stop()
        query_model.stop()
        query_job.stop()
        query_risk.stop()
        spark.stop()
