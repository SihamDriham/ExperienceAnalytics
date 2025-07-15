from pyspark.sql import SparkSession

def create_spark_session():
    spark = SparkSession.builder \
        .appName("KafkaUsersStream") \
        .config("spark.cassandra.connection.host", "cassandra") \
        .config("spark.cassandra.connection.port", "9042") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    return spark
