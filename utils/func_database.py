import psycopg2
import pytz
from datetime import datetime
from config.config import TIMEZONE
import asyncio

class DataBaseUserSaver:

    def __init__(self, db_params, message):
        self.db_params = db_params
        self.user_id = message.from_user.id
        self.date = datetime.now(pytz.timezone(TIMEZONE))

    def create_table(self):
        conn = psycopg2.connect(**self.db_params)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS USERS (
                user_id BIGINT PRIMARY KEY,
                agreement TIMESTAMP NOT NULL)
                """)
        conn.commit()
        conn.close()
    def user_exists(self):
        self.create_table()
        conn = psycopg2.connect(**self.db_params)
        cur = conn.cursor()
        cur.execute(f"SELECT COUNT(*) FROM users WHERE user_id={self.user_id}")
        data = cur.fetchone()[0]
        conn.close()
        return bool(data)

    def insert_user(self):
        conn = psycopg2.connect(**self.db_params)
        cur = conn.cursor()
        cur.execute("INSERT INTO USERS VALUES (%s, %s)", (self.user_id, self.date))
        conn.commit()
        conn.close()

    def get_user_agreement_date(self):
        conn = psycopg2.connect(**self.db_params)
        c = conn.cursor()
        c.execute(f"SELECT agreement FROM users WHERE user_id={self.user_id}")
        data = c.fetchone()
        conn.close()
        return data

class DataBaseTextSaver:
    def __init__(self, db_params, message, text, label):
        self.db_params = db_params
        self.label = label
        self.user_id = message.from_user.id
        self.text = text

    async def save_from_users(self):
        with psycopg2.connect(**self.db_params) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS MESSAGES (
                        user_id BIGINT,
                        text TEXT,
                        label INTEGER)
                """)
            with conn.cursor() as cur:
                cur.execute("INSERT INTO MESSAGES VALUES (%s, %s, %s)",
                             (self.user_id,
                              self.text,
                              int(self.label)))
            conn.commit()

class DatabaseUrl:
    def __init__(self, db_params, url_list):
        self.db_params = db_params
        self.url_list = url_list

    def create_url_table(self):
        conn = psycopg2.connect(**self.db_params)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS URLS (
                url TEXT,
                label INTEGER
            )
        """)
        conn.commit()
        conn.close()

    async def url_exists(self, url):
        conn = psycopg2.connect(**self.db_params)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM URLS WHERE url = %s", (url,))
        result = cur.fetchone()
        conn.close()
        return result[0] > 0

    async def insert_url(self, url):
        if await self.url_exists(url):
            return  # Skip insertion if URL already exists
        conn = psycopg2.connect(**self.db_params)
        cur = conn.cursor()
        cur.execute("INSERT INTO URLS (url, label) VALUES (%s, %s)", (url, None))
        conn.commit()
        conn.close()

    async def insert_urls(self):
        self.create_url_table()
        tasks = [self.insert_url(url) for url in self.url_list]
        await asyncio.gather(*tasks)


