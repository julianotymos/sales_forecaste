import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st
from contextlib import contextmanager

@contextmanager
def get_connection():
    conn = psycopg2.connect(
        dbname=st.secrets["dbname"],
        user=st.secrets["user"],
        password=st.secrets["password"],
        host=st.secrets["host"],
        port=st.secrets["port"],
        cursor_factory=RealDictCursor
    )
    try:
        yield conn
    finally:
        conn.close()
