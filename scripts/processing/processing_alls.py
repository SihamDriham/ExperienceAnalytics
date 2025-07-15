from pyspark.sql.functions import *

def analyze_sentiment_tech_correlation(df_users, df_apps, df_devices, df_sentiments):
    df_negative = df_sentiments.filter(col("score_sentiment") <= 2)

    s = df_negative.alias("s")
    d = df_devices.alias("d")
    a = df_apps.alias("a")
    u = df_users.alias("u")

    df_join1 = s.join(
        d,
        (col("s.user_id") == col("d.user_id")) &
        (col("s.record_date") == col("d.record_date")),
        how="inner"
    )

    df_join2 = df_join1.join(
        a,
        (col("s.user_id") == col("a.user_id")) &
        (col("s.record_date") == col("a.record_date")),
        how="inner"
    )

    df_full = df_join2.join(
        u,
        col("s.user_id") == col("u.id"),
        how="inner"
    )

    df_result = df_full.select(
        col("s.user_id").alias("user_id"),
        col("s.record_date").alias("date"),
        col("d.model").alias("model"),
        col("d.os").alias("os"),
        col("a.total_active_days").alias("total_active_days"),
        col("d.cpu_usage").alias("cpu_usage"),
        col("d.ram_usage").alias("ram_usage")
    )

    return df_result

def compute_digital_sentiment_score(df_users, df_devices, df_sentiments):
    # Joindre les sentiments avec les utilisateurs
    df_join_user = df_sentiments.alias("s").join(
        df_users.alias("u"),
        (col("s.user_id") == col("u.id")) & (col("s.record_date") == col("u.record_date")),
        how="inner"
    )

    # Joindre avec les appareils pour avoir le model
    df_full = df_join_user.join(
        df_devices.alias("d"),
        (col("s.user_id") == col("d.user_id")) & (col("s.record_date") == col("d.record_date")),
        how="inner"
    )

    # Moyenne par département + date
    sentiment_by_department = df_full.groupBy("u.department", "s.record_date") \
        .agg(avg("score_sentiment").alias("avg_sentiment_score")) \
        .withColumnRenamed("department", "group") \
        .withColumnRenamed("record_date", "date")

    # Moyenne par date seule (inchangé)
    sentiment_by_date = df_full.groupBy("s.record_date") \
        .agg(avg("score_sentiment").alias("avg_sentiment_score")) \
        .withColumnRenamed("record_date", "date")

    # Moyenne par modèle d'appareil + date
    sentiment_by_device_model = df_full.groupBy("d.model", "s.record_date") \
        .agg(avg("score_sentiment").alias("avg_sentiment_score")) \
        .withColumnRenamed("model", "group") \
        .withColumnRenamed("record_date", "date")

    # Moyenne par titre de poste + date
    sentiment_by_job_title = df_full.groupBy("u.job_title", "s.record_date") \
        .agg(avg("score_sentiment").alias("avg_sentiment_score")) \
        .withColumnRenamed("job_title", "group") \
        .withColumnRenamed("record_date", "date")

    return {
        "by_department": sentiment_by_department,
        "by_date": sentiment_by_date,
        "by_device_model": sentiment_by_device_model,
        "by_job_title": sentiment_by_job_title
    }

# def predire_risky_users(df_users, df_devices, df_apps):

#     df_join_user = df_users.alias("u").join(
#         df_devices.alias("d"),
#         (col("u.id") == col("d.user_id")) & (col("u.record_date") == col("d.record_date")),
#         how="inner"
#     )

#     df_full = df_join_user.join(
#         df_apps.alias("a"),
#         (col("u.id") == col("a.user_id")) & (col("u.record_date") == col("a.record_date")),
#         how="inner"
#     )

#     last_month_df = df_full.filter(col("record_date") >= date_sub(current_date(), 30))

#     score_risque = last_month_df.withColumn("risk_cpu", when(col("d.cpu_usage") > 85, 1).otherwise(0)) \
#         .withColumn("risk_ram", when(col("d.ram_usage") > 85, 1).otherwise(0))\
#         .withColumn("risk_crash", when(col("a.crash_rate") > 0.3, 1).otherwise(0)) \
#         .withColumn("risk_encryption", when(col("d.is_encrypted") == False, 1).otherwise(0)) \
#         .withColumn("score_risque",
#                 col("risk_cpu") + col("risk_ram") + col("risk_crash") + col("risk_encryption"))
    
#     df_risky_users = score_risk.filter(col("score_risque") >= 2)

#     df_result = df_risky_users.select(
#         col("u.id").alias("user_id"),
#         col("u.full_name"),
#         col("u.department"),
#         col("u.job_title"),
#         col("score_risque").alias("score_risk"),
#         col("u.record_date").alias("date")
#     )

#     return df_result


def predire_risky_users(df_users, df_devices, df_apps):

    # Définir les bornes de janvier 2023
    start_date = to_date(lit("2023-01-01"), "yyyy-MM-dd")
    end_date = to_date(lit("2023-01-31"), "yyyy-MM-dd")

    df_join_user = df_users.alias("u").join(
        df_devices.alias("d"),
        (col("u.id") == col("d.user_id")) & (col("u.record_date") == col("d.record_date")),
        how="inner"
    )

    df_full = df_join_user.join(
        df_apps.alias("a"),
        (col("u.id") == col("a.user_id")) & (col("u.record_date") == col("a.record_date")),
        how="inner"
    )

    # Filtrage uniquement pour les données de janvier 2023
    filtered_df = df_full.filter(
        (col("u.record_date") >= start_date) & (col("u.record_date") <= end_date)
    )

    score_risque = filtered_df.withColumn("risk_cpu", when(col("d.cpu_usage") > 85, 1).otherwise(0)) \
        .withColumn("risk_ram", when(col("d.ram_usage") > 85, 1).otherwise(0))\
        .withColumn("risk_crash", when(col("a.crash_rate") > 0.3, 1).otherwise(0)) \
        .withColumn("risk_encryption", when(col("d.is_encrypted") == False, 1).otherwise(0)) \
        .withColumn("score_risque",
                col("risk_cpu") + col("risk_ram") + col("risk_crash") + col("risk_encryption"))
    
    df_risky_users = score_risk.filter(col("score_risque") >= 2)

    df_result = df_risky_users.select(
        col("u.id").alias("user_id"),
        col("u.full_name"),
        col("u.department"),
        col("u.job_title"),
        col("score_risque").alias("score_risk"),
        col("u.record_date").alias("date")
    )

    return df_result


