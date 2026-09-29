import os
from contextlib import contextmanager

import pymysql
from dotenv import load_dotenv

load_dotenv()


def get_db_config():
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
        "cursorclass": pymysql.cursors.DictCursor,
    }


@contextmanager
def get_connection():
    """Opens a connection, commits if everything worked, rolls back if something failed."""
    conn = pymysql.connect(**get_db_config())
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()