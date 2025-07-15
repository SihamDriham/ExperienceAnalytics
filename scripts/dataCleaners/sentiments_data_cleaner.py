from pyspark.sql.functions import col, to_timestamp, to_date

def clean_sentiment_data(df):
    return df.filter(col("sentiment_id").isNotNull()) \
        .filter(col("user_id").isNotNull()) \
        .withColumn("record_date", to_date("record_date", "yyyy-MM-dd")) \
        .withColumn("score_sentiment", col("score_sentiment").cast("int"))