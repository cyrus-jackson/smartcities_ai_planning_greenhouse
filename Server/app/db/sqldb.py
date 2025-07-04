import psycopg2
from datetime import datetime
import json
import os

conn_str = os.environ.get("POSTGRESQL_CONNECTION_STRING")


def insert_pddl_problem(problem_name, content, solution, domain='greenhouse'):
    # Connect to PostgreSQL
    try:
        # Convert solution to JSON string if it's a dict
        if isinstance(solution, dict):
            solution = json.dumps(solution)

        conn = psycopg2.connect(conn_str)
        cur = conn.cursor()

        # Insert into table and return id
        insert_query = """
        INSERT INTO pddl_problems (name, domain, content, solution, created_at)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """
        
        cur.execute(insert_query, (
            problem_name,
            domain,
            content,
            solution,
            datetime.utcnow()
        ))

        inserted_id = cur.fetchone()[0]
        conn.commit()
        print(f"Problem '{problem_name}' inserted successfully with id {inserted_id}.")
        return inserted_id
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def get_pddl_problem(problem_id):
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(conn_str)
        cur = conn.cursor()
        select_query = """
        SELECT domain, content, solution, name, created_at
        FROM pddl_problems
        WHERE id = %s
        """
        cur.execute(select_query, (problem_id,))
        row = cur.fetchone()
        if row:
            domain, problem, solution, name, created_at = row
            # If solution is a JSON string, try to parse it
            try:
                solution = json.loads(solution)
            except Exception:
                pass
            return {
                "domain": domain,
                "problem": problem,
                "solution": solution,
                "name": name,
                "created_at": created_at
            }
        else:
            print(f"No problem found with id {problem_id}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def get_last_n_pddl_problems(n=5):
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(conn_str)
        cur = conn.cursor()
        select_query = """
        SELECT id, domain, content, solution, name, created_at
        FROM pddl_problems
        ORDER BY created_at DESC
        LIMIT %s
        """
        cur.execute(select_query, (n,))
        rows = cur.fetchall()
        results = []
        for row in rows:
            id_, domain, problem, solution, name, created_at = row
            try:
                solution = json.loads(solution)
            except Exception:
                pass
            results.append({
                "id": id_,
                "domain": domain,
                "problem": problem,
                "solution": solution,
                "name": name,
                "created_at": created_at
            })
        return results
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def insert_weather_forecast(data):
    try:
        conn = psycopg2.connect(conn_str)
        cur = conn.cursor()
        insert_query = """
            INSERT INTO weather_forecast (fetched_at, data)
            VALUES (%s, %s)
        """
        cur.execute(insert_query, (datetime.now(), json.dumps(data)))
        conn.commit()
    except Exception as e:
        print(f"Error inserting weather forecast: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def get_recent_weather_forecast():
    try:
        conn = psycopg2.connect(conn_str)
        cur = conn.cursor()
        select_query = """
            SELECT data FROM weather_forecast ORDER BY ID DESC LIMIT 1
        """
        cur.execute(select_query)
        row = cur.fetchone()
        if row:
            try:
                return row[0]
            except Exception:
                print(f"Error parsing weather forecast: {e}")
                return {}
    except Exception as e:
        print(f"Error selecting weather forecast: {e}")
        return {}
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()