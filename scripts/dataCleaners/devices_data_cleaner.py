from pyspark.sql.functions import col, to_timestamp, to_date

def clean_device_data(df):
    return df.filter(col("device_id").isNotNull()) \
        .filter(col("user_id").isNotNull()) \
        .withColumn("cpu_usage", col("cpu_usage").cast("double")) \
        .withColumn("ram_usage", col("ram_usage").cast("double")) \
        .withColumn("disk_usage", col("disk_usage").cast("double")) \
        .withColumn("is_encrypted", col("is_encrypted").cast("boolean")) \
        .withColumn("record_date", to_date("record_date", "yyyy-MM-dd")) \
        .withColumn("last_boot", to_timestamp("last_boot", "yyyy-MM-dd HH:mm:ss"))