import sqlite3
import streamlit as st

DB_PATH = 'dataurbe.bd'  # caminho do banco local

def get_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # permite acessar resultados como dicionário
        return conn
    except sqlite3.Error as e:
        st.error(f'Erro ao conectar ao banco SQLite: {e}')
        return None

def fetch_data(query, params=None):
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        result = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return result
    return []
