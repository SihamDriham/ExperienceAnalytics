from pyspark.sql.functions import col, sum, avg, count, when, current_date, lit, current_timestamp

def compute_active_users_stats(df_clean):
    df_actifs = df_clean.filter(col("number_of_days_since_last_seen") < 6)
    return df_actifs.groupBy("department", "record_date") \
        .agg(
            count("*").alias("total_active_users"),
            avg("total_active_days").alias("avg_active_days")
        ) \
        .withColumnRenamed("record_date", "date") \
        .select("department", "date", "total_active_users", "avg_active_days")

def compute_os_usage_stats(df_clean):
    return df_clean.groupBy("record_date") \
        .agg(
            sum(when(col("seen_on_windows") == True, 1).otherwise(0)).alias("windows_count"),
            sum(when(col("seen_on_mac_os") == True, 1).otherwise(0)).alias("mac_count"),
            count("*").alias("total_users")
        )\
        .withColumnRenamed("record_date", "date") \
        .withColumn("windows_usage_rate", col("windows_count") / col("total_users")) \
        .withColumn("mac_usage_rate", col("mac_count") / col("total_users")) \
        .select("date", "windows_count", "mac_count", "total_users", "windows_usage_rate", "mac_usage_rate")

