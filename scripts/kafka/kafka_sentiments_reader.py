from pyspark.sql.functions import col, from_json
from schemas.schema_sentiments import sentiment_schema

def read_kafka_sentiment_stream(spark, topic_name):
    df_raw = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:29092") \
        .option("subscribe", topic_name) \
        .option("startingOffsets", "earliest") \
        .option("failOnDataLoss", "false") \
        .load()

    df_string = df_raw.selectExpr("CAST(value AS STRING) as json_string")
    df_parsed = df_string.select(from_json(col("json_string"), sentiment_schema).alias("data")).select("data.*")
    return df_parsed
