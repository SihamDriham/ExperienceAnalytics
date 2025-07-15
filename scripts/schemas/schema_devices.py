from pyspark.sql.types import StructType, StringType

device_schema = StructType() \
    .add("device_id", StringType()) \
    .add("hostname", StringType()) \
    .add("os", StringType()) \
    .add("model", StringType()) \
    .add("cpu_usage", StringType()) \
    .add("ram_usage", StringType()) \
    .add("disk_usage", StringType()) \
    .add("last_boot", StringType()) \
    .add("is_encrypted", StringType()) \
    .add("user_id", StringType()) \
    .add("record_date", StringType())