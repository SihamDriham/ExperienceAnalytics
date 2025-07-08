from pyspark.sql import SparkSession
from pyspark.sql.functions import *

# 1. Créer la SparkSession
spark = SparkSession.builder \
    .appName("KafkaDevicesStream") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# 2. Lire les données du topic Kafka 'devices'
df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:29092") \
    .option("subscribe", "devices-topic") \
    .option("startingOffsets", "earliest") \
    .load()

# 3. Convertir la colonne "value" (binaire) en string
df_string = df_raw.selectExpr("CAST(value AS STRING) as json_string")

# 4. Définir le schéma (à adapter si besoin)
device_schema = StructType() \
    .add("device_id", StringType()) \
    .add("hostname", StringType()) \
    .add("os", StringType()) \
    .add("model", StringType()) \
    .add("cpu_usage", StringType()) \
    .add("ram_usage", StringType()) \
    .add("disk_usage", StringType()) \
    .add("last_boot", StringType()) \
    .add("is_encrypted", StringType()) \
    .add("user_id", StringType()) 

# 5. Parser le JSON
df_parsed = df_string.select(from_json(col("json_string"), device_schema).alias("data")).select("data.*")

# 6. Nettoyage
df_clean = df_parsed \
    .filter(col("device_id").isNotNull()) \
    .filter(col("user_id").isNotNull()) \
    .withColumn("cpu_usage", col("cpu_usage").cast("double")) \
    .withColumn("ram_usage", col("ram_usage").cast("double")) \
    .withColumn("disk_usage", col("disk_usage").cast("double")) \
    .withColumn("is_encrypted", col("is_encrypted").cast("boolean")) \
    .withColumn("last_boot", to_timestamp("last_boot", "yyyy-MM-dd HH:mm:ss")) 

# 7. Affichage en streaming
query = df_clean.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", False) \
    .start()

query.awaitTermination()