# Some parts and solutions of this code was found through help from Claude (Anthropic).

from pyspark.sql import DataFrame, SparkSession


def read_csv_from_volume(spark: SparkSession, path: str, header=True, infer_schema=True) -> DataFrame:
    # Reads a CSV from a Unity Catalog volume into a Spark DataFrame
    return (
        spark.read
        .option("header", str(header).lower())
        .option("inferSchema", str(infer_schema).lower())
        .csv(path)
    )


def write_df_to_table(df: DataFrame, table_name: str, mode="overwrite") -> None:
    # overwriteSchema lets us change columns when re-running during development
    # column mapping lets us use names with spaces/slashes (needed for bronze)
    (
        df.write
        .mode(mode)
        .option("overwriteSchema", "true")
        .option("delta.columnMapping.mode", "name")
        .option("delta.minReaderVersion", "2")
        .option("delta.minWriterVersion", "5")
        .saveAsTable(table_name)
    )


def read_table(spark: SparkSession, table_name: str) -> DataFrame:
    return spark.table(table_name)