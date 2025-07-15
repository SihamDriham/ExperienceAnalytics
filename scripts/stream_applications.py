from pyspark.sql import SparkSession
from pyspark.sql.functions import *

# 1. Créer la SparkSession
spark = SparkSession.builder \
    .appName("KafkaApplicationsStream") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# 2. Lire les données du topic Kafka 'applications'
df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:29092") \
    .option("subscribe", "applications-topic") \
    .option("startingOffsets", "earliest") \
    .load()

# 3. Convertir la colonne "value" (binaire) en string
df_string = df_raw.selectExpr("CAST(value AS STRING) as json_string")


# 4. Définir le schéma (à adapter si besoin)
application_schema = StructType() \
    .add("id", StringType()) \
    .add("name", StringType()) \
    .add("compagny", StringType()) \
    .add("description", StringType()) \
    .add("platform", StringType()) \
    .add("storage_policy", StringType()) \
    .add("first_seen", StringType()) \
    .add("last_seen", StringType()) \
    .add("total_active_days", StringType()) \
    .add("database_usage", StringType()) \
    .add("crash_rate", StringType()) \
    .add("cpu_consumption", StringType()) \
    .add("ram_consumption", StringType()) \
    .add("user_id", StringType()) \
    .add("record_date", StringType())

# 5. Parser le JSON
df_parsed = df_string.select(from_json(col("json_string"), application_schema).alias("data")).select("data.*")

# 6. Nettoyage
df_clean = df_parsed \
    .filter(col("id").isNotNull()) \
    .filter(col("user_id").isNotNull()) \
    .withColumn("total_active_days", col("total_active_days").cast("int")) \
    .withColumn("database_usage", col("database_usage").cast("double")) \
    .withColumn("crash_rate", col("crash_rate").cast("double")) \
    .withColumn("cpu_consumption", col("cpu_consumption").cast("double")) \
    .withColumn("ram_consumption", col("ram_consumption").cast("double")) \
    .withColumn("first_seen", to_timestamp("first_seen", "yyyy-MM-dd HH:mm:ss")) \
    .withColumn("last_seen", to_timestamp("last_seen", "yyyy-MM-dd HH:mm:ss")) \
    .withColumn("record_date", to_date("record_date", "yyyy-MM-dd")) \
    .filter(col("first_seen").isNotNull() & col("last_seen").isNotNull()) \
    .filter(col("first_seen") < col("last_seen")) 

# 7. Affichage en streaming
query = df_clean.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", False) \
    .start()

query.awaitTermination()
