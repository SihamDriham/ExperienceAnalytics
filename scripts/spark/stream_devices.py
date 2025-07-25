from kafka.kafka_devices_reader import read_kafka_device_stream
from dataCleaners.devices_data_cleaner import clean_device_data
from processing.processing_devices import compute_avg_usage, predire_risky_devices
from cassandra.cassandra_writer import write_to_cassandra
from spark.spark_session import create_spark_session

# def debug_batch_processing(df, epoch_id):
#     print(f"=== DEBUT DEBUG BATCH {epoch_id} ===")
    
#     # Afficher les données
#     print("Données du batch:")
#     df.show(2, truncate=False)
    
#     # Essayer d'écrire dans Cassandra
#     try:
#         write_to_cassandra(df, epoch_id, "avg_usage_by_model")
#     except Exception as e:
#         print(f"Erreur dans write_to_cassandra: {str(e)}")
#         import traceback
#         traceback.print_exc()
    
#     print(f"=== FIN DEBUG BATCH {epoch_id} ===")

# if __name__ == "__main__":
#     spark = create_spark_session()
    
#     df_parsed = read_kafka_device_stream(spark, "devices-topic")
#     df_clean = clean_device_data(df_parsed)
#     df_stats = compute_avg_usage(df_clean)

#     # Un seul stream pour debug
#     query = df_stats.writeStream \
#         .outputMode("update") \
#         .foreachBatch(debug_batch_processing) \
#         .option("checkpointLocation", "./checkpoints/avg_usage_by_model") \
#         .trigger(processingTime='30 seconds') \
#         .start()

#     try:
#         print("Démarrage du stream de debug...")
#         query.awaitTermination()
#     except KeyboardInterrupt:
#         print("Arrêt manuel du streaming...")
#         query.stop()
#         spark.stop()


if __name__ == "__main__":
    spark = create_spark_session()
    
    df_parsed = read_kafka_device_stream(spark, "devices-topic")
    df_clean = clean_device_data(df_parsed)

    df_stats = compute_avg_usage(df_clean)
    
    df_stats2 = predire_risky_devices(df_clean)

    query1 = df_stats.writeStream \
        .outputMode("update") \
        .foreachBatch(lambda df, epoch_id: write_to_cassandra(df, epoch_id, "avg_usage_by_model")) \
        .option("checkpointLocation", "./checkpoints/avg_usage_by_model") \
        .trigger(processingTime='30 seconds') \
        .start()

    # Lancer le deuxième stream vers Cassandra (os_usage_stats)
    query2 = df_stats2.writeStream \
        .outputMode("update") \
        .foreachBatch(lambda df, epoch_id: write_to_cassandra(df, epoch_id, "risky_devices")) \
        .option("checkpointLocation", "./checkpoints/risky_devices") \
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
