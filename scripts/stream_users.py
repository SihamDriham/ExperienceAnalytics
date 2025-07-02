from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import StructType, StringType, TimestampType, IntegerType

# 1. SparkSession
spark = SparkSession.builder \
    .appName("KafkaUsersCleanStream") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# 2. Lecture depuis Kafka
df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:29092") \
    .option("subscribe", "users-topic") \
    .option("startingOffsets", "earliest") \
    .load()

# 3. Convertir le message Kafka en string
df_string = df_raw.selectExpr("CAST(value AS STRING) as json_string")

# 4. Définir le schéma (à adapter si besoin)
user_schema = StructType() \
    .add("id", StringType()) \
    .add("user_name", StringType()) \
    .add("full_name", StringType()) \
    .add("department", StringType()) \
    .add("job_title", StringType()) \
    .add("first_seen", StringType()) \
    .add("last_seen", StringType()) \
    .add("total_active_days", StringType()) \
    .add("number_of_days_since_last_seen", StringType()) \
    .add("seen_on_windows", StringType()) \
    .add("seen_on_mac_os", StringType()) \
    .add("user_uid", StringType())

# 5. Parser le JSON
df_parsed = df_string.select(from_json(col("json_string"), user_schema).alias("data")).select("data.*")

# 6. Nettoyage
df_clean = df_parsed \
    .filter(col("id").isNotNull()) \
    .filter(col("user_uid").isNotNull()) \
    .withColumn("total_active_days", col("total_active_days").cast("int")) \
    .withColumn("number_of_days_since_last_seen", col("number_of_days_since_last_seen").cast("int"))\
    .withColumn("seen_on_windows", col("seen_on_windows").cast("boolean")) \
    .withColumn("seen_on_mac_os", col("seen_on_mac_os").cast("boolean"))\
    .withColumn("first_seen", to_timestamp("first_seen", "yyyy-MM-dd HH:mm:ss")) \
    .withColumn("last_seen", to_timestamp("last_seen", "yyyy-MM-dd HH:mm:ss")) \
    .filter(col("first_seen").isNotNull() & col("last_seen").isNotNull()) \
    .filter(col("first_seen") < col("last_seen")) 

# 7. Affichage en streaming
query = df_clean.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", False) \
    .start()

query.awaitTermination()
