# -*- coding: utf-8 -*-
"""tb_silver_business_rules.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1MR14HNJYKYptA33xryfRXU7YMBDM9Ouh

### Imports
"""

from datetime import datetime
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import current_timestamp, date_format, col
from pyspark.sql.types import StructType, StructField, StringType, TimestampType
from typing import List
from google.colab import drive

drive.mount('/content/drive')

# Configuração do logger
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

"""### Constantes"""

# Configurações
APP_NAME = "tb_business_rules" # Alterar

FILE_PATH = f"/content/drive/My Drive/projetos/Projeto Integrador/dataset/bronze/{APP_NAME}/"
OUTPUT_PATH = f"/content/drive/My Drive/projetos/Projeto Integrador/dataset/silver/{APP_NAME}/"
TABLE_NAME = "tb_silver_business_rules" # Alterar

COLUMNS: List[str] = [
    "IssuerId",
    "BusinessYear",
    "MarketCoverage",
    "ProductId",
    "StateCode"
    ] # Alterar

"""### Processamento Principal"""

def log_info(message: str):
    """Função para simular o comportamento do logger.info"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{current_time} - INFO - {message}")

def create_spark_session():
    """Cria e retorna uma sessão Spark."""
    log_info("Criando sessão Spark")
    return SparkSession.builder.appName("LoggerDemo").getOrCreate()

def define_silver_schema() -> StructType:
    """Define e retorna o schema para a tabela silver."""
    log_info("Definindo schema para a tabela silver")
    return StructType([
        StructField(col, StringType(), True) for col in COLUMNS
    ] + [
        StructField("ingestDate", TimestampType(), False),
        StructField("partitionDate", StringType(), False)
    ])

def read_and_process_data(spark: SparkSession, file_path: str, columns: List[str]) -> DataFrame:
    """Lê os dados do Parquet e processa para o formato desejado."""
    log_info(f"Lendo e processando dados de {file_path}")
    df = spark.read.parquet(file_path)
    return df.select(*columns).distinct() \
             .withColumn("ingestDate", current_timestamp()) \
             .withColumn("partitionDate", date_format(current_timestamp(), "yyyyMMdd"))

def prepare_silver_data(df: DataFrame, schema: StructType) -> DataFrame:
    """Prepara os dados para o formato silver."""
    log_info("Preparando dados para o formato silver")
    return df.select([
        col(c).cast("string") for c in COLUMNS
    ] + [
        col("ingestDate"),
        col("partitionDate")
    ]).select(schema.fieldNames())

def save_as_parquet(df: DataFrame, output_path: str):
    """Salva o DataFrame como arquivo Parquet no Google Drive."""
    log_info(f"Salvando dados como Parquet em {output_path}")
    df.write \
      .mode("overwrite") \
      .partitionBy("partitionDate") \
      .parquet(output_path)

def main():
    try:
        spark = create_spark_session()
        silver_schema = define_silver_schema()

        df_selected = read_and_process_data(spark, FILE_PATH, COLUMNS)
        df_silver = prepare_silver_data(df_selected, silver_schema)

        save_as_parquet(df_silver, OUTPUT_PATH)

        log_info(f"Dados salvos como Parquet em: {OUTPUT_PATH}")

        # Verificar se o arquivo foi salvo corretamente
        saved_df = spark.read.parquet(OUTPUT_PATH)
        log_info("Schema dos dados salvos:")
        saved_df.printSchema()
        log_info("Primeiras 5 linhas dos dados salvos:")
        saved_df.show(5)
        log_info(f"Contagem de registros salvos: {saved_df.count()}")
        log_info("Processo concluído com sucesso")

    except Exception as e:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{current_time} - ERROR - Erro durante a execução: {str(e)}")

if __name__ == "__main__":
    main()