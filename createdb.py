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
    create_database("smartcities")
    create_tables()
