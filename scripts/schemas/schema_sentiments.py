from pyspark.sql.types import StructType, StringType

sentiment_schema = StructType() \
    .add("sentiment_id", StringType()) \
    .add("user_id", StringType()) \
    .add("campaign_name", StringType()) \
    .add("question", StringType()) \
    .add("response", StringType()) \
    .add("score_sentiment", StringType()) \
    .add("date_response", StringType()) \
    .add("comment", StringType()) \
    .add("record_date", StringType())