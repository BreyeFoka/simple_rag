import sqlite3
import json

DB_PATH = 'vector_db.sqlite'

# Create table if not exists
CREATE_TABLE_SQL = '''
CREATE TABLE IF NOT EXISTS vectors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk TEXT NOT NULL,
    embedding TEXT NOT NULL
)
'''

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(CREATE_TABLE_SQL)
    return conn

def add_chunk_to_db(chunk, embedding):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO vectors (chunk, embedding) VALUES (?, ?)', (chunk, json.dumps(embedding)))
    conn.commit()
    conn.close()

def get_all_chunks_and_embeddings():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT chunk, embedding FROM vectors')
    rows = cur.fetchall()
    conn.close()
    return [(row[0], json.loads(row[1])) for row in rows]

def clear_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM vectors')
    conn.commit()
    conn.close()
