
import psycopg2
import pandas as pd
import uuid
from datetime import datetime

# IMPORTANT: Replace these with your actual PostgreSQL database credentials.
DB_HOST = "your_host"
DB_NAME = "your_database"
DB_USER = "your_user"
DB_PASS = "your_password"

def get_db_connection():
    """Establishes and returns a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error connecting to database: {e}")
        return None

# --- CRUD Operations for Goals ---

def get_all_employees():
    """Fetches all employees from the database."""
    conn = get_db_connection()
    if conn is None: return pd.DataFrame()
    
    try:
        df = pd.read_sql("SELECT employee_id, name FROM employees;", conn)
        return df
    except Exception as e:
        print(f"Error fetching employees: {e}")
        return pd.DataFrame()
    finally:
        if conn: conn.close()

def add_goal(employee_id, title, description, due_date, status):
    """Adds a new goal to the database."""
    conn = get_db_connection()
    if conn is None: return False

    try:
        cur = conn.cursor()
        goal_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO goals (goal_id, employee_id, title, description, due_date, status)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (goal_id, employee_id, title, description, due_date, status))
        conn.commit()
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error adding goal: {error}")
        conn.rollback()
        return False
    finally:
        if conn: conn.close()

def get_goals(employee_id=None, status=None, sort_by='due_date'):
    """Fetches goals with optional filtering and sorting."""
    conn = get_db_connection()
    if conn is None: return pd.DataFrame()

    query = f"SELECT * FROM goals WHERE 1=1"
    params = []
    
    if employee_id:
        query += " AND employee_id = %s"
        params.append(employee_id)
    if status and status != "All":
        query += " AND status = %s"
        params.append(status)
    
    query += f" ORDER BY {sort_by} ASC;"
    
    try:
        df = pd.read_sql(query, conn, params=params)
        return df
    except Exception as e:
        print(f"Error fetching goals: {e}")
        return pd.DataFrame()
    finally:
        if conn: conn.close()

def update_goal(goal_id, title, description, due_date, status):
    """Updates an existing goal."""
    conn = get_db_connection()
    if conn is None: return False

    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE goals
            SET title = %s, description = %s, due_date = %s, status = %s
            WHERE goal_id = %s;
        """, (title, description, due_date, status, goal_id))
        conn.commit()
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error updating goal: {error}")
        conn.rollback()
        return False
    finally:
        if conn: conn.close()

def delete_goal(goal_id):
    """Deletes a goal."""
    conn = get_db_connection()
    if conn is None: return False

    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM goals WHERE goal_id = %s;", (goal_id,))
        conn.commit()
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error deleting goal: {error}")
        conn.rollback()
        return False
    finally:
        if conn: conn.close()

# --- CRUD Operations for Feedback ---

def add_feedback(from_employee_id, to_employee_id, feedback_text):
    """Adds new feedback to the database."""
    conn = get_db_connection()
    if conn is None: return False

    try:
        cur = conn.cursor()
        feedback_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO feedback (feedback_id, from_employee_id, to_employee_id, feedback_text, created_at)
            VALUES (%s, %s, %s, %s, %s);
        """, (feedback_id, from_employee_id, to_employee_id, feedback_text, datetime.now()))
        conn.commit()
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error adding feedback: {error}")
        conn.rollback()
        return False
    finally:
        if conn: conn.close()

def get_feedback(employee_id):
    """Fetches all feedback for a specific employee."""
    conn = get_db_connection()
    if conn is None: return pd.DataFrame()

    try:
        query = "SELECT f.*, e.name AS from_employee_name FROM feedback f JOIN employees e ON f.from_employee_id = e.employee_id WHERE f.to_employee_id = %s ORDER BY f.created_at DESC;"
        df = pd.read_sql(query, conn, params=(employee_id,))
        return df
    except Exception as e:
        print(f"Error fetching feedback: {e}")
        return pd.DataFrame()
    finally:
        if conn: conn.close()

# --- Business Insights ---

def get_performance_insights():
    """Calculates key performance metrics using SQL aggregations."""
    conn = get_db_connection()
    if conn is None: return {}
    
    try:
        cur = conn.cursor()
        insights = {}
        
        # Total number of goals
        cur.execute("SELECT COUNT(*) FROM goals;")
        insights['total_goals'] = cur.fetchone()[0]

        # Total number of employees
        cur.execute("SELECT COUNT(*) FROM employees;")
        insights['total_employees'] = cur.fetchone()[0]
        
        # Goals by status
        cur.execute("SELECT status, COUNT(*) FROM goals GROUP BY status;")
        insights['goals_by_status'] = dict(cur.fetchall())
        
        # Average goals per employee
        if insights['total_employees'] > 0:
            insights['avg_goals_per_employee'] = insights['total_goals'] / insights['total_employees']
        else:
            insights['avg_goals_per_employee'] = 0

        # Average feedback received per employee
        cur.execute("SELECT COUNT(*) FROM feedback;")
        total_feedback = cur.fetchone()[0]
        if insights['total_employees'] > 0:
            insights['avg_feedback_per_employee'] = total_feedback / insights['total_employees']
        else:
            insights['avg_feedback_per_employee'] = 0

        # Max number of goals for any employee
        cur.execute("SELECT MAX(goal_count) FROM (SELECT employee_id, COUNT(*) AS goal_count FROM goals GROUP BY employee_id) AS T;")
        insights['max_goals_per_employee'] = cur.fetchone()[0] or 0

        # Min number of goals for any employee
        cur.execute("SELECT MIN(goal_count) FROM (SELECT employee_id, COUNT(*) AS goal_count FROM goals GROUP BY employee_id) AS T;")
        insights['min_goals_per_employee'] = cur.fetchone()[0] or 0
        
        return insights
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error fetching insights: {error}")
        return {}
    finally:
        if conn: cur.close(); conn.close()
