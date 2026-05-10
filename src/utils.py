import sqlite3

def run_sql(database, query_file):
    with sqlite3.connect(database) as conn:
        conn.execute('pragma foreign_keys = on;')
        cursor = conn.cursor()

        with open(query_file, 'r') as qf:
            query = qf.read()
    
        return cursor.execute(query).fetchall()
