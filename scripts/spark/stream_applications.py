from kafka.kafka_applications_reader import read_kafka_application_stream
from dataCleaners.applications_data_cleaner import clean_application_data
from processing.processing_applications import sum_crash_rate, analyze_application_usage
from cassandra.cassandra_writer import write_to_cassandra
from spark.spark_session import create_spark_session

if __name__ == "__main__":
    spark = create_spark_session()
    
    df_parsed = read_kafka_application_stream(spark, "applications-topic")
    df_clean = clean_application_data(df_parsed)

    df_stats = sum_crash_rate(df_clean)
    results = analyze_application_usage(df_clean)

    query1 = df_stats.writeStream \
        .outputMode("update") \
        .foreachBatch(lambda df, epoch_id: write_to_cassandra(df, epoch_id, "sum_crash_rate")) \
        .option("checkpointLocation", "./checkpoints/sum_crash_rate") \
        .trigger(processingTime='30 seconds') \
        .start()

    # Streaming vers Cassandra pour chaque résultat
    query_usage = results["usage_by_app"].writeStream \
        .outputMode("update") \
        .foreachBatch(lambda df, epoch_id: write_to_cassandra(df, epoch_id, "app_usage_stats")) \
        .option("checkpointLocation", "./checkpoints/app_usage_stats") \
        .trigger(processingTime="30 seconds") \
        .start()

    query_crash = results["avg_crash_by_app"].writeStream \
        .outputMode("update") \
        .foreachBatch(lambda df, epoch_id: write_to_cassandra(df, epoch_id, "app_crash_stats")) \
        .option("checkpointLocation", "./checkpoints/app_crash_stats") \
        .trigger(processingTime="30 seconds") \
        .start()

    query_top5 = results["top5_heavy_apps"].writeStream \
        .outputMode("complete") \
        .foreachBatch(lambda df, epoch_id: write_to_cassandra(df, epoch_id, "heavy_apps")) \
        .option("checkpointLocation", "./checkpoints/heavy_apps") \
        .trigger(processingTime="30 seconds") \
        .start()

    try:
        query1.awaitTermination()
        query_usage.awaitTermination()
        query_crash.awaitTermination()
        query_top5.awaitTermination()
    except KeyboardInterrupt:
        print("Arrêt manuel du streaming...")
        query1.stop()
        spark.stop()
        query_usage.stop()
        query_crash.stop()
        query_top5.stop()
