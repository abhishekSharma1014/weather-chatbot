import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import os

# ✅ Get connection from DATABASE_URL (Render-compatible)
def get_connection():
    try:
        db_url = os.environ.get("DATABASE_URL")
        if not db_url:
            raise ValueError("DATABASE_URL not set in environment variables")

        # ✅ psycopg2 expects "postgresql://" instead of "postgres://"
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)

        return psycopg2.connect(db_url, cursor_factory=RealDictCursor)
    except Exception as e:
        print(f"[DB ERROR] Could not connect to PostgreSQL: {e}")
        raise

# ✅ Insert chat history and auto-create table if needed
def insert_chat_history(user_msg, bot_reply):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # ✅ Create table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id SERIAL PRIMARY KEY,
                user_message TEXT NOT NULL,
                bot_reply TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ✅ Insert chat message
        cursor.execute("""
            INSERT INTO chat_history (user_message, bot_reply, timestamp)
            VALUES (%s, %s, %s)
        """, (user_msg, bot_reply, datetime.now()))

        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"[DB ERROR] Failed to insert chat: {e}")
