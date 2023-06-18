import sqlite3

def get_db_connection():
    '''
    Get connection to DB
    '''
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn