from pyspark.sql import functions as F
from pyspark.sql.window import Window


def add_event_id(df):
    # Same event_name can cover several different races (Sri Chinmoy organizes
    # 6-day, 10-day, 1000mi, 1300mi etc under one umbrella name). To get a unique
    # event_id per actual race we rank on name + distance + unit together.
    w = Window.orderBy("Event name", "event_value", "event_unit")
    df = df.withColumn("event_id", F.dense_rank().over(w))
    return df


def add_athlete_id(df):
    # Same idea for athletes - one id per athlete based on their name and birth year
    w = Window.orderBy("Athlete ID")
    df = df.withColumn("athlete_id", F.dense_rank().over(w))
    return df