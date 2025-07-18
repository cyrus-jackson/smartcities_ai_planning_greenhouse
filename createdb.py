import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'Server', 'app'))
from db.sqldb import update_config

import psycopg2
from psycopg2 import sql, errors

# --- Config ---
POSTGRES_CONN = {
    "dbname": "postgres",
    "user": "postgres",
    "host": "localhost",
    "port": 5432
}

POSTGRESQL_CONNECTION_STRING="postgresql://postgres:smartcities@localhost:5432/smartcities"


def init_configs():
    
    # Default values from your JSON
    default_configs = {
        "temperature-threshold": 25,
        "humidity-threshold": 25,
        "soil_moisture_threshold": 35,
        "water_level_threshold": 20,
        "water_alert_high_threshold": 10,
        "water_alert_warning_threshold": 50,
        "rain_expected_threshold": 30,
        "cooling-rate fan1": 2,
        "required-duration fan1": 100,
        "servo-cooling-rate s1": 1,
        "servo-duration s1": 100,
        "total-cost": 0
    }
    
    # Insert/update each config
    for name, value in default_configs.items():
        update_config(name, value)


# --- Create Database ---
def create_database(db_name):
    try:
        with psycopg2.connect(**POSTGRES_CONN) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(db_name)
                ))
                print(f"Database '{db_name}' created successfully.")
    except errors.DuplicateDatabase:
        print(f"Database '{db_name}' already exists.")
    except Exception as e:
        print("Error creating database:", e)


# --- Create Tables ---
def create_tables():
    create_tables_sql = """
    CREATE TABLE IF NOT EXISTS pddl_problems (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        domain TEXT NOT NULL DEFAULT 'greenhouse',
        content TEXT NOT NULL,
        solution JSONB,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS weather_forecast (
        id SERIAL PRIMARY KEY,
        fetched_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        data JSONB NOT NULL
    );

    CREATE TABLE IF NOT EXISTS configs (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL UNIQUE,
        value FLOAT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    try:
        with psycopg2.connect(POSTGRESQL_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:
                cur.execute(create_tables_sql)
                conn.commit()
                print("Tables created successfully.")
    except Exception as e:
        print("Error creating tables:", e)


# --- Run ---
if __name__ == "__main__":
    # create_database("smartcities")
    # create_tables()
    init_configs()