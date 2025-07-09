import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import os
import urllib.parse as urlparse  # ✅ NEW

# ✅ Parse DATABASE_URL from Render environment variable
def get_connection():
    try:
        db_url = os.environ.get("DATABASE_URL")
        if not db_url:
            raise ValueError("DATABASE_URL not set in environment variables")

        result = urlparse.urlparse(db_url)

        return psycopg2.connect(
            dbname=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
    except Exception as e:
        print(f"[DB ERROR] Could not connect to PostgreSQL: {e}")
        raise

# ✅ Insert and create table if not exists
def insert_chat_history(user_msg, bot_reply):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # ✅ Create table if it doesn't exist (safe for first-time deployment)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id SERIAL PRIMARY KEY,
                user_message TEXT NOT NULL,
                bot_reply TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ✅ Insert data
        cursor.execute("""
            INSERT INTO chat_history (user_message, bot_reply, timestamp)
            VALUES (%s, %s, %s)
        """, (user_msg, bot_reply, datetime.now()))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[DB ERROR] Failed to insert chat: {e}")
