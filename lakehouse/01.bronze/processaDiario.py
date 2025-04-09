# Databricks notebook source
# MAGIC %md
# MAGIC
# MAGIC ## Objetivo: Esse notebook faz o processamento dos dados diários que se encontram na camada landing
# MAGIC
# MAGIC ![Arquiteture de Ingestão Landing - Bronze](https://github.com/douglas-engenheirodedados/mvpEngDadosPosPuc/blob/529cc4ab58fa85f2476028b240bed918eb465830/docs/images/arquiterura-ingestao.png?raw=true)
# MAGIC
# MAGIC

# COMMAND ----------

# DBTITLE 1,Import Libraries
from pyspark.sql.functions import col, explode, from_json, schema_of_json, input_file_name

# COMMAND ----------

# DBTITLE 1,Catolog
spark.sql("create catalog if not exists lakehouse managed location 's3://databricks-9cwyoqzauqyermnrdpparb-cloud-storage-bucket/unity-catalog/1732645886098685'")
spark.sql("use catalog lakehouse")

# COMMAND ----------

# DBTITLE 1,Schema & Volume
spark.sql("create schema if not exists bronze")
spark.sql("create volume if not exists bronze.checkpoint_diario_cripto")
spark.sql("create volume if not exists bronze.schema_diario_cripto")

# COMMAND ----------

# DBTITLE 1,Parâmetros
path_landing_diario = "s3://01.landing/cripto/"
check_point_path = "/Volumes/lakehouse/bronze/checkpoint_diario_cripto" 
schema_path = "/Volumes/lakehouse/bronze/schema_diario_cripto"
table_name = "bronze.diario_cripto"

# COMMAND ----------

# Leitura com inferência de schema e multiline
df_raw_diario = (
    spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "json")
    .option("cloudFiles.inferColumnTypes", "true")
    .option("cloudFiles.schemaLocation", schema_path)
    .option("multiline", "true")  # Essencial para arquivos JSON com estrutura aninhada
    .load(path_landing_diario)
)

# COMMAND ----------

# Explode os dados mantendo os metadados
df_transformed = (
    df_raw_diario
    .withColumn("record", explode("data"))
    .select(
        col("record.timestamp").alias("timestamp"),
        col("record.price_usd").alias("price_usd"),
        col("metadata.asset_name").alias("asset_name"),
        col("metadata.extraction_date").alias("extraction_date"),
        col("metadata.source").alias("source"),
        col("metadata.time_interval").alias("time_interval"),
        input_file_name().alias("source_file")
    )
)

# COMMAND ----------

# Escrita no Delta Lake (bronze diário)
(
    df_transformed.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation",check_point_path)
    .trigger(availableNow=True)
    .table(table_name)
)

