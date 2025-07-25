from pyspark.sql.functions import *

def compute_avg_usage(df_clean):
    return df_clean.groupBy("model", "record_date") \
        .agg(
            avg("cpu_usage").alias("avg_cpu_usage") ,
            avg("ram_usage").alias("avg_ram_usage") ,
            avg("disk_usage").alias("avg_disk_usage") 
        ) \
        .withColumnRenamed("record_date", "date") \
        .select("model", "date", "avg_cpu_usage", "avg_ram_usage", "avg_disk_usage")


def predire_risky_devices(df_devices):
    # Définir les bornes de janvier 2023
    # start_date = to_date(lit("2023-01-01"), "yyyy-MM-dd")
    # end_date = to_date(lit("2023-01-31"), "yyyy-MM-dd")

    # # Filtrage uniquement pour les données de janvier 2023
    # filtered_df = df_devices.filter(
    #     (col("record_date") >= start_date) & (col("record_date") <= end_date)
    # )

    last_month_df = df_devices.filter(col("record_date") >= date_sub(current_date(), 30))

    # Calcul des colonnes de risque
    scored_df = last_month_df \
        .withColumn("risk_encryption", when(col("is_encrypted") == False, 1).otherwise(0)) \
        .withColumn("risk_boot", when(col("last_boot").isNotNull() & (datediff(current_date(), col("last_boot")) > 90), 1).otherwise(0)) \
        .withColumn("risk_cpu", when(col("cpu_usage") > 85, 1).otherwise(0)) \
        .withColumn("risk_ram", when(col("ram_usage") > 85, 1).otherwise(0)) \
        .withColumn("score_risque",
                    col("risk_encryption") + col("risk_boot") + col("risk_cpu") + col("risk_ram"))

    # Filtrer les équipements à risque (score >= 2)
    df_risky_devices = scored_df.filter(col("score_risque") >= 2)

    # Résultat final
    df_result = df_risky_devices.select(
        col("device_id"),
        col("hostname"),
        col("os"),
        col("model"),
        col("score_risque").alias("score_risk"),
        col("record_date").alias("date")
    )

    return df_result
