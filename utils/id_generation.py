from pyspark.sql import functions as F
from pyspark.sql.window import Window


def add_event_id(df):
    # Gives each unique event name the same id, using dense_rank like the lab suggested
    w = Window.orderBy("Event name")
    df = df.withColumn("event_id", F.dense_rank().over(w))
    return df


def add_athlete_id(df):
    # Same idea for athletes - one id per athlete based on their name and birth year
    w = Window.orderBy("Athlete ID")
    df = df.withColumn("athlete_id", F.dense_rank().over(w))
    return df