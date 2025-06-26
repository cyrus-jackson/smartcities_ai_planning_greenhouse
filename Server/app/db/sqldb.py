import psycopg2
from datetime import datetime


conn_str = "postgresql://postgres:smartcities@localhost:5432/smartcities"


def insert_pddl_problem(problem_name, content, solution, domain='greenhouse'):
    # Connect to PostgreSQL
    try:
        conn = psycopg2.connect(conn_str)
        cur = conn.cursor()

        # Insert into table
        insert_query = """
        INSERT INTO pddl_problems (name, domain, content, solution, created_at) VALUES (%s, %s, %s, %s)
        """
        
        cur.execute(insert_query, (
            problem_name,
            domain,
            content,
            solution,
            datetime.utcnow()
        ))

        conn.commit()
        print(f"Problem '{problem_name}' inserted successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()