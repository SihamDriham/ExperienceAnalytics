from pyspark.sql import SparkSession
from pyspark.sql.functions import *

# 1. Créer la SparkSession
spark = SparkSession.builder \
    .appName("KafkaSentimentsStream") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# 2. Lire les données du topic Kafka 'sentiments'
df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:29092") \
    .option("subscribe", "sentiments-topic") \
    .option("startingOffsets", "earliest") \
    .load()

# 3. Convertir la colonne "value" (binaire) en string
df_string = df_raw.selectExpr("CAST(value AS STRING) as json_string")

# 4. Définir le schéma (à adapter si besoin)
sentiment_schema = StructType() \
    .add("sentiment_id", StringType()) \
    .add("user_id", StringType()) \
    .add("campaign_name", StringType()) \
    .add("question", StringType()) \
    .add("response", StringType()) \
    .add("score_sentiment", StringType()) \
    .add("date_response", StringType()) \
    .add("comment", StringType()) 

# 5. Parser le JSON
df_parsed = df_string.select(from_json(col("json_string"), sentiment_schema).alias("data")).select("data.*")

# 6. Nettoyage
df_clean = df_parsed \
    .filter(col("sentiment_id").isNotNull()) \
    .filter(col("user_id").isNotNull()) \
    .withColumn("score_sentiment", col("score_sentiment").cast("int"))

# 7. Affichage en streaming
query = df_clean.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", False) \
    .start()

query.awaitTermination()

