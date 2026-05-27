# Some parts and solutions of this code was found through help from Claude (Anthropic).

# Catalog and schema names - kept here so we only change them in one place
CATALOG = "marathos"
SCHEMA_BRONZE = "bronze"
SCHEMA_SILVER = "silver"
SCHEMA_GOLD = "gold"
SCHEMA_DEFAULT = "default"

# Volume path for raw files
VOLUME_RAW_PATH = f"/Volumes/{CATALOG}/{SCHEMA_DEFAULT}/raw"

# Source CSV - update filename if needed
RAW_CSV_FILENAME = "TWO_CENTURIES_OF_UM_RACES.csv"
RAW_CSV_PATH = f"{VOLUME_RAW_PATH}/{RAW_CSV_FILENAME}"

# Table names
BRONZE_RESULTS_TABLE = f"{CATALOG}.{SCHEMA_BRONZE}.raw_results"
SILVER_RESULTS_OBT = f"{CATALOG}.{SCHEMA_SILVER}.results_obt"

GOLD_FCT_RESULTS = f"{CATALOG}.{SCHEMA_GOLD}.fct_results"
GOLD_DIM_EVENT = f"{CATALOG}.{SCHEMA_GOLD}.dim_event"
GOLD_DIM_ATHLETE = f"{CATALOG}.{SCHEMA_GOLD}.dim_athlete"
GOLD_DIM_DATE = f"{CATALOG}.{SCHEMA_GOLD}.dim_date"
GOLD_DIM_COUNTRY = f"{CATALOG}.{SCHEMA_GOLD}.dim_country"