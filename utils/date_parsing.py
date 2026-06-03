# Some parts and solutions of this code was found through help from Claude

from pyspark.sql import functions as F


def parse_event_dates(df):
    # The Event dates column has three formats:
    # "28.04.2018"               - single day
    # "05.-06.09.2015"           - multi-day, same month
    # "28.02.-03.03.2019"        - multi-day, different months (and sometimes years)
    # Some rows have invalid dates like "00.03.1998" - we let those become NULL
    # rather than crashing the pipeline.

    dates = F.col("Event dates")

    parts = F.split(dates, "-")
    left = parts.getItem(0)

    has_dash = F.size(parts) > 1
    right = F.when(has_dash, parts.getItem(1))

    left_clean = F.regexp_replace(left, r"\.+$", "")

    left_is_full = left_clean.rlike(r"^\d{2}\.\d{2}\.\d{4}$")
    left_has_month = left_clean.rlike(r"^\d{2}\.\d{2}$")

    start_str = (
        F.when(left_is_full, left_clean)
         .when(left_has_month, F.concat(left_clean, F.lit("."), F.regexp_extract(right, r"(\d{4})$", 1)))
         .otherwise(F.concat(left_clean, F.lit("."), F.regexp_extract(right, r"(\d{2}\.\d{4})$", 1)))
    )

    end_str = F.when(has_dash, right).otherwise(start_str)

    # try_to_date returns NULL for invalid dates instead of crashing.
    # This handles bad data like "00.03.1998" (day 0 doesn't exist).
    df = df.withColumn("start_date", F.try_to_date(start_str, F.lit("dd.MM.yyyy")))
    df = df.withColumn("end_date", F.try_to_date(end_str, F.lit("dd.MM.yyyy")))

    # Fix data quality issue: some rows have end_date earlier than start_date.
    df = df.withColumn(
        "end_date",
        F.when(F.col("end_date") < F.col("start_date"), F.col("start_date"))
         .otherwise(F.col("end_date"))
    )

    return df


def build_dim_date(spark, start_date, end_date):
    # Generate one row per calendar day between start_date and end_date,
    # then enrich each row with year, month, weekday etc.

    # F.sequence builds an array of all dates in the range. We explode it into rows.
    df = spark.sql(f"""
        SELECT explode(sequence(to_date('{start_date}'), to_date('{end_date}'), interval 1 day)) AS full_date
    """)

    df = (
        df
        # date_id as YYYYMMDD integer - meaningful and easy to read
        .withColumn("date_id", F.date_format("full_date", "yyyyMMdd").cast("int"))
        .withColumn("year", F.year("full_date"))
        .withColumn("month", F.month("full_date"))
        .withColumn("day", F.dayofmonth("full_date"))
        .withColumn("month_name", F.date_format("full_date", "MMMM"))
        .withColumn("day_of_week", F.dayofweek("full_date"))
        .withColumn("day_name", F.date_format("full_date", "EEEE"))
        .withColumn("quarter", F.quarter("full_date"))
        .withColumn("is_weekend", F.dayofweek("full_date").isin(1, 7))
    )

    # Put date_id and full_date first for readability
    df = df.select(
        "date_id", "full_date", "year", "month", "day",
        "month_name", "day_of_week", "day_name", "quarter", "is_weekend"
    )

    return df