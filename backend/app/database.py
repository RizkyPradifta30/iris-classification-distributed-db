
import os
import psycopg


def get_primary_connection():
    return psycopg.connect(
        host=os.getenv("PRIMARY_DB_HOST", "primary"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"]
    )


def get_replica_connection():
    return psycopg.connect(
        host=os.getenv("REPLICA_DB_HOST", "replica"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"]
    )
