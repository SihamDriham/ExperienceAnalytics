from kafka.kafka_users_reader import read_kafka_stream
from dataCleaners.users_data_cleaner import clean_user_data
from processing.processing_users import compute_active_users_stats, compute_os_usage_stats
from cassandra.cassandra_writer import write_to_cassandra
from spark.spark_session import create_spark_session

if __name__ == "__main__":
    spark = create_spark_session()
    
    df_parsed = read_kafka_stream(spark, "users-topic")
    df_clean = clean_user_data(df_parsed)

    df_stats = compute_active_users_stats(df_clean)
    
    df_stats2 = compute_os_usage_stats(df_clean)

    query1 = df_stats.writeStream \
        .outputMode("update") \
        .foreachBatch(lambda df, epoch_id: write_to_cassandra(df, epoch_id, "user_activity_by_department")) \
        .option("checkpointLocation", "./checkpoints/user_activity_by_department_v2") \
        .trigger(processingTime='30 seconds') \
        .start()

    # Lancer le deuxième stream vers Cassandra (os_usage_stats)
    query2 = df_stats2.writeStream \
        .outputMode("update") \
        .foreachBatch(lambda df, epoch_id: write_to_cassandra(df, epoch_id, "user_os_usage_stats")) \
        .option("checkpointLocation", "./checkpoints/user_os_usage_stats_v1") \
        .trigger(processingTime='30 seconds') \
        .start()

    try:
        query1.awaitTermination()
        query2.awaitTermination()
    except KeyboardInterrupt:
        print("Arrêt manuel du streaming...")
        query1.stop()
        query2.stop()
        spark.stop()
