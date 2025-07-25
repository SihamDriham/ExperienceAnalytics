from pyspark.sql.functions import *

def sum_crash_rate(df_clean):
    return df_clean.groupBy("id", "record_date") \
        .agg(
            sum("crash_rate").alias("sum_crash_rate") 
        ) \
        .withColumnRenamed("record_date", "date") \
        .select("id", "date", "sum_crash_rate")


def analyze_application_usage(df_apps):

    # 1. Somme de total_active_days par application (par nom d'app)
    usage_by_app = df_apps.groupBy("name", "record_date") \
        .agg(sum("total_active_days").alias("total_days_used"))

    # 2. Moyenne de crash_rate par application
    avg_crash_by_app = df_apps.groupBy("name", "record_date") \
        .agg(avg("crash_rate").alias("avg_crash_rate"))

    # 4. Top 5 des apps les plus lourdes (RAM + CPU combinés)
    heavy_apps = df_apps.withColumn("total_consumption", col("cpu_consumption") + col("ram_consumption")) \
        .groupBy("name", "record_date") \
        .agg(avg("total_consumption").alias("total_consumption")) \
        .orderBy(desc("total_consumption")) \
        .limit(5)

    return {
        "usage_by_app": usage_by_app,
        "avg_crash_by_app": avg_crash_by_app,
        "top5_heavy_apps": heavy_apps
    }


def predire_risky_apps(df_apps):

    # Définir les bornes de janvier 2023
    # start_date = to_date(lit("2023-01-01"), "yyyy-MM-dd")
    # end_date = to_date(lit("2023-01-31"), "yyyy-MM-dd")

    # # Filtrage uniquement pour les données de janvier 2023
    # filtered_df = df_apps.filter(
    #     (col("record_date") >= start_date) & (col("record_date") <= end_date)
    # )

    last_month_df = df_apps.filter(col("record_date") >= date_sub(current_date(), 30))
    
    score_risque = last_month_df.withColumn("risk_cpu", when(col("cpu_consumption") > 80, 1).otherwise(0)) \
        .withColumn("risk_ram", when(col("ram_consumption") > 80, 1).otherwise(0))\
        .withColumn("risk_crash", when(col("crash_rate") > 0.3, 1).otherwise(0)) \
        .withColumn("score_risque",
                col("risk_cpu") + col("risk_ram") + col("risk_crash"))
    
    df_risky_users = score_risque.filter(col("score_risque") >= 2)

    df_result = df_risky_users.select(
        col("id").alias("app_id"),
        col("name"),
        col("compagny"),
        col("description"),
        col("platform"),
        col("score_risque").alias("score_risk"),
        col("record_date").alias("date")
    )

    return df_result
