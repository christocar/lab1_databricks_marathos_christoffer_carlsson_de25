# Some parts and solutions of this code was found through help from Claude.

# Catalog and schema names - kept here so we only change them in one place
CATALOG = "marathos"
SCHEMA_BRONZE = "bronze"
SCHEMA_SILVER = "silver"
SCHEMA_GOLD = "gold"
SCHEMA_DEFAULT = "default"

# Volume paths
VOLUME_RAW_PATH = f"/Volumes/{CATALOG}/{SCHEMA_DEFAULT}/raw"

# Source CSVs
RAW_CSV_FILENAME = "TWO_CENTURIES_OF_UM_RACES.csv"
RAW_CSV_PATH = f"{VOLUME_RAW_PATH}/{RAW_CSV_FILENAME}"

COUNTRY_MAPPING_FILENAME = "country_mapping.csv"
COUNTRY_MAPPING_PATH = f"{VOLUME_RAW_PATH}/{COUNTRY_MAPPING_FILENAME}"

# Streaming source and checkpoint paths (Bonus 2)
STREAMING_SOURCE_PATH = f"{VOLUME_RAW_PATH}/streaming"
STREAMING_CHECKPOINT_PATH = f"{VOLUME_RAW_PATH}/_checkpoints/streaming_results"

# Bronze table names
BRONZE_RESULTS_TABLE = f"{CATALOG}.{SCHEMA_BRONZE}.raw_results"
BRONZE_STREAMING_RESULTS = f"{CATALOG}.{SCHEMA_BRONZE}.streaming_results"

# Silver table names
SILVER_RESULTS_OBT = f"{CATALOG}.{SCHEMA_SILVER}.results_obt"
SILVER_DIM_COUNTRY = f"{CATALOG}.{SCHEMA_SILVER}.dim_country"

# Gold table names
GOLD_FCT_RESULTS = f"{CATALOG}.{SCHEMA_GOLD}.fct_results"
GOLD_DIM_EVENT = f"{CATALOG}.{SCHEMA_GOLD}.dim_event"
GOLD_DIM_ATHLETE = f"{CATALOG}.{SCHEMA_GOLD}.dim_athlete"
GOLD_DIM_DATE = f"{CATALOG}.{SCHEMA_GOLD}.dim_date"
GOLD_DIM_COUNTRY = f"{CATALOG}.{SCHEMA_GOLD}.dim_country"