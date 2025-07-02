@echo off
echo ====================================================
echo Lancement du job Spark avec docker exec
echo ====================================================

docker exec -it spark-master bash -c "export USER=spark && export LOGNAME=spark && export USERNAME=spark && export HADOOP_USER_NAME=spark && export SPARK_USER=spark && echo Utilisateur actuel: && whoami && echo ID utilisateur: && id && spark-submit --master spark://spark-master:7077 --deploy-mode client --conf spark.jars.ivy=/tmp/.ivy2 --conf spark.hadoop.fs.defaultFS=file:/// --conf spark.hadoop.hadoop.security.authentication=simple --conf spark.hadoop.security.authorization=false --conf spark.hadoop.HADOOP_USER_NAME=spark --conf spark.driver.host=spark-master --conf spark.driver.bindAddress=0.0.0.0 --conf spark.sql.streaming.checkpointLocation=/opt/bitnami/spark/data/checkpoints --conf spark.hadoop.ipc.client.fallback-to-simple-auth-allowed=true --conf spark.hadoop.dfs.permissions.enabled=false --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 --verbose /opt/bitnami/spark/scripts/stream_devices.py"

echo.
echo Script terminé
pause
