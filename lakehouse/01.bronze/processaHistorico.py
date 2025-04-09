# Databricks notebook source
# MAGIC %md
# MAGIC
# MAGIC ## Objetivo: Esse notebook faz o processamento dos dados históricos que se encontram na camada landing
# MAGIC
# MAGIC ![Arquiteture de Ingestão Landing - Bronze](https://github.com/douglas-engenheirodedados/mvpEngDadosPosPuc/blob/529cc4ab58fa85f2476028b240bed918eb465830/docs/images/arquiterura-ingestao.png?raw=true)
# MAGIC

# COMMAND ----------

# DBTITLE 1,Import Libraries
from pyspark.sql.functions import col, explode
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, DoubleType, IntegerType, ArrayType

# COMMAND ----------

# DBTITLE 1,Catolog
spark.sql("create catalog if not exists lakehouse managed location 's3://databricks-9cwyoqzauqyermnrdpparb-cloud-storage-bucket/unity-catalog/1732645886098685'")
spark.sql("use catalog lakehouse")

# COMMAND ----------

# DBTITLE 1,Schema & Volume
spark.sql("create schema if not exists bronze")
spark.sql("create volume if not exists bronze.checkpoint_historico_cripto")

# COMMAND ----------

# DBTITLE 1,Parâmetros
landing_path = "s3://01.landing/historico/"
check_point_path = "/Volumes/lakehouse/bronze/checkpoint_historico_cripto" 
table_name = "bronze.historico_cripto"

# COMMAND ----------

# Define schema explícito (melhor para performance e evitar problemas de inferência)
schema = StructType([
    StructField("metadata", StructType([
        StructField("extraction_date", StringType()),
        StructField("source", StringType()),
        StructField("asset_name", StringType()),
        StructField("ticker", StringType()),
        StructField("total_records", StringType()),
    ])),
    StructField("data", ArrayType(StructType([
        StructField("timestamp", StringType()),
        StructField("price_usd", DoubleType())
    ])))
])

# COMMAND ----------

# Leitura com Auto Loader
df_raw = (
    spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "json")
    .option("multiline", "true")
    .schema(schema)  
    .load(landing_path)
)

# COMMAND ----------

# Explodir o array de data
from pyspark.sql.functions import explode, col, input_file_name

df_transformed = (
    df_raw
    .withColumn("record", explode(col("data")))
    .select(
        col("metadata.asset_name").alias("asset_name"),
        col("metadata.ticker").alias("ticker"),
        col("metadata.extraction_date").alias("extraction_date"),
        col("metadata.source").alias("source"),
        col("record.timestamp").alias("timestamp"),
        col("record.price_usd").alias("price_usd"),
        input_file_name().alias("source_file")
    )
)

# COMMAND ----------

# Escrita no Delta Lake camada bronze
(
    df_transformed.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", check_point_path)
    .trigger(availableNow=True)
    .table(table_name)
)
