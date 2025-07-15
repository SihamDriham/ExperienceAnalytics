from pyspark.sql.functions import desc, col, sum, avg, count, when, current_date, lit, current_timestamp

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
