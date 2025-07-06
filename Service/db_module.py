import time, os
from contextlib import contextmanager
from functools import wraps
import mysql.connector
from mysql.connector import Error

from log_module import setup_logger

global LOGGER
LOGGER = setup_logger("database", "logs/database")

def get_config():
    import configparser
    configs = configparser.ConfigParser()
    configs.read("myConfig.ini", encoding="utf-8")
    return configs

@contextmanager
def get_db_connection():
    config = get_config()
    DB_CONFIG = {
        "user": config["DATABASE"]["DB_USER"],
        "password": config["DATABASE"]["DB_PASSWORD"],
        "host": config["DATABASE"]["DB_HOST"],
        "database": config["DATABASE"]["DB_NAME"],
        "charset": "utf8mb4",
        "collation": "utf8mb4_general_ci",
    }
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        yield conn
    except Error as e:
        LOGGER.error(f"Database connection error: {e}")
        raise
    finally:
        if conn:
            try:
                if conn.is_connected():
                    conn.close()
            except Exception as e:
                LOGGER.error(f"Error closing mysql database connection: {e}")


def db_operation(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                result = func(cursor, *args, **kwargs)
                conn.commit()
                return result
        except Error as e:
            LOGGER.error(f"Database operation error: {e}")
            raise e

    return wrapper


def exec_sql(cursor, sql, params=None):
    """Execute & Log SQL query and its parameters."""
    start_time = time.time()
    if params:
        LOGGER.debug(f"Executing SQL: {sql} with params: {params}")
    else:
        LOGGER.debug(f"Executing SQL: {sql}")
    result = cursor.execute(sql, params or ())
    LOGGER.debug(f"Execution time: {time.time() - start_time}")
    return result


@db_operation
def create_user_table(cursor):
    """Create the users table if it doesn't exist."""
    sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(255) NOT NULL,
        auth_provider VARCHAR(50) NOT NULL,
        access_token TEXT,
        refresh_token TEXT,
        token_expiry DATETIME,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY (email, auth_provider)
    )
    """
    exec_sql(cursor, sql)
    LOGGER.info("Users table created or already exists.")


@db_operation
def get_or_create_user(cursor, email, auth_provider, access_token, refresh_token, expires_in):
    """
    Get a user by email and auth_provider, or create a new one.
    Updates tokens on every call.
    """
    from datetime import datetime, timedelta

    token_expiry = datetime.utcnow() + timedelta(seconds=int(expires_in))

    # Check if user exists
    sql_select = "SELECT * FROM users WHERE email = %s AND auth_provider = %s"
    exec_sql(cursor, sql_select, (email, auth_provider))
    user = cursor.fetchone()

    if user:
        # Update existing user's tokens
        sql_update = """
        UPDATE users SET access_token = %s, refresh_token = %s, token_expiry = %s
        WHERE id = %s
        """
        exec_sql(cursor, sql_update, (access_token, refresh_token, token_expiry, user['id']))
        user['access_token'] = access_token
        user['refresh_token'] = refresh_token
        user['token_expiry'] = token_expiry
        return user
    else:
        # Create new user
        sql_insert = """
        INSERT INTO users (email, auth_provider, access_token, refresh_token, token_expiry)
        VALUES (%s, %s, %s, %s, %s)
        """
        exec_sql(cursor, sql_insert, (email, auth_provider, access_token, refresh_token, token_expiry))
        user_id = cursor.lastrowid
        return {
            "id": user_id,
            "email": email,
            "auth_provider": auth_provider,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_expiry": token_expiry
        }

@db_operation
def get_user_by_id(cursor, user_id):
    """Get a user by their ID."""
    sql = "SELECT * FROM users WHERE id = %s"
    exec_sql(cursor, sql, (user_id,))
    return cursor.fetchone()
