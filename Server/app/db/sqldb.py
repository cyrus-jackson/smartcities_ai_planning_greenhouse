import psycopg2
from datetime import datetime
import json
import os
import bcrypt

conn_str = os.environ.get("POSTGRESQL_CONNECTION_STRING").strip()


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


def verify_password(stored_hash, provided_password):
    try:
        stored_hash_bytes = stored_hash.encode('utf-8')
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hash_bytes)
    except Exception as e:
        print(f"Password verification error: {str(e)}")
        return False

def check_control_panel_password(password):
    if not password or not isinstance(password, str) or len(password) == 0:
        return False

    conn = None
    cur = None
    try:
        conn = psycopg2.connect(conn_str)
        cur = conn.cursor()
        select_query = "SELECT value FROM keys WHERE name = 'control_panel_password'"
        cur.execute(select_query)
        stored_hash = cur.fetchone()[0]
        row = cur.fetchone()
        if verify_password(stored_hash, password):
            return True
        else:
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def get_all_configs():
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(conn_str)
        cur = conn.cursor()
        select_query = "SELECT name, value FROM configs"
        cur.execute(select_query)
        return dict(cur.fetchall())
    except Exception as e:
        print(f"Error fetching configs: {e}")
        return {}
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def update_config_in_db(name, value):
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(conn_str)
        cur = conn.cursor()
        update_query = """
        INSERT INTO configs (name, value) 
        VALUES (%s, %s)
        ON CONFLICT (name) 
        DO UPDATE SET value = EXCLUDED.value, updated_at = CURRENT_TIMESTAMP
        """
        cur.execute(update_query, (name, value))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating config: {e}")
        return False
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