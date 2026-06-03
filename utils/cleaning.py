# Some parts and solutions of this code was found through help from Claude

from pyspark.sql import functions as F


def time_to_seconds(time_col):
    # Turns "6:43:49" into total seconds, and handles days like "2d 02:17:00"
    days = F.regexp_extract(time_col, r"(\d+)d", 1)
    days = F.when(days == "", 0).otherwise(days.cast("int"))

    hms = F.regexp_extract(time_col, r"(\d+:\d+:\d+)", 1)
    hours = F.split(hms, ":").getItem(0).cast("int")
    minutes = F.split(hms, ":").getItem(1).cast("int")
    seconds = F.split(hms, ":").getItem(2).cast("int")

    return days * 86400 + hours * 3600 + minutes * 60 + seconds


def split_event_distance(df):
    # Splits "50km" into a number (50) and a unit ("km")
    df = df.withColumn("event_value", F.regexp_extract("Event distance/length", r"([\d.]+)", 1).cast("double"))
    df = df.withColumn("event_unit", F.regexp_extract("Event distance/length", r"([a-zA-Z]+)", 1))
    return df


def split_performance(df):
    # Performance is either a distance like "50.000 km" or a time like "6:43:49 h"
    df = df.withColumn("perf_unit", F.regexp_extract("Athlete performance", r"([a-zA-Z]+)\s*$", 1))

    # km or mi means it's a distance
    df = df.withColumn(
        "perf_distance",
        F.when(
            F.col("perf_unit").isin("km", "mi"),
            F.regexp_extract("Athlete performance", r"([\d.]+)", 1).cast("double")
        )
    )

    # h means it's a time - convert to seconds
    df = df.withColumn(
        "perf_seconds",
        F.when(F.col("perf_unit") == "h", time_to_seconds(F.col("Athlete performance")))
    )
    return df


def add_event_type(df):
    # Classify events into three types based on the unit:
    # distance (km/mi - race a fixed distance), time (h - race for a fixed time),
    # multi_day (d - multi-day races, kept based on instructor feedback)
    df = df.withColumn(
        "event_type",
        F.when(F.col("event_unit").isin("km", "mi"), "distance")
         .when(F.col("event_unit") == "h", "time")
         .when(F.col("event_unit") == "d", "multi_day")
         .otherwise("unknown")
    )
    return df


def add_validity_flag(df):
    # A row is valid if the event/performance unit combination makes sense:
    # distance event (km/mi) -> performance should be a time (h)
    # time event (h) -> performance should be a distance (km or mi)
    # multi_day event (d) -> performance should be a distance (km or mi)
    is_valid = (
        ((F.col("event_unit").isin("km", "mi")) & (F.col("perf_unit") == "h"))
        | ((F.col("event_unit") == "h") & (F.col("perf_unit").isin("km", "mi")))
        | ((F.col("event_unit") == "d") & (F.col("perf_unit").isin("km", "mi")))
    )
    df = df.withColumn("is_valid", is_valid)
    return df


def clean_rows(df):
    # Keep only valid rows
    df = df.filter(F.col("is_valid") == True)

    # Filter on age at event - works across the full 1798-2022 range
    df = df.withColumn("age_at_event", F.col("Year of event") - F.col("Athlete year of birth"))
    df = df.filter((F.col("age_at_event") >= 5) & (F.col("age_at_event") <= 100))

    # Country codes were mixed case (ACT, swe) - normalize to uppercase
    df = df.withColumn("athlete_country", F.upper(F.col("Athlete country")))

    # Birth year was a double, make it an int
    df = df.withColumn("athlete_year_of_birth", F.col("Athlete year of birth").cast("int"))

    # Age at event was a double - make it an int (it's just whole years)
    df = df.withColumn("age_at_event", F.col("age_at_event").cast("int"))

    return df


def normalize_country_codes(df):
    # Some countries appear with two codes in the source data.
    # Map the historical ones to the IOC codes used in dim_country.
    df = df.withColumn(
        "athlete_country",
        F.when(F.col("athlete_country") == "DAN", "DEN")
         .when(F.col("athlete_country") == "IRE", "IRL")
         .when(F.col("athlete_country") == "SVE", "SWE")
         .when(F.col("athlete_country") == "MDG", "MAD")
         .otherwise(F.col("athlete_country"))
    )
    return df


def select_final_columns(df):
    # Pick the columns we want in silver and give them clean snake_case names
    df = df.select(
        F.col("event_id"),
        F.col("Event name").alias("event_name"),
        F.col("Year of event").alias("year_of_event"),
        F.col("start_date"),
        F.col("end_date"),
        F.col("event_value").alias("event_distance_value"),
        F.col("event_unit").alias("event_distance_unit"),
        F.col("event_type"),
        F.col("Event number of finishers").alias("event_num_finishers"),
        F.col("athlete_id"),
        F.col("athlete_country"),
        F.col("athlete_year_of_birth"),
        F.col("age_at_event"),
        F.col("Athlete gender").alias("athlete_gender"),
        F.col("Athlete age category").alias("athlete_age_category"),
        F.col("Athlete club").alias("athlete_club"),
        F.col("perf_unit").alias("performance_unit"),
        F.col("perf_distance").alias("performance_distance"),
        F.col("perf_seconds").alias("performance_seconds"),
    )
    return df