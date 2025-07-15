from pyspark.sql.functions import col, to_timestamp, to_date

def clean_application_data(df):
    return df.filter(col("id").isNotNull()) \
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