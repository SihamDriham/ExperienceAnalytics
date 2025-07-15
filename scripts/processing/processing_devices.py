from pyspark.sql.functions import col, sum, avg, count, when, current_date, lit, current_timestamp

def compute_avg_usage(df_clean):
    return df_clean.groupBy("model", "record_date") \
        .agg(
            avg("cpu_usage").alias("avg_cpu_usage") ,
            avg("ram_usage").alias("avg_ram_usage") ,
            avg("disk_usage").alias("avg_disk_usage") 
        ) \
        .withColumnRenamed("record_date", "date") \
        .select("model", "date", "avg_cpu_usage", "avg_ram_usage", "avg_disk_usage")