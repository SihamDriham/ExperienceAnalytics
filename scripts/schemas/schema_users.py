from pyspark.sql.types import StructType, StringType

user_schema = StructType() \
    .add("id", StringType()) \
    .add("user_name", StringType()) \
    .add("full_name", StringType()) \
    .add("department", StringType()) \
    .add("job_title", StringType()) \
    .add("first_seen", StringType()) \
    .add("last_seen", StringType()) \
    .add("total_active_days", StringType()) \
    .add("number_of_days_since_last_seen", StringType()) \
    .add("seen_on_windows", StringType()) \
    .add("seen_on_mac_os", StringType()) \
    .add("user_uid", StringType()) \
    .add("record_date", StringType())
