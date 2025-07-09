import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import os

# Connect to PostgreSQL
def get_connection():
    return psycopg2.connect(
        dbname="weather_chatbot",
        user="postgres",
        password="Abhi@123",  # ← Replace this
        host="localhost",
        port="5432"
    )

# Insert a chat message (user + bot response)
def insert_chat_history(user_msg, bot_reply):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chat_history (user_message, bot_reply, timestamp)
            VALUES (%s, %s, %s)
        """, (user_msg, bot_reply, datetime.now()))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[DB ERROR] Failed to insert chat: {e}")
