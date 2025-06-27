import psycopg2
from datetime import datetime
import json


conn_str = "postgresql://postgres:smartcities@localhost:5432/smartcities"


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