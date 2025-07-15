from pyspark.sql.types import StructType, StringType

application_schema = StructType() \
    .add("id", StringType()) \
    .add("name", StringType()) \
    .add("compagny", StringType()) \
    .add("description", StringType()) \
    .add("platform", StringType()) \
    .add("storage_policy", StringType()) \
    .add("first_seen", StringType()) \
    .add("last_seen", StringType()) \
    .add("total_active_days", StringType()) \
    .add("database_usage", StringType()) \
    .add("crash_rate", StringType()) \
    .add("cpu_consumption", StringType()) \
    .add("ram_consumption", StringType()) \
    .add("user_id", StringType()) \
    .add("record_date", StringType())
