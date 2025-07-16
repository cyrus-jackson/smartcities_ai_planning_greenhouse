import bcrypt
import psycopg2
import os

def set_control_panel_password(password):
    """
    Set the control panel password with proper encryption
    """
    try:
        # Generate salt and hash the password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        # Store the hash as string in database
        conn = psycopg2.connect(os.environ.get("POSTGRESQL_CONNECTION_STRING").strip())
        cur = conn.cursor()
        
        # Update or insert the hashed password
        cur.execute("""
            INSERT INTO keys (name, value) 
            VALUES ('control_panel_password', %s)
            ON CONFLICT (name) DO UPDATE SET value = EXCLUDED.value
        """, (hashed.decode('utf-8'),))
        
        conn.commit()
        print("Password updated successfully")
        
    except Exception as e:
        print(f"Error setting password: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    import getpass
    password = getpass.getpass("Enter new control panel password: ")
    set_control_panel_password(password)