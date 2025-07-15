def write_to_cassandra(df, epoch_id, table_name):
    print(f"Traitement du batch {epoch_id}")
    try:
        df.write \
            .format("org.apache.spark.sql.cassandra") \
            .mode("append") \
            .option("keyspace", "experience_analytics") \
            .option("table", table_name) \
            .option("spark.cassandra.output.ttl", "864000") \
            .save()
        print(f"Batch {epoch_id} écrit avec succès dans {table_name}")
    except Exception as e:
        print(f"Erreur lors de l'écriture du batch {epoch_id}: {str(e)}")
