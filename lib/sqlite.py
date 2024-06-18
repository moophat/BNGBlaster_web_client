import sqlite3

def sqlite_connect_to_db(db_name):
    conn = sqlite3.connect(db_name)
    return conn
def sqlite_get_all_tables(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    return [table[0] for table in tables]
def sqlite_delete_table(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    conn.commit()
    print(f"Table '{table_name}' deleted successfully (if it existed).")

def sqlite_create_table_user(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            name TEXT PRIMARY KEY NOT NULL,
            class TEXT NOT NULL
        )
    ''')
    conn.commit()
def sqlite_insert_user(conn, name, user_class):
    cursor = conn.cursor()
    # Check if a user with the same name already exists
    cursor.execute('''
        SELECT * FROM users WHERE name = ?
    ''', (name,))
    existing_user = cursor.fetchone()
    if existing_user:
        print(f"User with name '{name}' already exists. Skipping insertion.")
    else:
        cursor.execute('''
            INSERT INTO users (name, class) VALUES (?, ?)
        ''', (name, user_class))
        conn.commit()
        print(f"User '{name}' inserted successfully.")
def sqlite_insert_blaster(conn, ip, port, user, passwd):
    cursor = conn.cursor()
    # Check if a user with the same name already exists
    cursor.execute('''
        SELECT * FROM blasters WHERE ip = ?
    ''', (ip,))
    existing_blaster = cursor.fetchone()
    if existing_blaster:
        print(f"Blaster '{ip}' already exists. Skipping insertion.")
    else:
        cursor.execute('''
            INSERT INTO blasters (ip, port, user, passwd) VALUES (?,?,?,?)
        ''', (ip, port, user, passwd))
        conn.commit()
        print(f"Blaster '{ip}' inserted successfully.")
def sqlite_fetch_table(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    return rows
def sqlite_fetch_users(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    rows = cursor.fetchall()
    return rows
def sqlite_select_user_by_name(conn, name):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM users WHERE name = ?
    ''', (name,))
    row = cursor.fetchone()
    return row
def sqlite_select_user_columns_by_name(conn, name, columns):
    cursor = conn.cursor()
    query = f'SELECT {", ".join(columns)} FROM users WHERE name = ?'
    cursor.execute(query, (name,))
    row = cursor.fetchone()
    return row
def sqlite_select_blaster_columns_by_ip(conn, ip, columns):
    cursor = conn.cursor()
    query = f'SELECT {", ".join(columns)} FROM users WHERE ip = ?'
    cursor.execute(query, (ip,))
    row = cursor.fetchone()
    return row
def sqlite_delete_user(conn, name):
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM users
        WHERE name = ?
    ''', (name,))
    conn.commit()
def sqlite_delete_blaster(conn, ip):
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM blasters
        WHERE ip = ?
    ''', (ip,))
    conn.commit()
def sqlite_update_user_class(conn, name, new_class):
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users
        SET class = ?
        WHERE name = ?
    ''', (new_class, name))
    conn.commit()
